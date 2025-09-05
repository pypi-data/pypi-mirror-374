from pathlib import Path
from typing import Dict, Any
from ..bash_cmd import BashCmd
from ..remote_storage import RemoteStorage, ClickhouseParams


class FilesystemStorage(RemoteStorage):
    """Remote storage implementation that uses local filesystem."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize filesystem remote with configuration."""
        self.base_path = Path(config["base_path"]).resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)

    def get_upload_file_command(self, local_path: Path, remote_path: str) -> BashCmd:
        """Return a BashCmd to upload a file to remote storage."""
        # cp with creating all necessary folders in bash
        remote_path = self.base_path / remote_path
        mkdir_cmd = f"mkdir -p '{remote_path.parent}'"
        cp_cmd = f"cp '{local_path}' '{remote_path}'"
        return BashCmd(f"{mkdir_cmd} && {cp_cmd}")
    
    def get_download_file_command(self, remote_path: str, local_path: Path) -> BashCmd:
        """Return a BashCmd to download a file from remote storage."""
        remote_path = self.base_path / remote_path
        mkdir_cmd = f"mkdir -p '{local_path.parent}'"
        cp_cmd = f"cp '{remote_path}' '{local_path}'"
        return BashCmd(f"{mkdir_cmd} && {cp_cmd}")
    
    def get_list_backups_command(self) -> BashCmd:
        """Return a BashCmd to list files in remote storage."""
        return BashCmd(f"cd '{self.base_path}' && find . -type f | sed 's|^./||'")
    
    def get_upload_stdout_command(self, export_cmd: str, remote_path: str) -> BashCmd:
        """Upload data from a shell command's stdout to remote storage."""
        remote_path = self.base_path / remote_path
        mkdir_cmd = f"mkdir -p '{remote_path.parent}'"
        # export_cmd should output to stdout, we redirect to file
        cmd = f"{mkdir_cmd} && {export_cmd} > '{remote_path}'"
        return BashCmd(cmd)
    
    def get_download_stdout_command(self, remote_path: str) -> BashCmd:
        """Download data from remote storage to stdout."""
        remote_path = self.base_path / remote_path
        return BashCmd(f"cat '{remote_path}'")

    @property
    def clickhouse_params(self) -> ClickhouseParams:
        # Returns (http_path, [access_key, secret_key], {s3_storage_class: storage_class, s3_storage_class: True})
        return ClickhouseParams(
            type="File",
            base_path=str(self.base_path.resolve()),
            args=[],
            settings={}
        )
