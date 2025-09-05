from pathlib import Path
from three_backup.backup_object import BackupObject
from three_backup.backup_object_id import BackupObjectId
from three_backup.backup_object_type import BackupObjectSubType
from three_backup.bash_cmd import BashCmd
from three_backup.config_manager import ConfigManager
from three_backup.remote_storage import RemoteManager
from ..bash_cmd import EmptyCmd

class LXDBackupObject(BackupObject):
    """LXD config backup object implementation (machines, networks, volumes, profiles)."""

    def __init__(
        self,
        object_id: BackupObjectId,
        config_manager: ConfigManager,
        remote_manager: RemoteManager,
    ):
        super().__init__(object_id, config_manager, remote_manager)
        self.subtype = object_id.subtype        
        self.local_backup_directory = Path(config_manager.credentials["lxd_local_backup_directory"])
        self.base_backup_path = self.local_backup_directory / f"{self.base_backup_name}"
        self.incremental_backup_path = self.local_backup_directory / f"{self.incremental_backup_name}"

    @classmethod
    def available_subtypes(cls):
        return [
            BackupObjectSubType.CONTAINER,
            BackupObjectSubType.VOLUME,
            BackupObjectSubType.PROFILE,
            BackupObjectSubType.NETWORK,            
        ]

    @property
    def backup_extension(self) -> str:
        return "yaml"

    @classmethod
    def discovery_command_for_objects(cls, subtype, config_manager, level1=None, level2=None):
        # If not all levels are provided, return possible values for the next level
        if level2 and not level1:
            raise ValueError("Level 2 cannot be specified without Level 1 for LXD discovery.")
        if not level1 and not level2:
            # List all databases (level1)
            cmd = "echo default"
            return BashCmd(cmd=cmd)
        elif level1 and not level2:
            # List all projects
            cmd = "lxc project list --format csv | awk -F, '{print $1}' | sed 's/(current)//'"
            return BashCmd(cmd=cmd)
        elif subtype == BackupObjectSubType.CONTAINER:          
            cmd = f"lxc list -c n --format csv --project {level2}"
            return BashCmd(cmd=cmd)            
        elif subtype == BackupObjectSubType.VOLUME:            
            cmd = f"lxc storage volume list --project {level2} --format csv | awk -F, '$2==\"volume\"{{print $3}}'"
            return BashCmd(cmd=cmd)            
        elif subtype == BackupObjectSubType.PROFILE:
            cmd = f"lxc profile list --project {level2 or 'default'} --format csv | awk -F, '{{print $1}}'"
            return BashCmd(cmd=cmd)
        elif subtype == BackupObjectSubType.NETWORK:
            cmd = f"lxc network list --project {level2 or 'default'} --format csv | awk -F, '$3==\"YES\"{{print $1}}'"
            return BashCmd(cmd=cmd)
        else:
            raise ValueError(f"Unsupported subtype: {subtype}")

    @classmethod
    def discovery_command_for_local_backups(cls, config_manager):
        path = Path(config_manager.credentials["lxd_local_backup_directory"])
        cmd = f"mkdir -p '{path}' && cd '{path}' && find . -type f -name '*.yaml' -printf '%P\\n'"
        return BashCmd(cmd=cmd)


    def get_backup_command(self, is_base: bool) -> BashCmd:
        # Export config as YAML for each object type
        self.base_backup_path.parent.mkdir(parents=True, exist_ok=True)
        if is_base:
            if self.subtype == BackupObjectSubType.CONTAINER:
                cmd = f"lxc config show {self.level3} --project {self.level2} --expanded | grep -Fv 'volatile.' > '{self.base_backup_path}' || true"
            elif self.subtype == BackupObjectSubType.VOLUME:
                cmd = f"lxc storage volume show {self.level1} {self.level3} --project {self.level2} > '{self.base_backup_path}'"
            elif self.subtype == BackupObjectSubType.PROFILE:
                cmd = f"lxc profile show {self.level3} > '{self.base_backup_path}'"
            elif self.subtype == BackupObjectSubType.NETWORK:
                cmd = f"lxc network show {self.level3} > '{self.base_backup_path}'"            
            else:
                raise ValueError(f"Unsupported subtype: {self.subtype}")
        else:
            # Incremental: diff current config with base_backup_path and save the diff
            diff_path = self.local_backup_directory / f"{self.incremental_backup_name}"
            if self.subtype == BackupObjectSubType.CONTAINER:
                cmd = f"lxc config show {self.level3} --project {self.level2} --expanded | grep -Fv 'volatile.' | diff -u '{self.base_backup_path}' - > '{diff_path}' || true"
            elif self.subtype == BackupObjectSubType.VOLUME:
                cmd = f"lxc storage volume show {self.level1} {self.level3} --project {self.level2} | diff -u - '{self.base_backup_path}' > '{diff_path}'"
            elif self.subtype == BackupObjectSubType.PROFILE:
                cmd = f"lxc profile show {self.level3} | diff -u - '{self.base_backup_path}' > '{diff_path}'"
            elif self.subtype == BackupObjectSubType.NETWORK:
                cmd = f"lxc network show {self.level3} | diff -u - '{self.base_backup_path}' > '{diff_path}'"
            else:
                raise ValueError(f"Unsupported subtype: {self.subtype}")
        return BashCmd(cmd=cmd)
    
    def get_restore_command(self, is_base: bool) -> BashCmd:
      # Restore config from YAML for each object type      
      diff_path = self.local_backup_directory / f"{self.incremental_backup_name}"
      cat_cmd = f"cat {input_path}" if is_base else f"patch '{self.base_backup_path}' '{diff_path}' -o - | awk '/^config:/ {{ print; system(\"lxc config show --project {self.level2} {self.level3} | sed -n \\\"/^config:/,/^[^ ]/p\\\" | grep -F volatile.\"); next }}1'"
      cleanup_cmd = ""
      if self.subtype == BackupObjectSubType.CONTAINER:
        create_cmd = f"lxc network create three_backup || true && lxc init ubuntu --project {self.level2} {self.level3} --network three_backup"
        apply_cmd = f"lxc config edit {self.level3} --project {self.level2}"
        cleanup_cmd = "&& lxc network delete three_backup"
      elif self.subtype == BackupObjectSubType.VOLUME:
        create_cmd = f"lxc storage volume create {self.level1} {self.level3} --project {self.level2}"
        apply_cmd = f"lxc storage volume edit {self.level1} {self.level3} --project {self.level2}"
      elif self.subtype == BackupObjectSubType.PROFILE:
        create_cmd = f"lxc profile create {self.level3} --project {self.level2 or 'default'}" if self.level3 != 'default' else "true"
        apply_cmd = f"lxc profile edit {self.level3} --project {self.level2 or 'default'}"
      elif self.subtype == BackupObjectSubType.NETWORK:
        create_cmd = f"lxc network create {self.level3} --project {self.level2 or 'default'}"
        apply_cmd = f"lxc network edit {self.level3} --project {self.level2 or 'default'}"
      else:
        raise ValueError(f"Unsupported subtype: {self.subtype}")
      cmd = f"{create_cmd} && {cat_cmd} | {apply_cmd}{cleanup_cmd}"
      return BashCmd(cmd=cmd)

    def get_upload_command(self, is_base: bool) -> BashCmd:
        # Upload the YAML config file to remote
        return self.remote.get_upload_file_command(
            self.base_backup_path if is_base else  self.incremental_backup_path,
            self.base_backup_name if is_base else self.incremental_backup_name,
        )
    
    def get_download_command(self, is_base: bool) -> BashCmd:
        # Download the YAML config file from remote
        return self.remote.get_download_file_command(
            self.base_backup_name if is_base else self.incremental_backup_name,
            self.base_backup_path if is_base else self.incremental_backup_path,
        )

    def get_check_command(self) -> BashCmd:
        # Check if the object exists in LXD
        if self.subtype == BackupObjectSubType.CONTAINER:
            cmd = f"lxc list {self.level3} --project {self.level2} -c n --format csv | grep -Fx '{self.level3}' || true"
        elif self.subtype == BackupObjectSubType.VOLUME:
            cmd = f"lxc storage volume list {self.level1} --project {self.level2} --format csv | awk -F, '$3==\"{self.level3}\"' | grep -Fx '{self.level3}' || true"
        elif self.subtype == BackupObjectSubType.PROFILE:
            cmd = f"lxc profile list --project {self.level2 or 'default'} --format csv | awk -F, '{{print $1}}' | grep -Fx '{self.level3}' || true"
        elif self.subtype == BackupObjectSubType.NETWORK:
            cmd = f"lxc network list --project {self.level2 or 'default'} --format csv | awk -F, '{{print $1}}' | grep -Fx '{self.level3}' || true"
        else:
            raise ValueError(f"Unsupported subtype: {self.subtype}")
        return BashCmd(cmd=cmd)

    def get_delete_command(self) -> BashCmd:
        # Delete the object from LXD
        if self.subtype == BackupObjectSubType.CONTAINER:
            cmd = f"lxc delete {self.level3} --project {self.level2} --force"
        elif self.subtype == BackupObjectSubType.VOLUME:
            cmd = f"lxc storage volume delete {self.level1} {self.level3} --project {self.level2}"
        elif self.subtype == BackupObjectSubType.PROFILE:
            # Don't delete default profile
            if self.level3 == 'default':
                return EmptyCmd()
            else:
                cmd = f"lxc profile delete {self.level3} --project {self.level2 or 'default'}"
        elif self.subtype == BackupObjectSubType.NETWORK:
            cmd = f"lxc network delete {self.level3} --project {self.level2 or 'default'}"
        else:
            raise ValueError(f"Unsupported subtype: {self.subtype}")
        return BashCmd(cmd=cmd)

    def rotate_local_backups(self) -> bool:
        # Not implemented
        return True