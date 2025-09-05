from pathlib import Path
from typing import Dict, Any
from ..bash_cmd import BashCmd
from ..remote_storage import RemoteStorage, ClickhouseParams

class S3Storage(RemoteStorage):
    """Remote storage implementation that uses S3 via s3cmd."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize S3 remote with configuration."""
        self.base_path = config["base_path"]  # e.g. s3://bucket-name/path/in/bucket
        self.s3cfg_path = config["s3cfg_path"]  # path to s3cmd config file
        # Read .s3cfg by self.s3cfg_path file and obtain access key and secret key
        with open(self.s3cfg_path) as f:
            s3cfg_content = f.read()        
        def parse_s3cfg(content):
            result = {}
            for line in content.splitlines():
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                key, value = line.split('=', 1)
                result[key.strip()] = value.strip()
            return result
        s3cfg = parse_s3cfg(s3cfg_content)
        self.access_key = s3cfg['access_key']
        self.secret_key = s3cfg['secret_key']              
        self.host_base = s3cfg['host_base']
        # Compute http_path: https://host_base/{base_path without s3:// prefix}
        base_path_no_prefix = self.base_path
        if base_path_no_prefix.startswith('s3://'):
            base_path_no_prefix = base_path_no_prefix[5:]
        self.http_path = f"https://{self.host_base}/{base_path_no_prefix.lstrip('/')}"
    
    @property
    def clickhouse_params(self) -> ClickhouseParams:        
        return ClickhouseParams(
            type="S3",
            base_path=self.http_path,
            args=[repr(self.access_key), repr(self.secret_key)],
            settings={"use_same_s3_credentials_for_base_backup": True}
        )

    def get_upload_file_command(self, local_path: Path, remote_path: str) -> BashCmd:
        """Return a BashCmd to upload a file to S3 storage using s3cmd."""
        # Compose full S3 path     
        s3_full_path = f"{self.base_path.rstrip('/')}/{remote_path.lstrip('/')}"
        cmd = f"s3cmd  --no-progress --config '{self.s3cfg_path}' put '{local_path}' '{s3_full_path}'"
        return BashCmd(cmd)

    def get_download_file_command(self, remote_path: str, local_path: Path) -> BashCmd:
        """Return a BashCmd to download a file from S3 storage using s3cmd."""
        s3_full_path = f"{self.base_path.rstrip('/')}/{remote_path.lstrip('/')}"
        cmd = f"s3cmd  --no-progress --config '{self.s3cfg_path}' get '{s3_full_path}' '{local_path}'"
        return BashCmd(cmd)

    def get_list_backups_command(self) -> BashCmd:
        """Return a BashCmd to list files in S3 storage using s3cmd."""
        # List files and extract only the path, removing self.base_path and the following slash
        # Example: s3://maxi-backup/abc/def.txt -> abc/def.txt
        cmd = (
            f"s3cmd --config '{self.s3cfg_path}' ls -r '{self.base_path}' "
            f"| awk '{{print $4}}' "
            f"| sed 's|^{self.base_path.rstrip('/')}/||'"
        )
        return BashCmd(cmd)

    def get_upload_stdout_command(self, export_cmd: str, remote_path: str) -> BashCmd:
        """Upload data from a shell command's stdout to S3 storage using s3cmd."""
        s3_full_path = f"{self.base_path.rstrip('/')}/{remote_path.lstrip('/')}"
        # Pipe export_cmd's stdout to s3cmd put -
        cmd = f"{export_cmd} | s3cmd --no-progress --config '{self.s3cfg_path}' put - '{s3_full_path}'"
        return BashCmd(cmd)
    
    def get_download_stdout_command(self, remote_path: str) -> BashCmd:
        """Download data from S3 storage to stdout using s3cmd."""
        s3_full_path = f"{self.base_path.rstrip('/')}/{remote_path.lstrip('/')}"
        cmd = f"s3cmd --no-progress --config '{self.s3cfg_path}' get '{s3_full_path}' -"
        return BashCmd(cmd)
