# UI and background jobs

The frontend is a Qt client. It starts jobs through the API and shows the events the backend sends. See [api.md](./api.md).

## Triggering

A scan runs only when the user starts it from the **Locations** screen. Nothing scans at startup, on a timer, or from the command line.

- **Locations screen:** the user adds and removes the folders to catalogue (see [scanning.md](./scanning.md)). Each location shows its drive, status and last scan.
- **Controls:** a Scan button per location and a "Scan all" button. A location on an offline drive has the button disabled and shows an "offline" badge.
- **Flow:** the button sends a "start scan" command. The backend creates a job and replies at once with a job id. The UI thread never blocks on the backend, and requests are asynchronous.

## Progress

- The backend sends `job.started`, `job.progress {files_seen, bytes, current_dir}`, `job.error`, `job.finished` and `job.cancelled` events over the WebSocket.
- The backend throttles progress to about 4 events a second, so a huge scan does not flood the UI.
- The UI shows a progress bar, a live file count and the current folder.

## Cancel

- A Cancel button sends a "cancel job" command. The scanner checks the cancellation flag between directories.
- A cancelled scan commits what it has, and the scan is marked `cancelled` so it can be resumed.

## Concurrency

- One scan per location at a time. Different locations may scan in parallel.
- All SQLite writes go through the single writer. See [scanning.md](./scanning.md).

## Results

- When a scan finishes, the Locations screen refreshes its counts and last-scanned time, and shows files added, changed and missing, plus any errors.

## Closing the window

- Closing during a scan cancels it safely and the scan can be resumed.
- Closing during Apply asks each time: stop after the current file, or wait until finished. The app shows the file being finished and a Force quit button after about 30 seconds. See [lifecycle.md](./lifecycle.md).
- If the backend stops unexpectedly, the app says so and offers a restart.
