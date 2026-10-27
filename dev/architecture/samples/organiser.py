#!/usr/bin/env python3
"""File-Organiser: index, de-duplicate and sort files across several drives.

Workflow (nothing is moved until `apply`):
  scan   -> index every file on the configured drives into a SQLite catalogue
  dupes  -> report duplicate files (size, then full SHA-256)
  plan   -> write a JSON move plan (dry run); review it
  apply  -> execute a plan, writing an undo journal
  undo   -> reverse an applied plan from its journal
"""
import argparse
import hashlib
import json
import os
import shutil
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONFIG_PATH = HERE / "config.json"
DB_PATH = HERE / "catalogue.db"

DEFAULT_CONFIG = {
    "drives": ["/mnt/DATA", "/mnt/STORAGE", "/media/carl/TOSHIBA EXT"],
    "exclude_dirs": [
        ".git", "node_modules", "__pycache__", ".venv", "venv", ".cache",
        "snap", "lost+found", "$RECYCLE.BIN", "System Volume Information",
        ".Trash-1000", "Organised",
    ],
    "organised_dir": "Organised",
    # Optional: send a category to a specific drive, e.g. {"Video": "/media/carl/TOSHIBA EXT"}
    "category_drive": {},
    "categories": {
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".heic", ".tiff", ".svg", ".raw", ".cr2", ".nef"],
        "Video": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"],
        "Audio": [".mp3", ".flac", ".wav", ".aac", ".ogg", ".m4a", ".wma"],
        "Documents": [".pdf", ".doc", ".docx", ".odt", ".txt", ".md", ".rtf", ".xls", ".xlsx", ".ods", ".ppt", ".pptx", ".csv", ".epub"],
        "Archives": [".zip", ".tar", ".gz", ".bz2", ".xz", ".7z", ".rar", ".iso", ".deb", ".rpm", ".appimage"],
        "Code": [".py", ".js", ".ts", ".java", ".c", ".cpp", ".h", ".go", ".rs", ".sh", ".json", ".yaml", ".yml", ".html", ".css", ".sql"],
    },
    "date_subfolders": True,
}


def load_config():
    cfg = dict(DEFAULT_CONFIG)
    if CONFIG_PATH.exists():
        cfg.update(json.loads(CONFIG_PATH.read_text()))
    return cfg


def categorise(path, cfg):
    ext = Path(path).suffix.lower()
    for cat, exts in cfg["categories"].items():
        if ext in exts:
            return cat
    return "Other"


def walk_files(root, exclude, recursive=True):
    excl = set(exclude)
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = [d for d in dirnames if d not in excl]
        for name in filenames:
            p = os.path.join(dirpath, name)
            if os.path.islink(p):
                continue
            yield p
        if not recursive:
            break


