"""Implementations of backup objects for different systems."""

from .postgres import PostgresBackupObject
from .lxd import LXDBackupObject
from .clickhouse import ClickHouseBackupObject
from .zfs import ZFSBackupObject

__all__ = ['PostgresBackupObject', 'LXDBackupObject', 'ClickHouseBackupObject', 'ZFSBackupObject']