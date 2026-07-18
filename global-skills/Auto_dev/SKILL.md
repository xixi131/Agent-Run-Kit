---
name: Auto_dev
description: Coordinate a parent-child multi-agent execution loop for this repository. Reads the execution mode (workflow / agent / loop) from .ark/project_goal.md and adapts stopping behavior accordingly. Dispatches workers by task type and model tier, verifies results, updates coordination files, and in loop mode checks acceptance criteria with gap-analysis replanning until all criteria pass or an escalation occurs.
---

# Auto_dev

Use this skill when the user wants to execute pending tasks from the repository's task queue.

All workflow files live under `.ark/` in the project root. When a file is referenced without a path prefix (e.g., `feature_list.json`), read it from `.ark/feature_list.json`.

If `.ark/feature_list.json` is empty, placeholder-only, or does not match the current requirement, stop and use `$Task_init` first.

## Required context

Read the smallest reliable startup context first:
* `AGENTS.md` (project root)
* `.ark/agent-state.md` if it exists
* `.ark/feature_list.json`

Use conditional reading for everything else:
* read `.ark/codex-progress.md` only if `agent-state.md` is missing, stale, or insufficient,
* read `.ark/codex-progress-archive.md` only when you explicitly need older history,
* read `.ark/rules/` only for the rule file that matches your task type,
* read `.ark/init.sh` only when the task type needs runtime startup or verification,
* read `.ark/lessons.json` if it exists and is non-empty — scan for known pitfalls before dispatch,
* read `.ark/project_goal.md` if it exists — record the `## Mode` field (`workflow`, `agent`, or `loop`) and the acceptance criteria for post-batch steps; default to `loop` if mode is absent.

## Memory-aware startup policy
* Use injected memories for stable project conventions, pitfalls, and project shape hints.
* Always verify volatile state from files: queue state in `feature_list.json`, handoff in `agent-state.md`.
* Do not reread `codex-progress.md`, `codex-progress-archive.md`, or `.ark/rules/` docs unless the memory layer and `agent-state.md` are insufficient.
* If a memory conflicts with checked-in files, trust the file.

## Parent agent workflow

1. Read `.ark/project_goal.md` if it exists. Record the `## Mode` value: `workflow`, `agent`, or `loop`. Default to `loop` if absent, unset, or the file does not exist. Parse how many tasks the user wants completed; if omitted, run until the stopping condition for the active mode (see step 23).
2. Run a memory-layer health check before dispatch:
   * if `.ark/codex-progress.md` is too long for default startup,
   * or `.ark/agent-state.md` is missing or clearly stale,
   * or `AGENTS.md` has drifted into duplicated generic SOP,
   * stop and use `$Context_archive` first, then resume.
3. Read `.ark/feature_list.json` top to bottom. Choose the first item with `"passes": false`; record its `task_id`.
4. If there is no pending task, proceed to the post-batch steps (step 23).
5. If the queue is placeholder-only, not executable, or stale, stop and tell the user to run `$Task_init` first.
6. Read the task's `task_id`, `task_type`, and `budget_minutes`:
   * `docs` and `planning` → lightweight fast path,
   * `frontend`, `backend`, and `e2e` → full execution path.
7. If `task_type` is missing, treat the queue as stale and send the user to `$Task_init`.
8. If more than one task was requested, inspect the next pending tasks up to that count and build a dependency plan:
   * tasks are dependent when one produces files, APIs, schemas, state, or UI surfaces that another consumes,
   * tasks are not safe to parallelize when write scopes overlap or both need broad refactors in the same module,
   * tasks may run in parallel when they have independent outcomes and disjoint write scopes.
9. Resolve model tiers, then dispatch the first dependency layer:
   a. **Tier resolution**: read `.ark/model_config.json` if it exists.
      * `fast` tier — use `tiers.fast` if set; otherwise infer the lightweight model for your current provider (e.g., Haiku for Anthropic, gpt-4o-mini for OpenAI).
      * `default` tier — always the current session model; never overridden.
      * `capable` tier — use `tiers.capable` if set; otherwise infer the most capable available model for your current provider (e.g., claude-sonnet-5 for Anthropic, o1 for OpenAI).
   b. **Task-to-tier mapping**: `docs`/`planning` → fast, `frontend`/`backend` → default, `e2e` → capable.
   c. **Platform fallback**: if the platform does not support specifying a model for sub-agents, apply instruction routing only — all workers use the current session model but still receive the appropriate lightweight or full execution instructions for their task type.
   d. Dispatch each worker with the resolved model. Tell every worker they are not alone in the codebase and must stay inside their assigned write scope.
