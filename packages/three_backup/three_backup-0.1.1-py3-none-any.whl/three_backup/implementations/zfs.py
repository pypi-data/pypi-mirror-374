from typing import override
from three_backup.backup_object import BackupObject
from three_backup.backup_object_id import BackupObjectId
from three_backup.backup_object_type import BackupObjectSubType
from three_backup.bash_cmd import BashCmd, EmptyCmd
from three_backup.config_manager import ConfigManager
from three_backup.remote_storage import RemoteManager


class ZFSBackupObject(BackupObject):
    """ZFS backup object implementation for LXD datasets using ZFS snapshots and streaming."""

    def __init__(
        self,
        object_id: BackupObjectId,
        config_manager: ConfigManager,
        remote_manager: RemoteManager,
    ):
        super().__init__(object_id, config_manager, remote_manager)
        self.base_zfs_snapshot_name = self.name_to_zfs_snapshot_name(self.base_backup_name)
        self.incremental_zfs_snapshot_name = self.name_to_zfs_snapshot_name(self.incremental_backup_name)

    @override
    def name_to_zfs_snapshot_name(self, backup_name: str) -> str:
        elements = backup_name.split('/')
        return f"{"/".join(elements[2:-2])}@threebackup_{elements[-2]}_{elements[-1]}"
        

    @classmethod
    def available_subtypes(cls):
        return [BackupObjectSubType.DATASET]

    @property
    def backup_extension(self) -> str:
        return "zfs"

    @classmethod
    def discovery_command_for_objects(cls, subtype, config_manager, level1=None, level2=None):
        if subtype != BackupObjectSubType.DATASET:
            raise ValueError(f"Unsupported subtype: {subtype}")

        if not level1 and not level2:
            # Level 0: List all pools that have exactly 3-segment datasets
            cmd = "zfs list -H -o name | grep -E '^[^/]+/[^/]+/[^/]+$' | cut -d/ -f1 | sort -u || true"
            return BashCmd(cmd=cmd)
        
        elif level1 and not level2:
            # Level 1: List all second-level components under the pool that have 3-segment datasets
            cmd = f"zfs list -H -o name | grep -E '^{level1}/[^/]+/[^/]+$' | cut -d/ -f2 | sort -u || true"
            return BashCmd(cmd=cmd)
        
        elif level1 and level2:
            # Level 2: List leaf datasets under pool/level2 (exactly 3 segments)
            cmd = f"zfs list -H -o name | grep -E '^{level1}/{level2}/[^/]+$' | cut -d/ -f3 || true"
            return BashCmd(cmd=cmd)
        
        else:
            raise ValueError("Invalid level combination for ZFS discovery")

    @classmethod
    def discovery_command_for_local_backups(cls, config_manager):
        # List ZFS snapshots with our naming pattern from 3-segment datasets
        cmd = "zfs list -t snapshot -H -o name | grep -E '^[^/]+/[^/]+/[^/]+@threebackup_' | sed 's/@threebackup_/\\//;s/_base/\\/base/;s/_incremental/\\/incremental/;s/^/zfs\\/dataset\\//' || true"
        return BashCmd(cmd=cmd)

    def _get_dataset_path(self) -> str:
        """Get the full ZFS dataset path: level1/level2/level3"""
        return f"{self.level1}/{self.level2}/{self.level3}"

    def get_backup_command(self, is_base: bool) -> BashCmd:
        """Create ZFS snapshot locally (no files)."""        
        cmd = f"zfs snapshot {self.base_zfs_snapshot_name if is_base else self.incremental_zfs_snapshot_name}"
        return BashCmd(cmd=cmd)

    def get_restore_command(self, is_base: bool) -> BashCmd:
        """Local restore is a rollback to the corresponding snapshot."""        
        cmd = f"zfs rollback {self.base_zfs_snapshot_name if is_base else self.incremental_zfs_snapshot_name}"
        return BashCmd(cmd=cmd)

    def get_upload_command(self, is_base: bool) -> BashCmd:
        """Stream zfs send directly to remote via stdout."""        
        if is_base:            
            zsend = f"zfs send {self.base_zfs_snapshot_name}"
            return self.remote.get_upload_stdout_command(zsend, self.base_backup_name)
        else:
            zsend = f"zfs send -i {self.base_zfs_snapshot_name} {self.incremental_zfs_snapshot_name}"
            return self.remote.get_upload_stdout_command(zsend, self.incremental_backup_name)

    def get_download_command(self, is_base: bool) -> BashCmd:
        """Stream from remote directly into zfs receive."""
        dl = self.remote.get_download_stdout_command(self.base_backup_name if is_base else self.incremental_backup_name)
        cmd = f"{dl.cmd} | zfs receive -F {self.base_zfs_snapshot_name if is_base else self.incremental_zfs_snapshot_name}"
        return BashCmd(cmd=cmd)

    def get_check_command(self) -> BashCmd:
        """Always return true, as local backup means that dataset exists."""        
        return BashCmd("true")

    def get_delete_command(self) -> BashCmd:
        """Destroy dataset recursively."""
        dataset = self._get_dataset_path()
        return BashCmd(cmd=f"zfs destroy -r {dataset}")

    def rotate_local_backups(self) -> bool:
        """Rotate ZFS snapshots - keep only the N most recent."""
        return True
