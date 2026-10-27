# Testing approach

Test-driven development, top down (outside-in). Each milestone starts from a failing acceptance test at the top and works downward.

## The loop

1. Write an acceptance test for the milestone's "done when" criteria in [milestones.md](./milestones.md). It fails.
2. Write the next layer down as the smallest code that could satisfy it. Whatever it needs from the layer below is defined as a trait, and a test double stands in for it.
3. Write a failing test for that lower layer, make it pass, and repeat until the real implementations exist.
4. The acceptance test now passes against real code. Refactor with all tests green.

## Where "top" is

The programs are separate, so there are two tops, each tested alone.

- **Backend:** the top is the **API**. Acceptance tests call it over HTTP and WebSocket against a real backend started on temporary directories and a temporary SQLite database. They assert on responses and events, such as progress and cancellation (see [ui-jobs.md](./ui-jobs.md)).
- **Frontend:** the top is the **UI**, tested with Qt Test headless (`QT_QPA_PLATFORM=offscreen`) against a **fake backend** that replays canned responses and events. No real drives are involved.
- **Contract tests** check that the real backend and the fake both match the contract in [api.md](./api.md).

## Test levels

| Level | Tests | Doubles used |
|---|---|---|
| Backend acceptance | An API use case end to end, such as "scan fills the catalogue" | None for the logic. A temporary directory tree and a temporary SQLite database. |
| Backend unit (core) | Scanner, classifier, planner, mover | Traits for the filesystem, the clock and the catalogue, so the layer is tested alone |
| Storage | Schema, queries, migrations | A real SQLite database in a temporary location |
| Frontend | Screens and view logic | A fake backend |
| Contract | Real and fake backend against the contract | None |

## Rules

- Lower layers are reached through traits so they can be replaced in tests. Do not add a trait that no test needs.
- Filesystem tests use temporary directories only and never touch the real drives (see [safety.md](./safety.md)).
- Prefer a real SQLite database over a mock. It is cheap, and it tests the actual queries.
- Failure paths are tested as seriously as success: unmounted drive, permission denied, a file that vanishes mid-scan, a cancelled job.
- Safety rules each need at least one test that fails if the rule is broken (never overwrite, journal every move, no symlink following).
- A mock that always passes is a defect. Where a double could hide a real difference, add one test that uses the real implementation.
- Tests live next to the code in the backend `core`. Backend acceptance tests go in `tests/`. Frontend tests live in the frontend tree.

## Tooling (proposed)

- Backend: `cargo test`, `tempfile` for temporary directories, `proptest` for path and name edge cases such as non-UTF-8 names, and `mockall` only if hand-written doubles become tedious.
- Frontend: Qt Test and Qt Quick Test, run headless.
