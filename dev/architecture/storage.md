# Storage

SQLite via `rusqlite`. It is the single source of truth and the only database. Rationale: embedded, crash-safe (the undo journal must survive failures), relational queries fit the catalogue, and one writer plus many readers matches the scan design.

## Search

- Filename and path search uses SQLite FTS5 in the same database file.
- If FTS5 proves too limited, add Tantivy as an optional embedded index rebuilt from the catalogue. It never becomes a source of truth.
- Elasticsearch, OpenSearch and other server databases are ruled out: they need a separate service, are heavy, and are not transactional.

## Decisions

- **Drive identity is the filesystem UUID, not the mount path.** Mount points change, so files are stored as `(drive_id, relative_path)`. Current UUIDs:
  - DATA `02dd1a9d-4461-431e-a4bf-583de9e34d58`
  - STORAGE `eb5424c8-1698-43d6-9eba-39e242d08b8f`
  - TOSHIBA EXT `6638A15138A12153` (NTFS)
- **Locations** are the folders the user chose to catalogue, stored as `(drive_id, relative_path)`. Locations must not overlap: adding a folder inside an existing location is merged or rejected. Rows of a removed location stay, marked out of scope, until the user purges them. Purging deletes catalogue rows only, never files.
- **The filesystem type is recorded per drive.** For NTFS and other case-insensitive filesystems, names that differ only by case are flagged. Do not rely on atime or ctime.
- **Paths are stored as raw bytes (BLOB).** Linux paths are not guaranteed to be valid UTF-8. A separate display column holds a lossy UTF-8 form for display.
- **The database lives in the user data directory** (`~/.local/share/file-organiser/catalogue.db`), never on a scanned drive.
- **Bulk writes.** Insert in batches of several thousand rows per transaction, with SQLite in WAL mode.
- **Hashes are cached** by path, size and mtime, so rescans stay fast.
- **Unmounted drives keep their rows,** flagged offline. They are never purged.

## Draft schema: catalogue

```
drives(id, uuid, label, fstype, case_insensitive, mount_path, online)
locations(id, drive_id, rel_path BLOB, display_path, in_scope, last_scan_id)
scans(id, location_id, started_at, finished_at, status, files_seen, errors)
files(id, drive_id, location_id, rel_path BLOB, display_path, name, ext, size,
      mtime, category, inode, scan_id, missing, out_of_scope, sha256 NULL)
scan_errors(scan_id, rel_path BLOB, error)

UNIQUE(drive_id, rel_path)
INDEX on size, (ext), (category), scan_id
```

## Draft schema: later milestones

- `plans` and `moves(src, dst, status)`.
- `journal(batch_id, src, dst, timestamp)` for undo.
- Rules are data: match on extension, size, age or path, with an action that sets a destination drive and folder pattern.
