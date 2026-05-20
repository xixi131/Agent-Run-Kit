---
name: auto_dev_init
description: Copy the Agent Workflow Kit project-level template files into a specified repository directory. Use when the user invokes $auto_dev_init or asks to initialize a target project with AGENTS.md, feature_list.json, agent-state.md, codex-progress files, init.sh, and project_DS workflow docs. If the target is a Git repository, add the auto_dev files to .git/info/exclude so they stay local by default.
---

# auto_dev_init

Use this skill when the user wants to install the Agent Workflow Kit project template into a specific project directory.

This skill copies the bundled `assets/project-template/` tree into the target directory so the target project can use `$Task_init`, `$Auto_dev`, and `$Context_archive`.

If the target directory is a Git repository, it also adds the copied auto_dev memory files to `.git/info/exclude`. This keeps the workflow files local to the repository clone by default without modifying the project's committed `.gitignore`.

## Required input

The user should provide a target directory path, for example:

```text
$auto_dev_init /Users/a12110/Code/my-project
```

If the target path is missing, ask for it before writing files.

## Safety rules

- Treat the target as a project root.
- Do not overwrite existing root memory files unless the user explicitly asks to overwrite.
- Preserve existing files by default.
- If the target has `.git/`, write local exclude rules to `.git/info/exclude` by default.
- Do not edit committed `.gitignore` unless the user explicitly asks for that instead.
- Use `--dry-run` first when the target project may already have workflow files.
- Use `--create-dir` only when the user asks to create a new target directory or the target clearly should be created.

Root memory files include:

```text
AGENTS.md
agent-state.md
codex-progress.md
codex-progress-archive.md
feature_list.json
init.sh
project_DS/
```

## Workflow

1. Resolve the target directory from the user's request.
2. If unsure whether overwriting is allowed, run a dry run first:

   ```bash
   python3 <skill_dir>/scripts/copy_project_template.py <target_dir> --dry-run
   ```

3. Copy the template without overwriting existing files by default:

   ```bash
   python3 <skill_dir>/scripts/copy_project_template.py <target_dir>
   ```

4. If the target is a Git repository, confirm that `.git/info/exclude` was updated with local auto_dev exclude entries. To skip this behavior only when explicitly requested:

   ```bash
   python3 <skill_dir>/scripts/copy_project_template.py <target_dir> --no-git-exclude
   ```

5. If the user explicitly requests overwriting existing template files:

   ```bash
   python3 <skill_dir>/scripts/copy_project_template.py <target_dir> --overwrite
   ```

6. If the target directory should be created:

   ```bash
   python3 <skill_dir>/scripts/copy_project_template.py <target_dir> --create-dir
   ```

7. Report the copied, skipped, overwritten files and Git exclude status. Remind the user to customize:
   - `AGENTS.md`
   - `init.sh`
   - `feature_list.json` via `$Task_init`

## Expected result

After success, the target project should contain:

```text
AGENTS.md
agent-state.md
codex-progress.md
codex-progress-archive.md
feature_list.json
init.sh
project_DS/workflows/auto_dev_loop.md
project_DS/workflows/task_init_loop.md
```
