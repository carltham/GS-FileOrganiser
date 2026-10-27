# Architecture

One file per concern. Keep each file focused, and link between them instead of repeating content.

| Concern | File |
|---|---|
| Generic file object and specialised kinds | [file-model.md](./file-model.md) |
| Machine, drives, prototype | [environment.md](./environment.md) |
| Technology choices and open questions | [decisions.md](./decisions.md) |
| Layers, source layout, the two programs | [overview.md](./overview.md) |
| API contract between backend and frontend | [api.md](./api.md) |
| Backend start, stop and recovery | [lifecycle.md](./lifecycle.md) |
| Rules that protect the user's files | [safety.md](./safety.md) |
| Database, schema, drive identity, paths | [storage.md](./storage.md) |
| Walking the drives and recording files | [scanning.md](./scanning.md) |
| Background jobs and how the UI drives them | [ui-jobs.md](./ui-jobs.md) |
| Ordered milestones and their acceptance criteria | [milestones.md](./milestones.md) |
| Test-driven, top-down development approach | [testing.md](./testing.md) |
| Throwaway reference code | [samples/](./samples) |
