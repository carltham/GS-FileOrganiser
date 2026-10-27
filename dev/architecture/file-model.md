# File model

A generic file object describes any file. Specialised kinds (image, video, audio, document, archive) extend it with extra data and behaviour.

## Why not inheritance

Rust has no class inheritance. The same goal is met with:

- **Composition:** a specialised file *contains* the generic one.
- **Enum:** the set of kinds is closed and known, so an enum with typed variants is exhaustive and checked by the compiler.
- **Traits:** shared behaviour is a trait that each kind implements.

## Generic object

`FileEntry` holds what every file has. It is exactly what the first scan records. Columns are in [storage.md](./storage.md).

```
FileEntry
  id, drive_id, rel_path (raw bytes), name, ext,
  size, mtime, inode, device,
  kind (enum), scan_id, missing, sha256 (optional)
```

- No behaviour that depends on the file's type lives here.
- It never reads file contents.

## Specialised objects

```
File
  entry:   FileEntry
  details: FileDetails

FileDetails (enum)
  Generic                      no extra data (default, and all unknown types)
  Image(ImageMeta)             width, height, taken_at, camera
  Video(VideoMeta)             duration, width, height, codec
  Audio(AudioMeta)             duration, artist, album, title
  Document(DocumentMeta)       pages, title
  Archive(ArchiveMeta)         entry_count, uncompressed_size
```

- Adding a kind means adding one variant and one metadata type. The compiler then flags every place that must handle it.
- A file with no specialised data is `Generic`. Nothing breaks if a kind is unknown.

## Shared behaviour (traits)

```
trait Classify          entry -> FileKind        by extension, later by magic bytes
trait ExtractMetadata   entry -> Option<FileDetails>   reads contents, one impl per kind
```

- Extractors are registered per kind in one place, so the scanner and the API layer never switch on type themselves.
- Generic operations (move, hash, display name) work on `FileEntry` only.

## First scan

- The first scan fills only `FileEntry`, including `kind`, derived from the extension. It does not open files.
- Specialised metadata is extracted later, on demand or in a separate background job, so the scan stays fast. See [scanning.md](./scanning.md).

## Storage of specialised data

- The generic `files` table holds `FileEntry`.
- Specialised data goes in a side table keyed by `file_id` (for example `image_meta`, `video_meta`), created only when that extraction exists. See [storage.md](./storage.md).

## Open

- Side tables per kind, or one `file_details` table with a JSON column. Side tables are typed and indexable. JSON is simpler to extend. Current preference: side tables.
- Categories in the placement rules (see [decisions.md](./decisions.md)) map onto `kind`. Decide whether they are the same thing.
