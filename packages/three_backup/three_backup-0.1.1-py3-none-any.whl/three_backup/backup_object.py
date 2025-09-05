from abc import ABC, abstractmethod
from typing import List
from datetime import datetime
from croniter import croniter
from .config_manager import ConfigManager
from .remote_storage import RemoteManager
from .backup_stage import BackupStage
from .backup_object_id import BackupObjectId
from .backup_object_type import BackupObjectSubType
from .bash_cmd import BashCmd


class BackupObject(ABC):
    """Base class for all backup objects."""

    def __init__(
        self,
        object_id: BackupObjectId,
        config_manager: ConfigManager,
        remote_manager: RemoteManager,
    ):
        self.type = object_id.type
        self.subtype = object_id.subtype
        self.level1 = object_id.level1
        self.level2 = object_id.level2
        self.level3 = object_id.level3
        self.url = object_id.url
        self.object_id = object_id
        self.config = config_manager.get_config_for_object(object_id)
        self.current_stage = (
            BackupStage.DISABLED if self.config["disabled"] else BackupStage.EXISTS
        )
        self.remote = remote_manager.get_remote(self.config["remote"])
        self.base_schedule = self.config["base_schedule"]
        self.incremental_schedule = self.config["incremental_schedule"]
        self.now = self.config["now"]
        self.base_backup_name = self.get_backup_name(is_base=True)
        self.incremental_backup_name = self.get_backup_name(is_base=False)
        self.max_stage = BackupStage[self.config["max_stage"]]
    
    def __lt__(self, other: "BackupObject") -> bool:
        if not isinstance(other, BackupObject):
            return NotImplemented
        return self.object_id < other.object_id

    def get_backup_name(self, is_base: bool) -> str:
        """Get the path where the backup should be stored.
        The path is based on object_id structure and the last scheduled time."""
        base_schedule = self.config["base_schedule"]
        now = self.config["now"]
        base_cron = croniter(base_schedule, now)
        base_timestamp = base_cron.get_prev(datetime).strftime("%Y%m%d_%H%M%S")
        if not is_base:
            incremental_cron = croniter(self.config["incremental_schedule"], now)
            incremental_timestamp = incremental_cron.get_prev(datetime).strftime(
                "%Y%m%d_%H%M%S"
            )
        if is_base or base_timestamp == incremental_timestamp:
            timestamp = base_timestamp
            backup_name = "base"
        elif base_timestamp < incremental_timestamp:
            timestamp = incremental_timestamp
            backup_name = f"incremental_{timestamp}"
        else:
            raise ValueError(
                "Base timestamp cannot be after incremental timestamp: "
                f"{base_timestamp} > {incremental_timestamp}"
            )

        return f"{self.url}/{base_timestamp}/{backup_name}.{self.backup_extension}"

    def advance_to_stage(self, target_stage: BackupStage) -> None:
        print(self.incremental_backup_name)        
        print(self.base_backup_name)
        if self.current_stage.value >= target_stage.value:
            print(f"Already at or beyond target stage ({self.current_stage}): {target_stage}")
            return
        if target_stage == BackupStage.BACKUP_BASE:
            self.create_backup(True)
        elif target_stage == BackupStage.SYNCED_BASE:
            self.advance_to_stage(BackupStage.BACKUP_BASE)
            self.sync_to_remote(True)
        elif target_stage == BackupStage.BACKUP_INCREMENTAL:
            self.advance_to_stage(BackupStage.SYNCED_BASE)
            if self.incremental_backup_name != self.base_backup_name:                
                self.create_backup(False)
        elif target_stage == BackupStage.SYNCED_INCREMENTAL:
            self.advance_to_stage(BackupStage.BACKUP_INCREMENTAL)
            if self.incremental_backup_name != self.base_backup_name:
                self.sync_to_remote(False)
        elif target_stage == BackupStage.ROTATED_LOCALLY:
            self.advance_to_stage(BackupStage.SYNCED_INCREMENTAL)
            self.rotate_local_backups()
        elif target_stage == BackupStage.ROTATED_REMOTE:
            self.advance_to_stage(BackupStage.ROTATED_LOCALLY)
            self.rotate_remote_backups()
        else:
            raise ValueError(f"Unsupported target stage: {target_stage}")
        self.current_stage = target_stage

    def advance_to_stage_back(self, target_stage: BackupStage, onexists: str) -> None:        
        if self.current_stage.value >= target_stage.value:
            print(f"Already at or beyond target stage ({self.current_stage}): {target_stage}")
            return
        if target_stage == BackupStage.SYNCED_BASE:
            self.sync_from_remote(True)
        elif target_stage == BackupStage.SYNCED_INCREMENTAL:
            self.advance_to_stage_back(BackupStage.SYNCED_BASE, onexists)
            self.sync_from_remote(False)
        elif target_stage == BackupStage.RESTORED:
            self.advance_to_stage_back(BackupStage.SYNCED_INCREMENTAL, onexists)
            self.restore_backup(onexists)

        self.current_stage = target_stage

    @property
    def disabled(self) -> bool:
        """Check if the object is disabled."""
        return self.current_stage == BackupStage.DISABLED

    @property
    @abstractmethod
    def backup_extension(self) -> str:
        pass

    def create_backup(self, is_base: bool) -> None:
        """Create a backup of the object using a BashCmd."""
        print(f"Creating {'base' if is_base else 'incremental'} backup for {self.url}...")
        self.get_backup_command(is_base).run()

    def sync_to_remote(self, is_base: bool) -> None:
        """Sync backups to remote storage."""
        print(f"Syncing backups for {self.url} to remote storage...")
        self.get_upload_command(is_base).run()

    def sync_from_remote(self, is_base: bool) -> None:
        """Sync backups from remote storage."""
        print(f"Syncing backups for {self.url} from remote storage...")
        self.get_download_command(is_base).run()

    def restore_backup(self, onexists: str) -> None:
        """Restore a backup of the object using a BashCmd."""
        print(f"Restoring backup for {self.url}...")
        is_base = self.base_backup_name == self.incremental_backup_name
        result = self.get_check_command().run()        
        if any(line.strip() for line in result):
            if onexists == "skip":
                print(f"Backup object already exists for {self.url}, skipping restore.")
                return
            elif onexists == "overwrite":
                print(f"Overwriting existing backup for {self.url}.")
                self.get_delete_command().run()
            elif onexists == "ask":
                response = input(f"Backup object already exists for {self.url}. Overwrite? (y/n): ").strip().lower()
                if response == 'y':
                    print(f"Overwriting existing backup object for {self.url}.")
                    self.get_delete_command().run()
                else:
                    print(f"Skipping restore for {self.url}.")
                    return
            else:
                raise ValueError(f"Unsupported onexists option: {onexists}")
        self.get_restore_command(is_base).run()

    @abstractmethod
    def rotate_local_backups(self) -> bool:
        """Remove old local backups according to config."""
        pass

    def rotate_remote_backups(self) -> bool:
        """Remove old remote backups according to config."""
        pass

    @classmethod
    @abstractmethod
    def available_subtypes(cls) -> List["BackupObjectSubType"]:
        """Return list of supported subtypes for this backup object."""
        pass

    @classmethod
    @abstractmethod
    def discovery_command_for_local_backups(cls, config_manager) -> "BashCmd":
        """Return a BashCmd to detect local backups."""
        pass

    @classmethod
    @abstractmethod
    def discovery_command_for_objects(
        cls, subtype: "BackupObjectSubType", config_manager, level1=None, level2=None
    ) -> "BashCmd":
        """Return a BashCmd to detect objects of this subtype at a specific level, or to list possible values for the next level if not all levels are provided."""
        pass

    @abstractmethod
    def get_backup_command(self, is_base: bool) -> BashCmd:
        """Return a BashCmd to create a base backup."""
        pass

    @abstractmethod
    def get_restore_command(self, is_base: bool) -> BashCmd:
        """Return a BashCmd to restore a backup."""
        pass

    @abstractmethod
    def get_upload_command(self, is_base: bool) -> BashCmd:
        """Return a BashCmd to sync backups to remote storage."""
        pass
    
    @abstractmethod
    def get_download_command(self, is_base: bool) -> BashCmd:
        """Return a BashCmd to sync backups from remote storage."""
        pass

    @abstractmethod
    def get_check_command(self, is_base: bool) -> BashCmd:
        """Return a BashCmd to check if object exists."""
        pass
    
    @abstractmethod
    def get_delete_command(self, is_base: bool) -> BashCmd:
        """Return a BashCmd to delete an object."""
        pass