10. For each dispatched task, pass only: `task_id`, description, `task_type`, `budget_minutes`, `steps`, expected write scope, the escalation contract, the active **mode**, and any entries from `.ark/lessons.json` directly relevant to this task (distilled by the parent before dispatch — workers do not read `lessons.json` themselves).
11. For a `docs` or `planning` task, enforce a hard timeout equal to `budget_minutes`.
12. Wait for the current dependency layer to finish before dispatching tasks that depend on it.
13. If a `docs` or `planning` task exceeds its budget or requires the heavy path, escalate as `task-process-mismatch`.
14. If any worker reports an escalation, stop immediately and wait for the user to resolve the blocker.
15. Accept each worker result only if all of the following are true:
    * the worker reports validation against every listed step,
    * the worker reports the concrete verification path used,
    * changed files stay inside the task-scoped write responsibility,
    * the worker did not mutate shared coordination files.
16. Parent performs all shared state updates for accepted tasks:
    * set each accepted `task_id` in `.ark/feature_list.json` to `"passes": true`,
    * refresh `.ark/agent-state.md` when the first pending task or startup read path changes,
    * append one fresh log entry per accepted task to `.ark/codex-progress.md`.
17. Parent verifies acceptance after the shared state update:
    * every accepted `task_id` is now `"passes": true`,
    * `.ark/codex-progress.md` has a fresh matching entry,
    * `.ark/agent-state.md` still matches the first pending task when one exists.
18. Parent performs Git post-processing: stage task-scoped files plus updated coordination files and create one focused commit per accepted task, or one batch commit when parallel tasks are tightly related and conflict-free.
19. If parent-side commit fails, retry at most 3 times.
20. Run remote Git operations (`git fetch`, `git pull`, `git push`) with escalated permissions from the start.
21. If the third commit attempt fails or a remote operation fails under escalation, stop as `post-processing-blocked`.
22. Continue by dependency layer until the requested number of tasks is complete or an escalation occurs.
23. **Post-batch steps** (run after each batch completes or queue empties):
    a. **Lesson extraction** (all modes): collect any `discoveries` returned by workers. Append each new discovery to `.ark/lessons.json` (skip entries whose `lesson` text already exists). Record only non-obvious facts that would otherwise require rediscovery: architecture corrections, environment gotchas, recurring patterns.
    b. **Mode-specific stopping logic**:
       * **`workflow` mode**: when the requested task count is reached or the queue is empty, report which tasks completed and stop. Do not check acceptance criteria. Do not re-plan.
       * **`agent` mode**: when the requested task count is reached or the queue is empty, run a single quality check — review the changes made across all accepted tasks and confirm they address the original requirement as stated in `project_goal.md`. Report any gaps or concerns, then stop. Do not invoke `$Task_init` or re-plan.
       * **`loop` mode**: run the full criteria-and-replan cycle:
         i. **Criteria check**: if `.ark/project_goal.md` exists and has acceptance criteria, verify each criterion using the appropriate method (shell command, API call, browser check, or file check). Mark passing criteria with `[x]` and record per-criterion results under `## Last Check`.
         ii. **Loop decision**:
             - All criteria pass → update `project_goal.md` status to `done`, report completion, stop.
             - Criteria unmet, queue has pending tasks → continue dispatching (return to step 3).
             - Criteria unmet, queue empty → generate a gap analysis (which criteria failed, what is still missing), write it under `## Gap Analysis` in `project_goal.md`, invoke `$Task_init` in `rewrite-pending` mode with the gap analysis as context, return to step 3. Stop if the same criterion has failed in 3 consecutive gap-analysis cycles.
             - No `project_goal.md` or no criteria → report queue status and stop.
       * **Mode absent or unknown**: treat as `loop`.

## Skill boundaries

Use `$Auto_dev` when the task queue exists and you want to execute pending tasks.
Do not use `$Auto_dev` to:
* create or rewrite the queue from a new requirement (use `$Task_init`),
* compress repository memory files (use `$Context_archive`).

## Task type contract

Every task in `.ark/feature_list.json` must declare:
* `task_id`: sequential identifier in format `NNN-<slug>` (e.g., `001-setup-schema`)
* `task_type`: one of `docs`, `planning`, `frontend`, `backend`, or `e2e`
* `budget_minutes`: expected maximum execution time

Default budgets:
* `docs`: 10
* `planning`: 10
* `frontend`: 15–20
* `backend`: 15–20
* `e2e`: 20–30

## Parallel dispatch policy

