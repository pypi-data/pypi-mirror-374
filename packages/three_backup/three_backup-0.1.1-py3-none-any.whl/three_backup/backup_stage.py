from enum import Enum, auto

class BackupStage(Enum):
    """Represents the various stages a backup object can be in."""

    DISABLED = auto()
    EXISTS = auto()
    BACKUP_BASE = auto()
    SYNCED_BASE = auto()
    BACKUP_INCREMENTAL = auto()
    SYNCED_INCREMENTAL = auto()
    ROTATED_LOCALLY = auto()
    ROTATED_REMOTE = auto()
    RESTORED = auto()

    def __str__(self):
        return self.name

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented
