from typing import Dict, List, Any
import yaml
from .fnmatch import fnmatch
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
from .backup_object_id import BackupObjectId


class ConfigManager:
    """Manages configuration loading and pattern matching for backup objects."""

    def __init__(self, config_path: str, credentials: Dict[str, str]):
        self.config_path = Path(config_path)
        self.config_sections: List[Dict[str, Any]] = []
        self.load_config()
        self.now = datetime.now()
        self.credentials = credentials

    def load_config(self) -> None:
        """Load configuration from YAML file."""
        load_dotenv()  # Load environment variables from .env file
        with open(self.config_path) as f:
            self.config_sections = yaml.safe_load(f)        
        if not isinstance(self.config_sections, list):
            raise ValueError("Config file must contain a list of sections")

    def get_config_for_object(self, object_id: "BackupObjectId") -> Dict[str, Any]:
        """
        Get merged configuration for a backup object.
        Later sections override earlier ones if they match the object ID.
        """
        merged_config: Dict[str, Any] = {}
        # Process sections in order, merging matching ones
        for section in self.config_sections:
            pattern = next(iter(section.keys()))  # First key is the pattern
            config = section[pattern]

            if fnmatch(object_id.url, pattern):
                merged_config.update(config)
        merged_config['now'] = self.now
        merged_config['credentials'] = self.credentials
        return merged_config
