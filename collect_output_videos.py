"""Collect and rename output videos from subdirectories.

The script scans the given root directory (default: current working
working directory) for immediate child directories. For each child
directory that contains a file named ``output.mp4`` (configurable), the
file is copied to the root directory and renamed to match the child
directory name while keeping the original extension.

Example structure::

    根目录/
        课程A/
            output.mp4
        课程B/
            output.mp4
        其他文件.txt

Running the script inside ``根目录`` produces::

    根目录/
        课程A.mp4
        课程B.mp4
        课程A/
            output.mp4
        课程B/
            output.mp4
        其他文件.txt

Conflicting filenames are resolved by appending a numeric suffix, e.g.
``课程A.mp4`` becomes ``课程A_1.mp4`` if the first name is already taken.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def resolve_conflict(target: Path) -> Path:
    """Return a non-conflicting path by appending a numeric suffix if needed."""
    if not target.exists():
        return target

    stem = target.stem
    suffix = target.suffix
    parent = target.parent

    counter = 1
    while True:
        candidate = parent / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def collect_outputs(root: Path, source_name: str = "output.mp4", dry_run: bool = False) -> None:
    """Copy videos from child directories into ``root`` and rename them.

    Parameters
    ----------
    root:
        Directory to scan for child folders and the destination for copied files.
    source_name:
        Name of the source file inside each child directory (default: ``output.mp4``).
    dry_run:
        If True, print planned operations without copying files.
    """
    if not root.is_dir():
        raise NotADirectoryError(f"{root} is not a directory")

    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue

        source = child / source_name
        if not source.is_file():
            print(f"Skipping '{child.name}': {source_name} not found")
            continue

        destination = resolve_conflict(root / (child.name + source.suffix))

        if dry_run:
            print(f"[dry-run] Would copy '{source}' -> '{destination}'")
            continue

        shutil.copy2(source, destination)
        print(f"Copied '{source}' -> '{destination}'")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect output videos from subdirectories")
    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=Path.cwd(),
        help="Root directory containing the subfolders (default: current directory)",
    )
    parser.add_argument(
        "--source-name",
        default="output.mp4",
        help="Name of the video file inside each subfolder (default: output.mp4)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List operations without copying files",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    collect_outputs(args.root, source_name=args.source_name, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
