# Safety rules (non-negotiable)

This tool moves and deletes the user's files.

1. **Plan, review, apply.** Nothing moves from a single click. Every change is a plan the user reviews first.
2. **Never overwrite.** If a destination exists, pick a unique name or skip.
3. **Journal every move** so a whole batch can be undone.
4. **Verify cross-drive moves:** copy, verify the hash, then delete the source. Check free space first.
5. **Duplicates are never auto-deleted.** The user picks the keeper per group. Removing a duplicate moves it to the system trash (freedesktop spec, per drive). **Permanent delete** is a separate, explicit confirmation, is never a one-click action, and cannot be undone.
6. **Protect project and system folders:** `.git`, `node_modules`, `target`, OS directories, and anything outside the chosen locations. The backend never reads or acts on a path outside them.
7. **Do not follow symlinks.**
8. **Handle missing drives and I/O errors gracefully.** No panics on filesystem errors.
9. **Drives may be unmounted at any time.** Never assume they are present.
10. **The backend never trusts the frontend.** The frontend sends ids, not paths to act on. Apply names a plan the backend created and stored. See [api.md](./api.md).
11. **Moves are crash-safe.** The journal records each step before it happens, cross-drive copies use a temporary name until verified, and recovery runs at every backend start. See [lifecycle.md](./lifecycle.md).
