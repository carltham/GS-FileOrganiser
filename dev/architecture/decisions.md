# Decisions

| Topic | Decision | State |
|---|---|---|
| Structure | Two separate programs, a backend and a frontend, sharing only the API contract. See [overview.md](./overview.md). | Decided |
| Backend language | Rust (braces, strong typing, memory and thread safety). Python is ruled out. | Decided |
| Frontend | Qt 6, C++ Widgets. No browser, web view or Electron. | Decided |
| Transport | Localhost HTTP plus WebSocket, with a session token and `Origin`/`Host` checks. See [api.md](./api.md). | Decided |
| Backend lifecycle | Child process of the frontend. Stops when the app closes. About 30 second shutdown deadline. See [lifecycle.md](./lifecycle.md). | Decided |
| Closing during Apply | The app asks each time: stop after the current file, or wait until finished. | Decided |
| Scan scope | Chosen folders (locations) only. See [scanning.md](./scanning.md). | Decided |
| NTFS | Treated like the other drives. Record the filesystem type and flag case-insensitive names. | Decided |
| Contract format | Schema exported from Rust types, or hand-written OpenAPI. See [api.md](./api.md). | Open |
| Storage | SQLite (`rusqlite`), single source of truth. No server database. | Decided |
| Search | SQLite FTS5 first. Tantivy only if FTS5 proves too limited. Elasticsearch ruled out. | Decided |
| Memory control | Arenas (`bumpalo`), fixed pool of hashing buffers, optional counting allocator | Proposed |
| Duplicate handling | System trash by default. Permanent delete only as a separate, explicit confirmation. | Decided |
| Development method | TDD, top down (outside-in), see [testing.md](./testing.md) | Decided |
| First milestone | Catalogue all files (see [milestones.md](./milestones.md)) | Decided |

Update this table whenever a decision changes.

## Open questions

- Contract format for the API (see [api.md](./api.md)).
- Placement rules, for example which categories live on which drive. Not needed for the catalogue milestone.
- Specialised-metadata storage: side tables per kind or one JSON column. See [file-model.md](./file-model.md).
- Whether the placement-rule categories and the file `kind` are the same thing.
