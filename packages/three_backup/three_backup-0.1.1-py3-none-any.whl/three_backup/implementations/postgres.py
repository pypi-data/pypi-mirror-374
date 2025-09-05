from pathlib import Path
from ..backup_object import BackupObject
from ..backup_object_id import BackupObjectId
from ..backup_object_type import BackupObjectType, BackupObjectSubType
from ..bash_cmd import BashCmd
from ..config_manager import ConfigManager
from ..remote_storage import RemoteManager
from abc import abstractmethod


class PostgresBackupObject(BackupObject):
    """PostgreSQL backup object implementation."""

    def __init__(
        self,
        object_id: BackupObjectId,
        config_manager: ConfigManager,
        remote_manager: RemoteManager,
    ):
        super().__init__(object_id, config_manager, remote_manager)
        self.host = self.config["credentials"]["pg_host"]
        self.port = self.config["credentials"]["pg_port"]
        self.username = self.config["credentials"]["pg_user"]
        self.password = self.config["credentials"]["pg_password"]
        self.local_backup_directory = Path(
            self.config["credentials"]["pg_local_backup_directory"]
        )
        self.base_backup_path = self.local_backup_directory / f"{self.base_backup_name}"
        self.incremental_backup_path = (
            self.local_backup_directory / f"{self.incremental_backup_name}"
        )

    @classmethod
    def available_subtypes(cls):
        return [BackupObjectSubType.TABLE, BackupObjectSubType.VIEW]

    @property
    def backup_extension(self) -> str:
        """Return the file extension for PostgreSQL backups."""
        return "dump"

    @classmethod
    def discovery_command_for_objects(
        cls, subtype, config_manager, level1=None, level2=None, level3=None
    ):
        host = config_manager.credentials["pg_host"]
        port = config_manager.credentials["pg_port"]
        username = config_manager.credentials["pg_user"]
        password = config_manager.credentials["pg_password"]
        env_vars = {}
        if password:
            env_vars["PGPASSWORD"] = password
        # If not all levels are provided, return possible values for the next level
        if not level1 and not level2 and not level3:
            # List all databases (level1)
            cmd = f"psql -h {host} -p {port} -U {username} -t -A -c 'SELECT datname FROM pg_database WHERE datistemplate = false'"
            return BashCmd(cmd=cmd, env=env_vars)
        elif level1 and not level2 and not level3:
            # List all schemas in db (level2)
            cmd = f"psql -h {host} -p {port} -U {username} -d {level1} -t -A -c \"SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT LIKE 'pg_%' AND schema_name != 'information_schema'\""
            return BashCmd(cmd=cmd, env=env_vars)
        elif level1 and level2 and not level3:
            # List all tables/views in db.schema (level3)
            if subtype == BackupObjectSubType.TABLE:
                cmd = f"psql -h {host} -p {port} -U {username} -d {level1} -t -A -F',' -c \"SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = '{level2}'\""
            else:
                cmd = f"psql -h {host} -p {port} -U {username} -d {level1} -t -A -F',' -c \"SELECT viewname FROM pg_catalog.pg_views WHERE schemaname = '{level2}'\""
            return BashCmd(cmd=cmd, env=env_vars)
        elif level1 and level2 and level3:
            # Just echo the table/view name (return as BackupObjectId)
            cmd = f"echo {level3}"
            return BashCmd(cmd=cmd, env=env_vars)
        else:
            raise ValueError("Invalid level combination for Postgres")

    def get_backup_command(self, is_base: bool) -> BashCmd:
        """Create a backup using pg_dump."""
        if not is_base:
            raise ValueError("Incremental backups are not supported for Postgres.")        
        env_vars = {}
        if self.password:
            env_vars["PGPASSWORD"] = self.password      
        # Добавляем расширение .dump для custom format
        backup_file = self.base_backup_path.with_suffix('.dump')
        mkdir_cmd = f"mkdir -p '{backup_file.parent}'"        
        pg_dump_cmd = [
            "pg_dump",
            "-h", self.host,
            "-p", str(self.port),
            "-U", self.username,
            "-d", self.level1,
            "-n", self.level2,
            "-t", f"{self.level2}.{self.level3}",
            "-F", "c",  # Custom format
            "--create",
            "--clean",
            "-f", str(backup_file)
        ]
        
        cmd = f"{mkdir_cmd} && {' '.join(pg_dump_cmd)}"
        return BashCmd(cmd=cmd, env=env_vars)



    @classmethod
    def discovery_command_for_local_backups(cls, config_manager):
        path = Path(config_manager.credentials["pg_local_backup_directory"])
        cmd = f"mkdir -p '{path}' && cd '{path}' && find . -type f -name '*.dump' -printf '%P\\n'"
        return BashCmd(cmd=cmd)

    def get_restore_command(self) -> BashCmd:
        """Restore a backup using psql."""
        env_vars = {}
        if self.password:
            env_vars["PGPASSWORD"] = self.password
        # The restore target database is self.level1
        # The backup file is self.base_backup_path
        cmd = (
            f"gunzip -c '{self.base_backup_path}' | "
            f"psql -h {self.host} -p {self.port} -U {self.username} -d {self.level1}"
        )
        return BashCmd(cmd=cmd, env=env_vars)

    def get_check_command(self) -> BashCmd:
        """Return a BashCmd to check if the table or view exists in the database."""
        env_vars = {}
        if self.password:
            env_vars["PGPASSWORD"] = self.password
        # Check for table or view existence in the specified schema and database
        if self.object_id.subtype == BackupObjectSubType.TABLE:
            sql = (
                f"SELECT 1 FROM pg_catalog.pg_tables "
                f"WHERE schemaname = '{self.level2}' AND tablename = '{self.level3}';"
            )
        else:
            sql = (
                f"SELECT 1 FROM pg_catalog.pg_views "
                f"WHERE schemaname = '{self.level2}' AND viewname = '{self.level3}';"
            )
        cmd = (
            f"psql -h {self.host} -p {self.port} -U {self.username} -d {self.level1} "
            f'-t -A -c "{sql}"'
        )
        return BashCmd(cmd=cmd, env=env_vars)

    def get_delete_command(self) -> BashCmd:
        """Return a BashCmd to delete a table or view from the database."""
        env_vars = {}
        if self.password:
            env_vars["PGPASSWORD"] = self.password
        if self.object_id.subtype == BackupObjectSubType.TABLE:
            sql = f'DROP TABLE IF EXISTS "{self.level2}"."{self.level3}" CASCADE;'
        else:
            sql = f'DROP VIEW IF EXISTS "{self.level2}"."{self.level3}" CASCADE;'
        cmd = (
            f"psql -h {self.host} -p {self.port} -U {self.username} -d {self.level1} "
            f'-c "{sql}"'
        )
        return BashCmd(cmd=cmd, env=env_vars)

    def get_upload_command(self, is_base: bool) -> BashCmd:
        return self.remote.get_upload_file_command(
            self.base_backup_path if is_base else self.incremental_backup_path,
            f"{self.type.value}/{self.base_backup_name}",
        )

    def get_download_command(self, is_base: bool) -> BashCmd:
        return self.remote.get_download_file_command(
            f"{self.type.value}/{self.base_backup_name}",
            self.base_backup_path if is_base else self.incremental_backup_path,
        )

    def rotate_local_backups(self) -> bool:
        pass
