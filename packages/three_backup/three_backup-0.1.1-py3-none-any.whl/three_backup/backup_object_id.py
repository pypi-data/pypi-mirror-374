from dataclasses import dataclass
from urllib.parse import quote, unquote
from .backup_object_type import BackupObjectType, BackupObjectSubType


@dataclass(frozen=True)
class BackupObjectId:
    """Unique identifier for a backup object."""

    type: BackupObjectType
    subtype: BackupObjectSubType
    level1: str
    level2: str
    level3: str


    def __lt__(self, other):
      if not isinstance(other, BackupObjectId):
        return NotImplemented
      return (
        self.type,
        self.subtype.value,
        self.level1,
        self.level2,
        self.level3,
      ) < (
        other.type,
        other.subtype.value,
        other.level1,
        other.level2,
        other.level3,
      )
      

    @property
    def url(self) -> str:
        return "/".join(
            quote(str(part), safe="")
            for part in [
                self.type.value,
                self.subtype.name.lower(),
                self.level1,
                self.level2,
                self.level3,
            ]
        )

    @classmethod
    def from_url(cls, s: str) -> "BackupObjectId":        
        parts = s.split("/")
        if len(parts) != 5:
            raise ValueError("Invalid BackupObjectId string")
        return cls(
            BackupObjectType(unquote(parts[0])),
            BackupObjectSubType[unquote(parts[1]).upper()],
            unquote(parts[2]),
            unquote(parts[3]),
            unquote(parts[4]),
        )

    @classmethod
    def from_backup_name(cls, backup_name: str) -> "BackupObjectId":
        """Create BackupObjectId from a backup name."""
        parts = backup_name.split("/")
        if len(parts) < 5:
            raise ValueError(
                f"Invalid backup name format: {backup_name}, expected at least 5 parts separated by '/'"
            )
        return cls.from_url("/".join(parts[:5]))
