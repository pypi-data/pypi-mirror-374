import click
from datetime import datetime
from typing import Optional, List

from three_backup.backup_stage import BackupStage
from .config_manager import ConfigManager
from .remote_storage import RemoteManager
from .backup_object import BackupObject
from .backup_object_type import BackupObjectType
from .discovery import Discovery
from .implementations import (
    PostgresBackupObject,
    LXDBackupObject,
    ClickHouseBackupObject,
    ZFSBackupObject
)


def get_backup_object_fields() -> List[str]:
    # Exclude private attributes and callables
    return [
        attr
        for attr in dir(BackupObject)
        if not attr.startswith("_") and not callable(getattr(BackupObject, attr))
    ]


@click.group()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    default="config.yaml",
    help="Path to config file",
)
@click.option(
    "--systems",
    multiple=True,
    type=click.Choice([e.name for e in BackupObjectType]),
    help="Limit operations to specific backup system(s)",
)
@click.option(
    "--select", "-s", default="*", help="Filter objects by pattern (fnmatch syntax)"
)
@click.option("--pg-host", default='""', help="PostgreSQL host")
@click.option("--pg-port", default="5432", help="PostgreSQL port")
@click.option("--pg-user", default="postgres", help="PostgreSQL user")
@click.option("--pg-password", default="", help="PostgreSQL password")
@click.option("--ch-host", default="localhost", help="Clickhouse host")
@click.option("--ch-port", default="9000", help="Clickhouse port")
@click.option("--ch-user", default="default", help="Clickhouse user")
@click.option("--ch-password", default="", help="Clickhouse password")
@click.option(
    "--pg-local-backup-directory",
    default="./pg_local_backups",
    help="PostgreSQL local backup directory",
)
@click.option(
    "--lxd-local-backup-directory",
    default="./lxd_local_backups",
    help="LXD local backup directory",
)
@click.pass_context
def cli(
    ctx: click.Context,
    config: str,
    systems: Optional[List[str]],
    select: str,
    pg_host: str,
    pg_port: str,
    pg_user: str,
    pg_password: str,
    pg_local_backup_directory: str,
    lxd_local_backup_directory: str,
    ch_host: str,
    ch_port: str,
    ch_user: str,
    ch_password: str,
):
    """three_backup: Unified backup tool for LXD, PostgreSQL, and ClickHouse"""
    ctx.ensure_object(dict)
    ctx.obj["config_manager"] = ConfigManager(
        config,
        credentials={
            "pg_host": pg_host,
            "pg_port": pg_port,
            "pg_user": pg_user,
            "pg_password": pg_password,
            "pg_local_backup_directory": pg_local_backup_directory,
            "lxd_local_backup_directory": lxd_local_backup_directory,
            "ch_host": ch_host,
            "ch_port": ch_port,
            "ch_user": ch_user,
            "ch_password": ch_password,
        },
    )
    ctx.obj["remote_manager"] = RemoteManager()
    ctx.obj["select"] = select
    # Transform selected system names to class list
    if systems:
        # Map enum names to classes
        type_to_class = {
            BackupObjectType.POSTGRES.name: PostgresBackupObject,
            BackupObjectType.LXD.name: LXDBackupObject,
            BackupObjectType.CLICKHOUSE.name: ClickHouseBackupObject,
            BackupObjectType.ZFS.name: ZFSBackupObject,
        }
        ctx.obj["systems"] = [type_to_class[name] for name in systems]
    else:
        ctx.obj["systems"] = [
            PostgresBackupObject,
            LXDBackupObject,
            ClickHouseBackupObject,
            ZFSBackupObject,
        ]
    ctx.obj["discovery"] = Discovery(
        ctx.obj["config_manager"],
        ctx.obj["remote_manager"],
        ctx.obj["select"],
        ctx.obj["systems"],
    )


