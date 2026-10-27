# Scanning

Read-only: the scanner indexes files and never moves, hashes or deletes anything. Schema is in [storage.md](./storage.md).

## Scope

- The user chooses the folders to catalogue. Each is a **location** (see [storage.md](./storage.md)). Nothing outside the locations is read.
- Walk every location and record one row per regular file.
- Skip symlinks and the exclude list (`.git`, `node_modules`, `target`, caches, recycle bins).
- Hashing is **not** part of scanning. It is deferred to the Duplicates step and only runs on files that share a size.
- **NTFS** is treated like the other drives. The drive's filesystem type is recorded, and names that differ only by case are flagged.

## Incremental rescans

- Each scan has a `scan_id`. Files seen get the new `scan_id`.
- Rows of the scanned location that keep an old id after the scan are marked missing. This is cheaper than deleting and reinserting. Rows outside the scanned location are never touched.
- Unmounted drives are skipped, not purged.

## Pipeline

- The scanner is a producer and the database writer is a single consumer, connected by a bounded channel, so memory stays flat on millions of files.

## Metadata captured

- Size, mtime, extension, category, inode and device (to spot hardlinks). These are the fields of the generic `FileEntry` in [file-model.md](./file-model.md).
- Do not rely on atime or ctime, because NTFS reports them differently.

## Errors

- Permission-denied and vanished files are recorded in `scan_errors` and never abort the scan.
