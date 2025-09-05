"""Storage management for remote backups."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any
import hashlib
import json
from .bash_cmd import BashCmd
from .config_manager import ConfigManager
from collections import namedtuple

# Define a named tuple for ClickHouse parameters
ClickhouseParams = namedtuple('ClickhouseParams', ['type', 'base_path', 'args', 'settings'])


class RemoteStorage(ABC):
    """Abstract base class for remote storage providers."""

    @abstractmethod
    def __init__(self, config: Dict[str, Any]):
        """Initialize remote storage with configuration."""
        pass

    @abstractmethod
    def get_upload_file_command(self, local_path: Path, remote_path: str) -> BashCmd:
        """Upload a file to remote storage."""
        pass
    
    @abstractmethod
    def get_download_file_command(self, remote_path: str, local_path: Path) -> BashCmd:
        """Download a file from remote storage."""
        pass
    
    @property
    @abstractmethod    
    def clickhouse_params(self) -> ClickhouseParams:
      pass

    @abstractmethod
    def get_list_backups_command(self) -> BashCmd:
        """List files in remote storage."""
        pass

    @abstractmethod
    def get_upload_stdout_command(self, export_cmd: str, remote_path: str) -> BashCmd:
        """Upload data from a shell command's stdout to remote storage."""
        pass


class RemoteManager:
    """Manages remote storage singletons."""

    def __init__(self):
        self.storages: Dict[str, RemoteStorage] = {}

    def get_remote(self, config: Dict[str, Any]) -> RemoteStorage:
        from .remote_storages.filesystem import FilesystemStorage
        from .remote_storages.s3 import S3Storage
        """Get or create a remote storage instance based on config."""
        # Create a hash of the config to use as a key
        config_str = json.dumps(config, sort_keys=True)
        config_hash = hashlib.sha256(config_str.encode()).hexdigest()
        if config_hash not in self.storages:
            storage_type = config["type"]
            if storage_type == "filesystem":
                self.storages[config_hash] = FilesystemStorage(config)
            elif storage_type == "s3":
                self.storages[config_hash] = S3Storage(config)            
            else:
                raise ValueError(f"Unsupported remote storage type: {storage_type}")
        return self.storages[config_hash]

    def warm(self, config_manager: ConfigManager):
        for section in config_manager.config_sections:            
            remote = next(iter(section.values())).get("remote")
            if remote:
                self.get_remote(remote)
