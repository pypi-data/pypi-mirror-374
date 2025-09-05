from collections import defaultdict
from .fnmatch import fnmatch
from typing import List, Type
from .config_manager import ConfigManager
from .backup_object_id import BackupObjectId
from .backup_object import BackupObject
from .remote_storage import RemoteManager
from .backup_object_type import BackupObjectType
from .bash_cmd import EmptyCmd
from .backup_stage import BackupStage


class Discovery:
    def __init__(
        self,
        config_manager: ConfigManager,
        remote_manager: RemoteManager,
        select: str = "*",
        systems: List[Type[BackupObject]] = [],
    ):
        self.config_manager = config_manager
        self.remote_manager = remote_manager
        self.systems = systems
        self.select = select

    def discover_object_ids(self, cls: Type[BackupObject]) -> List[BackupObjectId]:
        """Level-based discovery: iterate over levels to build all object ids using discover_command_for_ids only."""
        object_ids = []
        for subtype in cls.available_subtypes():
            # Level 1
            level1_cmd = cls.discovery_command_for_objects(subtype, self.config_manager)
            level1s = [
                line.strip() for line in level1_cmd.run().splitlines() if line.strip()
            ]
            if not level1s:
                print(f"No objects found for at level 1 for subtype: {subtype.name}")
            for level1 in level1s:
                # Level 2
                level2_cmd = cls.discovery_command_for_objects(
                    subtype, self.config_manager, level1=level1
                )
                level2s = [
                    line.strip()
                    for line in level2_cmd.run().splitlines()
                    if line.strip()
                ]
                if not level2s:
                    print(
                        f"No objects found for at level 2 for subtype: {subtype.name}, level1: {level1}"
                    )
                for level2 in level2s:
                    # Level 3
                    level3_cmd = cls.discovery_command_for_objects(
                        subtype, self.config_manager, level1=level1, level2=level2
                    )
                    level3s = [
                        line.strip()
                        for line in level3_cmd.run().splitlines()
                        if line.strip()
                    ]
                    object_ids.extend(
                        BackupObjectId(
                            BackupObjectType.from_cls(cls),
                            subtype,
                            level1,
                            level2,
                            level3,
                        )
                        for level3 in level3s
                    )
        return object_ids

    def discover_local_backups(self, cls: Type[BackupObject]) -> List[str]:
        """Discover local backups for a given object_id."""
        bash_cmd = cls.discovery_command_for_local_backups(self.config_manager)
        if isinstance(bash_cmd, EmptyCmd):
            return self.discover_remote_backups()
        output = bash_cmd.run()
        return output.splitlines()

    def discover_remote_backups(self) -> List[str]:
        self.remote_manager.warm(self.config_manager)
        res = []
        for storage in self.remote_manager.storages.values():
            output = storage.get_list_backups_command().run()
            res.extend(output.splitlines())
        return res

    def discover_objects(self) -> List[BackupObject]:
        """Discover objects, filter by select, and set stage to BACKUP_BASE for those with actual local backups."""
        objects = []
        local_backups = []
        for cls in self.systems:
            local_backups.extend(self.discover_local_backups(cls))
            object_ids = [
                id
                for id in self.discover_object_ids(cls)
                if fnmatch(id.url, self.select)
            ]            
            for id in object_ids:
                object = cls(id, self.config_manager, self.remote_manager)
                objects.append(object)
        remote_backups = (
            self.discover_remote_backups()
        )  # Made after object creation to have them all
        for object in objects:
            if object.disabled:
                object.current_stage = BackupStage.DISABLED
            elif (
                object.base_backup_name in remote_backups
                and object.incremental_backup_name in remote_backups
            ):
                object.current_stage = BackupStage.SYNCED_INCREMENTAL
            elif object.base_backup_name in remote_backups:
                object.current_stage = BackupStage.SYNCED_BASE
            elif (
                object.base_backup_name in local_backups
                and object.incremental_backup_name in local_backups
            ):
                object.current_stage = BackupStage.BACKUP_INCREMENTAL
            elif object.base_backup_name in local_backups:
                object.current_stage = BackupStage.BACKUP_BASE
            else:
                object.current_stage = BackupStage.EXISTS        
        return sorted(objects)

    def discover_objects_back(self) -> List[BackupObject]:
        local_backups = []
        for cls in self.systems:
            local_backups.extend(self.discover_local_backups(cls))
        remote_backups = self.discover_remote_backups()
        # backup name has a form clickhouse/view/__nocluster__/maxi/test_screen_view/20250601_020000/base.zip
        # first five elements is url of object_id, 6th is datetime, 7th is backup type (base or datetime of incremental backup)
        # create a dict with object_id as key and a list of backups as value
        backup_dict = defaultdict(lambda: defaultdict(list))
        for type, backup_list in {"local": local_backups, "remote": remote_backups}.items():
            for backup in backup_list:
                backup_object_id = BackupObjectId.from_backup_name(backup)
                if fnmatch(backup_object_id.url, self.select):
                    backup_dict[backup_object_id][type].append(backup)
        objects = []
        for object_id, backups in backup_dict.items():
            object = cls(object_id, self.config_manager, self.remote_manager)
            objects.append(object)
            if object.disabled:
                continue
            if (
                object.base_backup_name in backups["local"]
                and object.incremental_backup_name in backups["local"]
            ):
                object.current_stage = BackupStage.SYNCED_INCREMENTAL
            elif (
                object.base_backup_name in backups["local"]
                and object.incremental_backup_name in backups["remote"]
            ):
                object.current_stage = BackupStage.SYNCED_BASE
            elif (
                object.base_backup_name in backups["remote"]
                and object.incremental_backup_name in backups["remote"]
            ):
                object.current_stage = BackupStage.EXISTS
            else:
                raise ValueError(
                    print(remote_backups),
                    f"Backup {object.base_backup_name} or {object.incremental_backup_name} not found in local or remote backups.",
                )
        return sorted(objects)