def sha256(path, block=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(block):
            h.update(chunk)
    return h.hexdigest()


def db():
    con = sqlite3.connect(DB_PATH)
    con.execute(
        "CREATE TABLE IF NOT EXISTS files (path TEXT PRIMARY KEY, drive TEXT, size INTEGER,"
        " mtime REAL, category TEXT, sha256 TEXT)"
    )
    return con


# ---------------------------------------------------------------- scan
def cmd_scan(args):
    cfg = load_config()
    con = db()
    for drive in cfg["drives"]:
        if not os.path.isdir(drive):
            print(f"! skipping missing drive: {drive}", file=sys.stderr)
            continue
        print(f"Scanning {drive} ...")
        con.execute("DELETE FROM files WHERE drive=?", (drive,))
        n = 0
        for p in walk_files(drive, cfg["exclude_dirs"]):
            try:
                st = os.stat(p)
            except OSError:
                continue
            con.execute(
                "INSERT OR REPLACE INTO files VALUES (?,?,?,?,?,NULL)",
                (p, drive, st.st_size, st.st_mtime, categorise(p, cfg)),
            )
            n += 1
        con.commit()
        print(f"  {n} files")
    print(f"Catalogue: {DB_PATH}")


# ---------------------------------------------------------------- dupes
def cmd_dupes(args):
    con = db()
    sizes = con.execute(
        "SELECT size FROM files WHERE size >= ? GROUP BY size HAVING COUNT(*) > 1", (args.min_size,)
    ).fetchall()
    for (size,) in sizes:
        for (path,) in con.execute("SELECT path FROM files WHERE size=? AND sha256 IS NULL", (size,)).fetchall():
            try:
                con.execute("UPDATE files SET sha256=? WHERE path=?", (sha256(path), path))
            except OSError:
                pass
        con.commit()
    groups = con.execute(
        "SELECT sha256, size FROM files WHERE sha256 IS NOT NULL GROUP BY sha256 HAVING COUNT(*) > 1"
        " ORDER BY size * (COUNT(*) - 1) DESC"
    ).fetchall()
    report, wasted = [], 0
    for h, size in groups:
        paths = [r[0] for r in con.execute("SELECT path FROM files WHERE sha256=? ORDER BY path", (h,))]
        wasted += size * (len(paths) - 1)
        report.append({"sha256": h, "size": size, "paths": paths})
    out = HERE / "duplicates.json"
    out.write_text(json.dumps(report, indent=2))
    print(f"{len(report)} duplicate groups, {wasted / 1e9:.2f} GB reclaimable -> {out}")
    print("Duplicates are only reported; delete them yourself after review.")


# ---------------------------------------------------------------- plan
def unique_dest(dest, taken):
    base, n = Path(dest), 1
    while str(dest) in taken or os.path.lexists(dest):
        dest = base.with_name(f"{base.stem}_{n}{base.suffix}")
        n += 1
    taken.add(str(dest))
    return str(dest)


def cmd_plan(args):
    cfg = load_config()
    sources = [os.path.abspath(s) for s in args.source]
    for s in sources:
        if not os.path.isdir(s):
            sys.exit(f"Source not a directory: {s}")
    moves, taken = [], set()
    for src in sources:
        drive = next((d for d in cfg["drives"] if src == d or src.startswith(d.rstrip("/") + "/")), src)
        for p in walk_files(src, cfg["exclude_dirs"], recursive=args.recursive):
            cat = categorise(p, cfg)
            target_drive = cfg["category_drive"].get(cat, drive)
            parts = [target_drive, cfg["organised_dir"], cat]
            if cfg["date_subfolders"]:
                parts.append(datetime.fromtimestamp(os.path.getmtime(p)).strftime("%Y"))
            dest = unique_dest(os.path.join(*parts, os.path.basename(p)), taken)
            if os.path.abspath(dest) != os.path.abspath(p):
                moves.append({"src": p, "dst": dest})
    out = Path(args.output)
    out.write_text(json.dumps({"created": time.time(), "moves": moves}, indent=2))
    print(f"Plan: {len(moves)} moves -> {out}  (dry run, nothing moved)")
    for m in moves[:20]:
        print(f"  {m['src']}\n    -> {m['dst']}")
    if len(moves) > 20:
        print(f"  ... and {len(moves) - 20} more")


# ---------------------------------------------------------------- apply / undo
def cmd_apply(args):
    plan = json.loads(Path(args.plan).read_text())
    journal, done = Path(args.plan).with_suffix(".journal.json"), []
    for m in plan["moves"]:
        src, dst = m["src"], m["dst"]
        if not os.path.exists(src) or os.path.lexists(dst):
            print(f"skip (missing source or destination exists): {src}")
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.move(src, dst)
        done.append(m)
        journal.write_text(json.dumps(done, indent=2))
    print(f"Moved {len(done)} files. Undo with: organiser.py undo {journal}")


def cmd_undo(args):
    done = json.loads(Path(args.journal).read_text())
    n = 0
    for m in reversed(done):
        if os.path.exists(m["dst"]) and not os.path.lexists(m["src"]):
            os.makedirs(os.path.dirname(m["src"]), exist_ok=True)
            shutil.move(m["dst"], m["src"])
            n += 1
    print(f"Restored {n} files.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("scan", help="index all drives").set_defaults(fn=cmd_scan)
    d = sub.add_parser("dupes", help="find duplicates in the catalogue")
    d.add_argument("--min-size", type=int, default=1, help="ignore files smaller than N bytes")
    d.set_defaults(fn=cmd_dupes)
    p = sub.add_parser("plan", help="create a dry-run move plan")
    p.add_argument("--source", nargs="+", required=True, help="folders to organise")
    p.add_argument("--recursive", action="store_true", help="include subfolders")
    p.add_argument("--output", default=str(HERE / "plan.json"))
    p.set_defaults(fn=cmd_plan)
    a = sub.add_parser("apply", help="execute a plan")
    a.add_argument("plan")
    a.set_defaults(fn=cmd_apply)
    u = sub.add_parser("undo", help="reverse an applied plan")
    u.add_argument("journal")
    u.set_defaults(fn=cmd_undo)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
