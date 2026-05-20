#!/usr/bin/env python3
"""Copy the bundled Agent Workflow Kit project template into a target project."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

AUTO_DEV_EXCLUDE_PATTERNS = [
    "/AGENTS.md",
    "/agent-state.md",
    "/codex-progress.md",
    "/codex-progress-archive.md",
    "/feature_list.json",
    "/init.sh",
    "/project_DS/",
]

AUTO_DEV_EXCLUDE_HEADER = "# Agent Workflow Kit / auto_dev local files"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Copy the bundled Codex agent workflow project template into a target directory."
    )
    parser.add_argument("target", help="Target project directory that should receive the template files.")
    parser.add_argument(
        "--template-root",
        default=str(Path(__file__).resolve().parents[1] / "assets" / "project-template"),
        help="Template directory to copy from. Defaults to the bundled asset directory.",
    )
    parser.add_argument(
        "--create-dir",
        action="store_true",
        help="Create the target directory if it does not already exist.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing target files. Without this flag, existing root memory files are preserved.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned operations without writing files.",
    )
    parser.add_argument(
        "--no-git-exclude",
        action="store_true",
        help="Do not update .git/info/exclude when the target is a Git repository.",
    )
    return parser.parse_args()


def ensure_directory(path: Path, create_dir: bool, dry_run: bool) -> None:
    if path.exists() and not path.is_dir():
        raise ValueError(f"Target exists but is not a directory: {path}")
    if path.exists():
        return
    if not create_dir:
        raise FileNotFoundError(
            f"Target directory does not exist: {path}. Re-run with --create-dir if this is intended."
        )
    if not dry_run:
        path.mkdir(parents=True, exist_ok=True)


def iter_template_files(template_root: Path) -> list[Path]:
    if not template_root.is_dir():
        raise FileNotFoundError(f"Template root does not exist: {template_root}")
    return sorted(path for path in template_root.rglob("*") if path.is_file())


def copy_file(src: Path, dest: Path, overwrite: bool, dry_run: bool) -> str:
    existed = dest.exists()
    if existed and not overwrite:
        return "skipped-existing"
    if not dry_run:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
    return "overwritten" if existed and overwrite else "created"


def git_exclude_path(target: Path) -> Path | None:
    git_path = target / ".git"
    if git_path.is_dir():
        return git_path / "info" / "exclude"
    return None


def update_git_exclude(target: Path, dry_run: bool) -> dict[str, object]:
    exclude_path = git_exclude_path(target)
    if exclude_path is None:
        return {
            "status": "not-git-repository",
            "path": None,
            "added_patterns": [],
            "existing_patterns": [],
        }

    existing_text = exclude_path.read_text() if exclude_path.exists() else ""
    existing_lines = set(existing_text.splitlines())
    missing_patterns = [
        pattern for pattern in AUTO_DEV_EXCLUDE_PATTERNS if pattern not in existing_lines
    ]

    if missing_patterns and not dry_run:
        exclude_path.parent.mkdir(parents=True, exist_ok=True)
        with exclude_path.open("a") as handle:
            if existing_text and not existing_text.endswith("\n"):
                handle.write("\n")
            if AUTO_DEV_EXCLUDE_HEADER not in existing_lines:
                handle.write(f"\n{AUTO_DEV_EXCLUDE_HEADER}\n")
            for pattern in missing_patterns:
                handle.write(f"{pattern}\n")

    return {
        "status": "updated" if missing_patterns else "already-current",
        "path": str(exclude_path),
        "added_patterns": missing_patterns,
        "existing_patterns": [
            pattern for pattern in AUTO_DEV_EXCLUDE_PATTERNS if pattern in existing_lines
        ],
    }


def main() -> int:
    args = parse_args()
    template_root = Path(args.template_root).expanduser().resolve()
    target = Path(args.target).expanduser().resolve()

    ensure_directory(target, args.create_dir, args.dry_run)

    operations = []
    for src in iter_template_files(template_root):
        relative = src.relative_to(template_root)
        dest = target / relative
        status = copy_file(src, dest, args.overwrite, args.dry_run)
        operations.append({"status": status, "path": str(dest), "source": str(relative)})

    git_exclude = (
        {
            "status": "disabled",
            "path": None,
            "added_patterns": [],
            "existing_patterns": [],
        }
        if args.no_git_exclude
        else update_git_exclude(target, args.dry_run)
    )

    summary = {
        "target": str(target),
        "template_root": str(template_root),
        "dry_run": args.dry_run,
        "overwrite": args.overwrite,
        "git_exclude": git_exclude,
        "created": sum(1 for item in operations if item["status"] == "created"),
        "overwritten": sum(1 for item in operations if item["status"] == "overwritten"),
        "skipped_existing": sum(1 for item in operations if item["status"] == "skipped-existing"),
        "operations": operations,
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
