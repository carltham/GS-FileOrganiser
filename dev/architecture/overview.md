# Overview

## Two programs

The application is two separate programs. They share only the API contract in [api.md](./api.md).

```
Frontend (Qt 6, C++ Widgets)             Backend (Rust)
  Locations | Browse | Duplicates |        API server (localhost HTTP + WebSocket)
  Rules | Plan | History                     ^
  views only, no file logic                Application services (use cases, job runner)
        |                                    ^
        |   HTTP + WebSocket, token        Core (scanner, hasher, classifier, rules engine,
        +--------------------------------->      planner, journaled mover, safety checks)
                                             ^
                                           Storage: SQLite catalogue, plans, journal, config
```

- The frontend is a client. It never reads the drives or the database.
- The backend runs without a UI and enforces every safety rule. It never trusts the frontend.
- The backend is a child process of the frontend. See [lifecycle.md](./lifecycle.md).

## Source layout (planned)

```
backend/     Cargo workspace: core (no network code), server (API)
frontend/    CMake project, Qt 6 Widgets
```

The two trees have separate build files, dependencies and test suites. Neither imports the other.

## Layer rules

- Backend `core` has no network or UI code and is testable on its own.
- The API server only translates between the contract and the application services.
- Long work (scan, hash, move) runs in background jobs and reports through events. See [ui-jobs.md](./ui-jobs.md).
- Safety constraints apply to every layer. See [safety.md](./safety.md).
