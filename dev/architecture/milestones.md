# Milestones

## 1. Catalogue all files into a database

Design: [scanning.md](./scanning.md), [storage.md](./storage.md), [ui-jobs.md](./ui-jobs.md), [api.md](./api.md), [lifecycle.md](./lifecycle.md).

Done when:

- The user can add and remove locations from the Locations screen, and overlapping locations are merged or rejected.
- A scan of the chosen locations, started from the UI, fills the catalogue and can be cancelled and resumed.
- A second scan with no changes is much faster and creates no duplicate rows.
- Files removed between scans are flagged missing, only within the scanned location.
- An unmounted drive does not lose its rows.
- The backend starts with the app, stops with it, and exits if the app dies.
- The API rejects a request with a missing or wrong token, a wrong `Host`, or any `Origin` header.
- Tests use temporary directories only, never the real drives.

## Later (proposed order)

2. Duplicates: hash files that share a size, report groups, user picks a keeper.
3. Rules and Plan: placement rules, reviewable plan.
4. Apply and Undo: journaled moves.
