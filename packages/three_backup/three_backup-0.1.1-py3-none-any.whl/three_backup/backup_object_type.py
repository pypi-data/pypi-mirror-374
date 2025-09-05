from enum import Enum, StrEnum, auto


class BackupObjectType(StrEnum):
    """Types of backup objects supported by the system."""

    LXD = auto()
    POSTGRES = auto()
    CLICKHOUSE = auto()
    ZFS = auto()

    @staticmethod
    def from_cls(cls) -> "BackupObjectType":
        return BackupObjectType[cls.__name__.upper().replace("BACKUPOBJECT", "")]


class BackupObjectSubType(Enum):
    """Subtypes for different backup objects."""
    
    TABLE = auto()
    VIEW = auto()
    PROFILE = auto()
    NETWORK = auto()
    VOLUME = auto()
    CONTAINER = auto()
    DATASET = auto()