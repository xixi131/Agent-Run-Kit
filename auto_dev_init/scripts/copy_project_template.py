#!/usr/bin/env python3
"""Copy the bundled Agent Workflow Kit project template into a target project."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ARK_DIR = ".ark"

# Patterns added to .git/info/exclude so workflow files stay local by default.
AUTO_DEV_EXCLUDE_PATTERNS = [
    "/AGENTS.md",
    f"/{ARK_DIR}/",
]

AUTO_DEV_EXCLUDE_HEADER = "# Agent Workflow Kit / auto_dev local files"

# Files that lived at the project root in the old layout (pre-.ark migration).
OLD_ROOT_FILES = [
    "feature_list.json",
    "final_feature_list.json",
    "agent-state.md",
    "codex-progress.md",
    "codex-progress-archive.md",
    "lessons.json",
    "project_goal.md",
    "init.sh",
]
OLD_ROOT_DIRS = ["project_DS"]


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
        help="Overwrite existing target files. Without this flag, existing files are preserved.",
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


def detect_install_state(target: Path) -> str:
    """Return 'fresh', 'already-ark', or 'needs-migration'."""
    if (target / ARK_DIR).is_dir():
        return "already-ark"
    old_found = [f for f in OLD_ROOT_FILES if (target / f).exists()]
    old_dirs_found = [d for d in OLD_ROOT_DIRS if (target / d).is_dir()]
    if old_found or old_dirs_found:
        return "needs-migration"
    return "fresh"


def migrate_to_ark(target: Path, dry_run: bool) -> dict:
    """Move old-layout root files into .ark/."""
    ark_dir = target / ARK_DIR
    if not dry_run:
        ark_dir.mkdir(exist_ok=True)

    moves = []
    for filename in OLD_ROOT_FILES:
        src = target / filename
        if src.exists():
            dest = ark_dir / filename
            if not dry_run:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dest))
            moves.append({
                "from": str(src.relative_to(target)),
                "to": str(dest.relative_to(target)),
            })

    for dirname in OLD_ROOT_DIRS:
        src = target / dirname
        if src.is_dir():
            dest = ark_dir / dirname
            if not dry_run:
                if dest.exists():
                    # Merge: copy files from src into dest without overwriting
                    for item in src.rglob("*"):
                        if item.is_file():
                            rel = item.relative_to(src)
                            target_file = dest / rel
                            if not target_file.exists():
                                target_file.parent.mkdir(parents=True, exist_ok=True)
                                shutil.copy2(item, target_file)
                else:
                    shutil.move(str(src), str(dest))
            moves.append({
                "from": str(src.relative_to(target)),
                "to": str(dest.relative_to(target)),
            })

    return {"moves": moves}


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
        "existing_patterns": [p for p in AUTO_DEV_EXCLUDE_PATTERNS if p in existing_lines],
    }


def main() -> int:
    args = parse_args()
    template_root = Path(args.template_root).expanduser().resolve()
    target = Path(args.target).expanduser().resolve()

    ensure_directory(target, args.create_dir, args.dry_run)

    install_state = detect_install_state(target)
    migration_result: dict = {"moves": []}

    if install_state == "needs-migration":
        migration_result = migrate_to_ark(target, args.dry_run)

    # Copy template files (AGENTS.md to root, everything else lands under .ark/)
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
        "install_state": install_state,
        "dry_run": args.dry_run,
        "overwrite": args.overwrite,
        "migration": migration_result,
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
