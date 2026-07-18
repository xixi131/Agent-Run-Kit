---
name: auto_dev_init
description: Initialize or migrate the Agent Workflow Kit into a target project. Copies AGENTS.md to the project root and all other workflow files into a .ark/ subdirectory. If the project was previously initialized with the old flat-file layout, migrates existing files from the root into .ark/ automatically. Use when the user invokes $auto_dev_init or asks to set up (or upgrade) a target project with the workflow kit.
---

# auto_dev_init

Use this skill when the user wants to install or upgrade the Agent Workflow Kit in a specific project directory.

## What this skill does

* **First-time install**: copies `AGENTS.md` to the project root and all other workflow files into a `.ark/` subdirectory. If the target is a Git repository, adds the workflow files to `.git/info/exclude` so they stay local by default.
* **Migration from old layout**: if the project was previously initialized with workflow files at the root (old flat layout), the script detects this automatically and moves them into `.ark/`. New template files (such as `lessons.json` and `project_goal.md`) are added without overwriting migrated content.
* **Already on new layout**: if `.ark/` already exists, copies only missing template files without overwriting existing ones.

## Required input

The user should provide a target directory path:

```text
$auto_dev_init /Users/a12110/Code/my-project
```

If the target path is missing, ask for it before writing files.

## Safety rules

* Treat the target as a project root.
* Do not overwrite existing files unless the user explicitly asks with `--overwrite`.
* Preserve existing content during migration — move files, do not delete them.
* If the target has `.git/`, write local exclude rules to `.git/info/exclude` by default. Do not edit committed `.gitignore` unless the user explicitly asks.
* Use `--dry-run` first when the target project may already have workflow files.
* Use `--create-dir` only when the user asks to create a new target directory.

## Workflow

1. Resolve the target directory from the user's request.
2. If unsure whether the target has existing files, run a dry run first:

   ```bash
   python3 <skill_dir>/scripts/copy_project_template.py <target_dir> --dry-run
   ```

3. Run the script (it auto-detects install state and handles migration):

   ```bash
   python3 <skill_dir>/scripts/copy_project_template.py <target_dir>
   ```

4. If the target is a Git repository, confirm that `.git/info/exclude` was updated with:
   - `/AGENTS.md`
   - `/.ark/`

5. If the user explicitly requests overwriting existing template files:

   ```bash
   python3 <skill_dir>/scripts/copy_project_template.py <target_dir> --overwrite
   ```

6. If the target directory should be created:

   ```bash
   python3 <skill_dir>/scripts/copy_project_template.py <target_dir> --create-dir
   ```

7. Report: install state detected (`fresh`, `already-ark`, or `needs-migration`), files migrated or copied, files skipped, and Git exclude status. Remind the user to customize:
   - `AGENTS.md` (project summary, rules, doc routing)
   - `.ark/init.sh` (real startup or validation command)
   - `.ark/rules/*` (project-specific code constraint docs)
   - `.ark/project_goal.md` (acceptance criteria via `$Task_init`)

## Expected result

After success, the target project contains:

```text
AGENTS.md                              ← project root (auto-loaded by Codex)
.ark/
  agent-state.md
  codex-progress.md
  codex-progress-archive.md
  feature_list.json
  final_feature_list.json
  lessons.json
  project_goal.md
  init.sh
  rules/
    backend_rules.md
    frontend_rules.md
    project_architecture.md
    ui_design_system.md
  workflows/
    auto_dev_loop.md
    task_init_loop.md
```
