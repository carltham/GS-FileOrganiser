# Backend lifecycle

The backend is a child process of the frontend. It starts when the app starts and stops when the app closes.

## Start

- The frontend launches the backend, passes the session token privately, and reads back the port. See [api.md](./api.md).
- One backend serves one frontend. No lock file or discovery file is needed.
- On start the backend runs **recovery** before accepting work: it reads the journal, completes or rolls back any unfinished move, and deletes leftover temporary partial copies.

## Stop

The app asks the backend to shut down, and the backend stops at a safe point.

| Situation | Behaviour |
|---|---|
| Nothing running | Close the database cleanly and exit. |
| Scan running | Cancel between directories, commit what it has, mark the scan `cancelled`. The next scan continues cheaply through the `scan_id` design. |
| Apply running | The app asks each time. **Stop after the current file:** remaining moves stay pending in the plan and can be resumed. **Wait until finished:** the window stays open and shows progress. **Cancel:** return to the app with Apply still running. |

### Deadline

- The backend gets about **30 seconds** to reach a safe point after a shutdown request.
- The app shows a status such as "Finishing `<file>`..." and a **Force quit** button.
- After the deadline, or on Force quit, the backend exits as it is. This is safe because every step is journaled and recovery cleans up on the next start.

## Failure cases

- **The app crashes or is killed.** The backend watches its parent (a parent-death signal on Linux and/or an end-of-file on a pipe from the app). It then takes the same safe stop as a normal shutdown, so it never runs without an owner.
- **The backend is killed hard** (`SIGKILL`, out of memory, power loss). No handler can run, so recovery at the next start handles it.
- **The backend crashes while the app is open.** The app notices, says so clearly, and offers a restart. Interrupted jobs are marked failed or interrupted.

## Rules that make this safe

- A same-drive move is one atomic rename.
- A cross-drive move writes the copy under a recognisable temporary name, verifies the hash, renames it into place, and only then deletes the source. Recovery removes any temporary file it finds.
- The journal records the intent of each step before the step happens. See [safety.md](./safety.md).
