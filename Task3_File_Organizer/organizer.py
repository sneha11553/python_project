"""Automated File Organizer & Cleanup Utility

Sorts files in a folder into category subfolders (Documents, Images, Videos,
Audio, Archives, Code, Others) by file extension.

Usage:
    python3 organizer.py                      # organizes ~/Downloads
    python3 organizer.py /path/to/folder      # organizes a chosen folder
    python3 organizer.py /path --dry-run      # preview only, moves nothing

Features:
  - Creates category folders only when needed
  - Never overwrites: name collisions become  name (1).ext, name (2).ext ...
  - Handles PermissionError / OSError per file and keeps going
  - Skips hidden files, subfolders and this script itself
  - Logs everything to organizer.log and prints a summary
"""

import argparse
import logging
import os
import shutil
import sys
from collections import Counter
from pathlib import Path

CATEGORIES = {
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx",
                  ".csv", ".ppt", ".pptx", ".md", ".epub"},
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".heic", ".tiff", ".ico"},
    "Videos": {".mp4", ".mkv", ".mov", ".avi", ".wmv", ".flv", ".webm", ".m4v"},
    "Audio": {".mp3", ".wav", ".flac", ".aac", ".m4a", ".ogg"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".tgz"},
    "Code": {".py", ".js", ".ts", ".java", ".c", ".cpp", ".h", ".cs", ".html", ".css",
             ".json", ".xml", ".sql", ".sh", ".ipynb", ".go", ".rs", ".php", ".rb"},
}
OTHERS = "Others"
EXT_TO_CATEGORY = {ext: cat for cat, exts in CATEGORIES.items() for ext in exts}
LOG_FILE = "organizer.log"


def setup_logging(log_path):
    logger = logging.getLogger("organizer")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    fmt = logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s", "%Y-%m-%d %H:%M:%S")
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(fmt)
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(logging.Formatter("%(levelname)-7s | %(message)s"))
    logger.addHandler(file_handler)
    logger.addHandler(console)
    return logger


def categorize(path):
    return EXT_TO_CATEGORY.get(path.suffix.lower(), OTHERS)


def unique_destination(dest_dir, filename):
    """Return a path in dest_dir that does not exist yet (adds ' (n)' on collision)."""
    candidate = dest_dir / filename
    if not candidate.exists():
        return candidate
    stem, suffix = Path(filename).stem, Path(filename).suffix
    n = 1
    while True:
        candidate = dest_dir / f"{stem} ({n}){suffix}"
        if not candidate.exists():
            return candidate
        n += 1


def organize(folder, dry_run, logger):
    stats = Counter()
    moved_by_category = Counter()
    this_script = Path(__file__).resolve()

    try:
        entries = sorted(os.scandir(folder), key=lambda e: e.name.lower())
    except PermissionError:
        logger.error("Permission denied reading folder: %s", folder)
        return stats, moved_by_category
    except FileNotFoundError:
        logger.error("Folder not found: %s", folder)
        return stats, moved_by_category

    for entry in entries:
        path = Path(entry.path)

        if entry.is_dir(follow_symlinks=False):
            stats["skipped_folders"] += 1
            continue
        if entry.name.startswith(".") or path.resolve() == this_script or entry.name == LOG_FILE:
            stats["skipped_other"] += 1
            continue
        if not entry.is_file(follow_symlinks=False):
            stats["skipped_other"] += 1
            continue

        category = categorize(path)
        dest_dir = folder / category
        try:
            if not dry_run:
                dest_dir.mkdir(exist_ok=True)
            destination = unique_destination(dest_dir, entry.name)
            renamed = destination.name != entry.name
            if dry_run:
                logger.info("[DRY RUN] %s -> %s/%s", entry.name, category, destination.name)
            else:
                shutil.move(str(path), str(destination))
                logger.info("Moved %s -> %s/%s%s", entry.name, category, destination.name,
                            "  (renamed: name collision)" if renamed else "")
            stats["moved"] += 1
            stats["renamed"] += int(renamed)
            moved_by_category[category] += 1
        except PermissionError:
            logger.error("Permission denied, skipped: %s", entry.name)
            stats["errors"] += 1
        except (shutil.Error, OSError) as exc:
            logger.error("Could not move %s: %s", entry.name, exc)
            stats["errors"] += 1

    return stats, moved_by_category


def print_summary(folder, stats, by_category, dry_run):
    line = "=" * 44
    print(f"\n{line}")
    print(f"{'EXECUTION SUMMARY' + (' (DRY RUN)' if dry_run else ''):^44}")
    print(line)
    print(f"Folder:             {folder}")
    print(f"Files relocated:    {stats['moved']}")
    print(f"Renamed (collision):{stats['renamed']:>4}")
    print(f"Errors:             {stats['errors']}")
    print(f"Skipped (folders):  {stats['skipped_folders']}")
    print(f"Skipped (other):    {stats['skipped_other']}")
    if by_category:
        print("-" * 44)
        for cat, count in sorted(by_category.items()):
            print(f"  {cat:<12} {count:>5}")
    print(line)


def main():
    parser = argparse.ArgumentParser(description="Organize a folder by file type.")
    parser.add_argument("folder", nargs="?", default=str(Path.home() / "Downloads"),
                        help="folder to organize (default: ~/Downloads)")
    parser.add_argument("--dry-run", action="store_true", help="preview without moving files")
    args = parser.parse_args()

    folder = Path(args.folder).expanduser().resolve()
    if not folder.is_dir():
        print(f"Error: '{folder}' is not a folder.")
        sys.exit(1)

    logger = setup_logging(folder / LOG_FILE if not args.dry_run else Path(LOG_FILE))
    logger.info("Starting organizer on %s%s", folder, " (dry run)" if args.dry_run else "")
    stats, by_category = organize(folder, args.dry_run, logger)
    print_summary(folder, stats, by_category, args.dry_run)
    logger.info("Finished: %d moved, %d errors", stats["moved"], stats["errors"])


if __name__ == "__main__":
    main()