* Parallelize independent tasks with disjoint write scopes.
* Sequence dependent tasks (schema before API, API before frontend, route before browser verification).
* Never let parallel workers mutate `.ark/feature_list.json`, `.ark/agent-state.md`, or `.ark/codex-progress.md`.
* The parent updates and reconciles all coordination files after each layer.
* Report whether dispatch was parallel or sequential and why.

## Git permissions policy

* Local operations (`git status`, `git diff`, `git add`, `git commit`, `git log`) run normally.
* Remote operations (`git fetch`, `git pull`, `git push`) require escalated permissions immediately.
* Do not run remote commands in restricted sandbox first. Use escalation up front.
* If a remote operation fails under escalation, stop as `post-processing-blocked`.

## Worker contract

Workers return: validation evidence, changed file list, suggested commit message, and an optional `discoveries` list (new non-obvious project facts found during this task — keep it short).

Workers must NOT mutate `.ark/feature_list.json`, `.ark/agent-state.md`, `.ark/codex-progress.md`, or `.ark/lessons.json`. The parent owns all coordination file updates.

### Mode overlay (applied on top of the execution path for every worker)

Read the active mode from the task briefing and adjust behavior accordingly:

* **`workflow`** — execute the assigned steps exactly as described. Do not explore beyond the assigned scope. Do not investigate unrelated code. Return evidence that each step completed as described.
* **`agent`** — reason through the task before acting. Investigate the relevant code to understand the root cause or best approach before writing any changes. Return your reasoning chain alongside the implementation and validation evidence. If you discover that the task description is wrong or incomplete, include that finding in `discoveries`.
* **`loop`** — implement the assigned task and validate strictly against each declared step using the real execution path. Report every failing step explicitly. Do not expand scope.

### Lightweight fast path (docs / planning)
1. Read `AGENTS.md`, then `.ark/agent-state.md` if it exists, then the assigned task.
2. Read only the minimum extra context needed.
3. Skip `.ark/codex-progress.md` unless `agent-state.md` is insufficient.
4. Skip `.ark/init.sh` unless the task explicitly needs runtime output.
5. Implement only the assigned task.
6. Validate with lightweight checks: file exists, headings exist, path is discoverable.
7. Do not launch browser MCP, API checks, or heavy environment startup.
8. If the task clearly requires the heavy path, escalate as `task-process-mismatch`.
9. Return validation evidence, changed file list, suggested commit message, and optional discoveries.
10. Do not run git commands.

### Full execution path (frontend / backend / e2e)
1. Read `AGENTS.md`, then `.ark/agent-state.md` if it exists, then the assigned task.
2. Do NOT read `.ark/codex-progress.md` or `.ark/lessons.json` unless `agent-state.md` is clearly insufficient. The parent already applied lessons before dispatch.
3. Read only the task-routed project docs or code files needed.
4. Run `.ark/init.sh`.
5. Implement only the assigned task.
6. Validate every declared step with the real execution path:
   * browser MCP for user-visible and end-to-end flows,
   * API requests for backend endpoint behavior,
   * database verification when the task writes persisted data.
7. If validation fails, debug the minimum necessary chain: UI → API → backend → database.
8. Self-repair at most 3 times for the same failing symptom. Escalate if the blocker persists.
9. Return validation evidence, changed file list, suggested commit message, and optional discoveries.
10. Do not run git commands.

## Escalation rules

Stop and ask the user when:
* validation still fails after 3 repair attempts,
* prerequisites are missing,
* requirements are unclear,
* task type and required execution path do not match,
* Git post-processing fails after 3 attempts,
* or `.ark/init.sh` reveals an environment failure that cannot be safely recovered.

Include in the escalation report:
* blocker category: `repair-loop-exceeded`, `missing-prerequisite`, `requirement-unclear`, `task-process-mismatch`, `post-processing-blocked`, or `environment-collapse`,
* current error or failing symptom,
* attempted fixes and repair-attempt count,
* verification methods used,
* task type, budget, and elapsed time,
* whether content delivery is already complete and only the commit is blocked,
* impacted files or modules.

## Degraded mode

If sub-agent tooling is unavailable, run the same loop locally as a single agent and clearly report degraded single-agent mode.

## Memory health thresholds

Treat the memory layer as needing archive work when:
* `.ark/codex-progress.md` is roughly over 250 lines or 18 KB,
* `.ark/agent-state.md` is missing and the main log is no longer short,
* `.ark/agent-state.md` does not match the current first pending task,
* or `AGENTS.md` has drifted into repeated generic SOP.

Use `$Context_archive` before continuing when any threshold is met.
