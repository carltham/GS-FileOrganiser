# API contract

The backend and the frontend are separate programs. They share nothing except this contract. The frontend never touches the drives or the database. Lifecycle is in [lifecycle.md](./lifecycle.md).

## Transport (decided)

- HTTP and WebSocket on `127.0.0.1` only. The backend never binds another interface.
- The operating system picks the port. The backend reports it to the frontend at launch.
- **Session token.** The frontend generates a random token and gives it to the backend privately at launch (through a pipe or standard input, never the command line). Every request and the WebSocket handshake must carry it.
- **Origin and host checks.** The backend rejects a request when any of these is true:
  - The token is missing or wrong.
  - The `Host` header is not `127.0.0.1:<port>`.
  - An `Origin` header is present. The Qt client sends none, and browsers always do, so no web page can use the API.

## Message kinds

| Kind | Direction | Purpose |
|---|---|---|
| Command | frontend to backend | Ask for a change: add a location, start a scan, cancel a job |
| Query | frontend to backend | Read state: list locations, browse files, job status |
| Event | backend to frontend, over the WebSocket | Report progress and state changes |

### Draft messages for milestone 1 (names provisional)

- Commands: add location, remove location, start scan (location ids), cancel job, request shutdown.
- Queries: list drives, list locations, browse and search files (paged), job status, last scan summary.
- Events: `job.started`, `job.progress {job_id, files_seen, bytes, current_dir}`, `job.error`, `job.finished`, `job.cancelled`, `drive.online`, `drive.offline`, `backend.shutting_down {reason, current_item}`.

## Rules for messages

- **Plain data only.** No UI types, callbacks or shared memory.
- **Paths are raw bytes,** encoded (for example base64) next to a lossy display string. File names may not be valid UTF-8 (see [storage.md](./storage.md)).
- **Large lists are paged** with cursors. Sorting, filtering and search run on the backend. The frontend never asks for everything.
- **Progress is throttled by the backend** to about 4 events a second.
- **Ids are opaque** to the frontend.
- **Errors are structured:** a stable code plus a message. The frontend never parses message text.

## The backend is the authority

- The frontend sends intent and ids, never paths to act on. A plan is created and stored by the backend. Apply names a stored plan id and nothing else.
- The backend validates every request against [safety.md](./safety.md), including that targets lie inside the chosen locations. A buggy or hostile client cannot make it move arbitrary paths.

## Versioning

- The handshake carries an API version. On a mismatch the backend refuses the connection with a clear error.

## Open

- **Contract format.** A C++ frontend cannot share Rust types, so a schema is still needed. Options:
  - Define the types in Rust and export a schema (for example `schemars` or `utoipa`).
  - Write an OpenAPI specification by hand. OpenAPI does not describe WebSocket events, so events would need AsyncAPI or a written description.
- Whether the WebSocket or Server-Sent Events carries events. The current preference is the WebSocket.
