# Environment

- OS: Linux Mint 21.3 (MATE, GTK3-based), Ubuntu 22.04 base.
- Drives in scope:
  - `/mnt/DATA` (ext4, NVMe)
  - `/mnt/STORAGE` (ext4)
  - `/media/carl/TOSHIBA EXT` (NTFS)
- Drives may be unmounted at any time. See [safety.md](./safety.md).
- Drive UUIDs are listed in [storage.md](./storage.md).
- `samples/organiser.py` is a throwaway Python prototype of the core logic. Port its ideas, then delete it.
- Toolchain: the Rust toolchain is installed (`cargo 1.99.1`). The Qt 6 development packages are not installed yet.
