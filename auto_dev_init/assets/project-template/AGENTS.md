# AGENTS.md

This file is the default-loaded project summary and operating constitution for Codex agents in this repository.

## 1. Project Summary
* **Project:** Replace with your project name
* **Domain:** Replace with a one-line business description
* **Goal:** Replace with the current delivery goal
* **Tech stack:** Replace with the main stack

## 2. Memory Files
All workflow files live under `.ark/` in the project root. Agents read them in this order at startup:

1. `AGENTS.md` (this file, project root)
2. `.ark/agent-state.md` — current handoff summary
3. `.ark/feature_list.json` — active task queue; every task includes a sequential `task_id` (e.g., `001-auth-schema`)
4. `.ark/codex-progress.md` — recent log (read only if agent-state.md is insufficient)

Read on demand only:
* `.ark/final_feature_list.json` — rolled-up previous task queues preserved by `$Task_init`
* `.ark/codex-progress-archive.md` — older detailed history
* `.ark/lessons.json` — cross-session knowledge base of discovered pitfalls and architecture facts
* `.ark/project_goal.md` — current development goal, acceptance criteria, and gap analysis
* `.ark/init.sh` — project startup and validation entry point
* `.ark/rules/` — code constraint docs; read only the file that matches your task type (see Doc Routing)
* `.ark/workflows/` — workflow contracts; read only when investigating the automation loop

## 3. Project Facts
Replace this section with the high-signal facts that should remain stable across sessions:
* core domain invariants,
* important data model rules,
* high-risk integrations,
* and any cross-module constraints.

## 4. Doc Routing

Read these files on demand only — not at startup. Load the file that matches what you are about to write:

* writing frontend components or page logic → `.ark/rules/frontend_rules.md`
* writing UI interactions, layouts, or visual design → `.ark/rules/ui_design_system.md`
* writing backend endpoints, service logic, or persistence → `.ark/rules/backend_rules.md`
* designing module structure or data-flow boundaries → `.ark/rules/project_architecture.md`
* investigating the task-planning loop → `.ark/workflows/task_init_loop.md`
* investigating the automated execution loop → `.ark/workflows/auto_dev_loop.md`

Parent agents own shared coordination-file updates and Git commits during `$Auto_dev`; workers return validation evidence and changed-file lists.

Keep this file short. Put generic workflow logic in global skills, not here.
