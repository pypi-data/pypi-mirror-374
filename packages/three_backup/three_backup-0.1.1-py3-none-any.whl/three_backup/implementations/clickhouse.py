from pathlib import Path
from ..backup_object import BackupObject
from ..backup_object_id import BackupObjectId
from ..backup_object_type import BackupObjectSubType
from ..bash_cmd import BashCmd, EmptyCmd
from ..config_manager import ConfigManager
from ..remote_storage import RemoteManager


class ClickHouseBackupObject(BackupObject):
    """ClickHouse backup object implementation."""

    def __init__(
        self,
        object_id: BackupObjectId,
        config_manager: ConfigManager,
        remote_manager: RemoteManager,
    ):
        super().__init__(object_id, config_manager, remote_manager)
        self.subtype = object_id.subtype
        self.local_backup_directory = Path(
            config_manager.credentials.get("clickhouse_local_backup_directory", ".")
        )
        self.base_backup_path = self.local_backup_directory / f"{self.base_backup_name}"

    @classmethod
    def available_subtypes(cls):
        return [BackupObjectSubType.TABLE, BackupObjectSubType.VIEW]

    @property
    def backup_extension(self) -> str:
        return "zip"

    @classmethod
    def discovery_command_for_objects(
        cls, subtype, config_manager, level1=None, level2=None
    ):
        host = config_manager.credentials["ch_host"]
        port = config_manager.credentials["ch_port"]
        user = config_manager.credentials["ch_user"]
        password = config_manager.credentials["ch_password"]
        auth = f"--user {user} --password {password}" if password else f"--user {user}"
        if not level1 and not level2:
            # List clusters (if any), else return 'default' if empty (Bash logic)
            return BashCmd(cmd="echo __nocluster__")
        elif level1 and not level2:
            cmd = f'clickhouse-client {auth} --host {host} --port {port} --query="SHOW DATABASES"'
            return BashCmd(cmd=cmd)
        elif level1 and level2:
            if subtype == BackupObjectSubType.TABLE:
                engine_filter = "NOT LIKE '%View'"
            elif subtype == BackupObjectSubType.VIEW:
                engine_filter = "LIKE '%View'"
            else:
                raise ValueError(f"Unsupported subtype: {subtype}")
            query = (
                f"SELECT name FROM system.tables "
                f"WHERE database = '{level2}' AND engine {engine_filter}"
            )
            cmd = f'clickhouse-client {auth} --host {host} --port {port} --query="{query}"'
            return BashCmd(cmd=cmd)
        else:
            raise ValueError("Invalid level combination for ClickHouse")

    @classmethod
    def discovery_command_for_local_backups(cls, config_manager):
        return EmptyCmd()

    def get_backup_command(self, is_base: bool) -> BashCmd:
        params = self.remote.clickhouse_params
        # Compose the backup object SQL part
        object_sql = f"{self.subtype.name.upper()} {self.level2}.{self.level3}"
        backup_name = (
            self.base_backup_name if is_base else self.incremental_backup_name
        )
        # Compose the destination
        dest_args = ", ".join(
            [repr(params.base_path + "/" + backup_name)] + list(params.args)
        )
        dest = f"{params.type}({dest_args})"

        # Compose settings
        settings = dict(params.settings) if params.settings else {}
        if not is_base:
            settings["base_backup"] = (
                f"{params.type}('{params.base_path}/{self.base_backup_name}')"
            )
        settings_sql = (
            "SETTINGS " + ", ".join(f"{k}={v}" for k, v in settings.items())
            if settings
            else ""
        )

        query = f"BACKUP {object_sql} TO {dest} {settings_sql}".strip()

        # Compose clickhouse-client command
        host = self.config["credentials"]["ch_host"]
        port = self.config["credentials"]["ch_port"]
        user = self.config["credentials"]["ch_user"]
        password = self.config["credentials"]["ch_password"]
        auth = f"--user {user} --password {password}" if password else f"--user {user}"
        cmd = f'clickhouse-client {auth} --host {host} --port {port} --query="{query}"'
        return BashCmd(cmd=cmd)
    
    def get_restore_command(self, is_base: bool) -> BashCmd:
      params = self.remote.clickhouse_params
      object_sql = f"{self.subtype.name.upper()} {self.level2}.{self.level3}"
      backup_name = (
        self.base_backup_name if is_base else self.incremental_backup_name
      )
      src_args = ", ".join(
        [repr(params.base_path + "/" + backup_name)] + list(params.args)
      )
      src = f"{params.type}({src_args})"

      settings = dict(params.settings) if params.settings else {}
      if not is_base:
        settings["base_backup"] = (
          f"{params.type}('{params.base_path}/{self.base_backup_name}')"
        )
      settings_sql = (
        "SETTINGS " + ", ".join(f"{k}={v}" for k, v in settings.items())
        if settings
        else ""
      )

      query = f"RESTORE {object_sql} FROM {src} {settings_sql}".strip()

      host = self.config["credentials"]["ch_host"]
      port = self.config["credentials"]["ch_port"]
      user = self.config["credentials"]["ch_user"]
      password = self.config["credentials"]["ch_password"]
      auth = f"--user {user} --password {password}" if password else f"--user {user}"
      cmd = f'clickhouse-client {auth} --host {host} --port {port} --query="{query}"'
      return BashCmd(cmd=cmd)

    def get_upload_command(self, is_base: bool) -> BashCmd:
        return EmptyCmd()

    def get_download_command(self, is_base: bool) -> BashCmd:
        return EmptyCmd()    

    def rotate_local_backups(self) -> bool:
        pass

    def get_check_command(self) -> BashCmd:
        # Check if the table or view exists in ClickHouse
        host = self.config["credentials"]["ch_host"]
        port = self.config["credentials"]["ch_port"]
        user = self.config["credentials"]["ch_user"]
        password = self.config["credentials"]["ch_password"]
        auth = f"--user {user} --password {password}" if password else f"--user {user}"
        if self.subtype == BackupObjectSubType.TABLE:
            sql = (
                f"SELECT 1 FROM system.tables WHERE database = '{self.level2}' AND name = '{self.level3}';"
            )
        else:
            sql = (
                f"SELECT 1 FROM system.tables WHERE database = '{self.level2}' AND name = '{self.level3}' AND engine LIKE '%View';"
            )
        cmd = f"clickhouse-client {auth} --host {host} --port {port} --query=\"{sql}\""
        return BashCmd(cmd=cmd)

    def get_delete_command(self) -> BashCmd:
        # Drop the table or view in ClickHouse
        host = self.config["credentials"]["ch_host"]
        port = self.config["credentials"]["ch_port"]
        user = self.config["credentials"]["ch_user"]
        password = self.config["credentials"]["ch_password"]
        auth = f"--user {user} --password {password}" if password else f"--user {user}"
        if self.subtype == BackupObjectSubType.TABLE:
            sql = f"DROP TABLE IF EXISTS {self.level2}.{self.level3}"
        else:
            sql = f"DROP VIEW IF EXISTS {self.level2}.{self.level3}"
        cmd = f"clickhouse-client {auth} --host {host} --port {port} --query=\"{sql}\""
        return BashCmd(cmd=cmd)