@cli.command()
@click.option(
    "--fields",
    "-f",
    multiple=True,
    type=click.Choice(get_backup_object_fields()),
    help="Fields to display for each object",
)
@click.pass_context
def list(ctx: click.Context, fields: List[str]):
    """List objects available for backup and their selected fields"""
    discovery = ctx.obj["discovery"]
    objects = discovery.discover_objects()
    # Use default if no fields specified
    if not fields:
        fields = ["current_stage"]
    for obj in objects:
        values = []
        for field in fields:
            values.append(str(getattr(obj, field, None)))
        click.echo(f"{obj.url}: " + ", ".join(values))


@cli.command()
@click.option(
    "--fields",
    "-f",
    multiple=True,
    type=click.Choice(get_backup_object_fields()),
    help="Fields to display for each object",
)
@click.option(
    "--moment",
    type=str,
    help="Time moment to list backups for (e.g. '2023-10-01 12:00:00')",
    default=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
)
@click.pass_context
def list_back(ctx: click.Context, fields: List[str], moment: str):
    """List objects available for recovery and their selected fields"""
    discovery = ctx.obj["discovery"]
    # parse datetime with of without time
    try:
        moment_dt = datetime.strptime(moment, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        moment_dt = datetime.strptime(moment, "%Y-%m-%d")
    discovery.config_manager.now = moment_dt
    objects = discovery.discover_objects_back()
    # Use default if no fields specified
    if not fields:
        fields = ["current_stage"]
    for obj in objects:
        values = []
        for field in fields:
            values.append(str(getattr(obj, field, None)))
        click.echo(f"{obj.url}: " + ", ".join(values))


@cli.command()
@click.option(
    "--max-stage",
    type=click.Choice(
        [
            stage.name
            for stage in BackupStage
            if stage
            not in [
                BackupStage.DISABLED,
                BackupStage.EXISTS,                
                BackupStage.RESTORED,
            ]
        ]
    ),
    help="Override max stage for all objects (e.g. BACKUP_BASE)",
    default=BackupStage.ROTATED_REMOTE.name,  # Default to ROTATED_REMOTE
)
@click.pass_context
def run(ctx: click.Context, max_stage: str):
    """Run backup operations on selected objects"""
    # Default to ROTATED_REMOTE if not specified
    max_stage_enum = BackupStage[max_stage]
    discovery = ctx.obj["discovery"]
    objects = discovery.discover_objects()
    for obj in objects:
        if obj.disabled:
            click.echo(f"Skipping disabled object: {obj.url}")
            continue
        click.echo(f"Running backup for {obj.url} ...")
        obj.advance_to_stage(min(max_stage_enum, obj.max_stage))


@cli.command()
@click.option(
    "--max-stage",
    type=click.Choice(
        [
            stage.name
            for stage in [
                BackupStage.SYNCED_BASE,
                BackupStage.SYNCED_INCREMENTAL,                
                BackupStage.RESTORED,
            ]
        ]
    ),
    help="Override max stage for all objects (e.g. BACKUP_BASE)",
    default=BackupStage.RESTORED.name
)
@click.option(
    "--moment",
    type=str,
    help="Time moment to list backups for (e.g. '2023-10-01 12:00:00')",
    default=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
)
@click.option(    
    "--onexists",
    type=click.Choice(["skip", "fail", "ask", "overwrite"]),
    default="ask",
    help="Run on existing objects only, skipping those without backups",
)
@click.pass_context
def run_back(ctx: click.Context, max_stage: str, moment: str, onexists: str = "ask"):
    """Run restore operations on selected objects"""
    discovery = ctx.obj["discovery"]
    max_stage_enum = BackupStage[max_stage]
    try:
        moment_dt = datetime.strptime(moment, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        moment_dt = datetime.strptime(moment, "%Y-%m-%d")
    discovery.config_manager.now = moment_dt
    objects = discovery.discover_objects_back()
    for object in objects:
        if object.disabled:
            click.echo(f"Skipping disabled object: {object.url}")
            continue
        click.echo(f"Running restore for {object.url} ...")        
        object.advance_to_stage_back(max_stage_enum, onexists=onexists)


def main():
    """Entry point for the CLI"""
    cli(obj={})
