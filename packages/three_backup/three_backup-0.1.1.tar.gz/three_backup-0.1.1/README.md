## three_backup: Project Specification

### Overview

three_backup is a tool for making incremental backups of LXD containers, PostgreSQL, and ClickHouse. The tool is designed to be robust, configurable, and extensible, supporting S3-compatible storage (including non-Amazon providers like Selectel), and providing a clear, staged backup lifecycle.

---

### 1. Tool Detection

- On startup, the tool checks the running machine for the presence of the following executables:
    - `lxc` (for LXD)
    - `pg_dump` (for PostgreSQL)
    - `clickhouse-client` (for ClickHouse)
- Only sources with detected tools are processed.

---

### 2. Backup Object Creation

- For each detected source, the tool creates **BackupObjects**.
- Each BackupObject has the following fields:
    - `type`: The system type (`lxd`, `postgres`, `clickhouse`)
    - `subtype`: For LXD: `container` or `volume`; for databases: `table` or `view`
    - `level1`, `level2`, `level3`: Hierarchical identifiers, meaning differs by system (see below)
- **Three-level structure** for all systems:
    - **LXD**:
        - `level1`: Storage pool name
        - `level2`: Project name (or `default` if projects are not used)
        - `level3`: Container or volume name
    - **PostgreSQL**:
        - `level1`: Database name
        - `level2`: Schema name
        - `level3`: Table or view name
    - **ClickHouse**:
        - `level1`: Cluster name (or `default` if not clustered)
        - `level2`: Database name
        - `level3`: Table or view name
- Each object can be referenced by an ID:
`type/subtype/level1/level2/level3`
Example: `postgres/table/production/public/users`

---

### 3. Incremental Backup Implementation

- **LXD**: Uses `lxc snapshot` for base snapshots and ZFS incremental snapshots for incrementals.
- **PostgreSQL 17+**: Uses the built-in incremental backup feature (base backup + incremental files).
- **ClickHouse**: Uses the built-in backup feature that stores backups directly in S3.
- For ClickHouse, there are no local backups; stages like `snapshot_incremental` and `partially_synced` are skipped, proceeding directly from `snapshot_base` to `synced_s3`.

---

### 4. Backup Stages

Each object can have one of the following stages. Each stage implies all previous stages are met:

- **exists**: Object exists in the source (LXD or database)
- **snapshot_base**: Most recent base snapshot is created according to `base_schedule` in config
- **snapshot_incremental**: Most recent incremental snapshot is created according to `incremental_schedule` in config
- **partially_synced**: At least some parts of S3 multipart upload for the most recent snapshot are uploaded (indicates a failed or incomplete upload; must be resumed)
- **synced_s3**: All available snapshots are fully uploaded to S3
- **rotated_locally**: Number of local snapshots does not exceed config; old ones are removed, only the most recent remain
- **rotated_s3**: Same as above, but for S3 snapshots

For ClickHouse, only relevant stages are used (`exists`, `snapshot_base`, `synced_s3`, `rotated_s3`).

---

### 5. Configuration File

- The config file is a standard YAML file.
- It consists of sections, each specified by a glob-like pattern on object IDs (e.g., `*` matches any sequence).
- Configs from all matched sections are merged; if keys contradict, the lower section (appearing later in the file) wins.
- Example config:

```yaml
- clickhouse/*:
    base_schedule: 13 16 1 * *
    incremental_schedule: 13 16 * * *
- clickhouse/table/tmp*:
    disable: true
- postgres/table/local*:
    max_stage: snapshot_incremental
- "*":
    s3_endpoint: selectel.ru
    s3_secret_key: 123
    max_base_snapshots_local: 1
    max_incremental_snapshots_local: 3
    max_base_snapshots_s3: 3
    max_incremental_snapshots_s3: 40
```

- Config options include:
    - Cron strings for base/incremental backups
    - Max number of base/incremental snapshots (local/S3)
    - S3 endpoint, bucket, client ID/secret
    - `max_stage` (the highest stage to process for this object)
    - `disable` flag (skip object if true)

---

### 6. Program Modes

- **list**: Prints the names and optionally the stages of all objects. Output includes current stage and max_stage.
- **run**: Tries to move every object to its configured `max_stage`.
- **restore**: Restores an object from a snapshot. If the snapshot is not available locally, it is downloaded from S3 (for ClickHouse, restore is performed directly from S3). Supports overriding levels or adding suffixes for restoration targets via CLI arguments (e.g., `--level2-suffix`).
- The `--select` (`-s`) argument specifies which objects to process, using the beginning of the selector to filter by source type (`clickhouse`, `postgres`, or `lxd`).

---

### 7. Additional Implementation Details and Decisions

- **Tool Detection**: Only process sources for which required tools are present.
- **Temporary Storage**: Local snapshots are stored in a configurable directory, organized by object ID.
- **S3 Integration**:
    - Uses access/secret keys from config.
    - Handles multipart uploads, with resume capability for incomplete uploads.
    - Progress bar for S3 upload/download (e.g., using tqdm).
- **Scheduling**:
    - The tool is intended to be run via cron, not as a daemon.
    - If a previous run is still active (lock file exists), a new run can kill the old process and remove the stale lock.
- **Compression**: Uses the best available compression for each system (zstd for PostgreSQL and ClickHouse, native ZFS compression for LXD).
- **Authentication**:
    - S3 credentials in config.
    - PostgreSQL/ClickHouse credentials via environment variables or `.env` file.
- **Concurrency Control**: Lock file to prevent concurrent runs.
- **Error Handling**: Errors are reported to stderr; a summary is printed to stdout.
- **Restore Mode**: Supports restoring to a different target (e.g., different schema/container name) via CLI overrides.
- **Verification**: After backup, a simple verification step (e.g., integrity check for PostgreSQL) is performed if possible.
- **Metrics**: Size of each object is tracked; S3 transfers display a progress bar.
- **Testing and Performance**: No built-in integrity testing or dry-run mode at this stage; performance impact is not a current priority.
- **Security**: Encryption is not implemented, but compression is applied where possible.

---

### 8. Special Cases and Clarifications

- **Three-level structure** is used for all systems, with placeholder values (`default`) if a level does not apply (e.g., non-clustered ClickHouse, LXD without projects).
- **Stage tracking for ClickHouse** is performed by listing S3 objects.
- **Config merging** is determined by the order in the YAML file (lower sections override higher ones).
- **Disable flag** disables the object entirely; to stop at a specific stage, use `max_stage`.
- **Partial uploads**: If an object is in `partially_synced`, the next run will attempt to resume the upload.
- **No daemon mode**: Scheduling is handled externally (e.g., cron).
- **Restoration**: After restoring from S3, temporary files are deleted. For ClickHouse, restore is performed directly from S3.
- **.env support**: Environment variables can be loaded from a `.env` file for database credentials.
