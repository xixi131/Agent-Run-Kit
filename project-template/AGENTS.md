# AGENTS.md

This file is the default-loaded project summary and operating constitution for Codex agents in this repository.

## 1. Project Summary
* **Project:** Replace with your project name
* **Domain:** Replace with a one-line business description
* **Goal:** Replace with the current delivery goal
* **Tech stack:** Replace with the main stack

## 2. Memory Files
Agents should treat these files as the external memory layer:
* `AGENTS.md`: stable project facts and routing rules
* `feature_list.json`: active task queue and pass/fail state
* `final_feature_list.json`: rolled-up previous task queues preserved by `$Task_init`
* `agent-state.md`: current handoff summary
* `codex-progress.md`: recent human/agent log
* `codex-progress-archive.md`: older detailed history
* `init.sh`: project startup entry

## 3. Project Facts
Replace this section with the high-signal facts that should remain stable across sessions:
* core domain invariants,
* important data model rules,
* high-risk integrations,
* and any cross-module constraints.

## 4. Doc Routing
Tell agents which docs to read for which task types. Keep detailed rules outside this file and ask agents to read them only when relevant:
* frontend implementation: `project_DS/specification/frontend_rules.md`
* UI and interaction work: `project_DS/specification/ui_design_system.md`
* backend implementation: `project_DS/specification/backend_rules.md`
* architecture or module boundaries: `project_DS/specification/project_architecture.md`
* queue planning: `project_DS/workflows/task_init_loop.md`
* automation execution: `project_DS/workflows/auto_dev_loop.md`

Keep this file short. Put generic workflow logic in global skills, not here.
