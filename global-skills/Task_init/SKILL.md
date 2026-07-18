---
name: Task_init
description: Break a product requirement into typed, ordered, executable tasks in .ark/feature_list.json. Use when the user asks to initialize, regenerate, or rewrite pending tasks before running $Auto_dev. Tasks are written in English and sized to represent one coherent developer session, not the smallest possible atomic change.
---

# Task_init

Use this skill when the user wants Codex to turn a requirement into executable tasks in `.ark/feature_list.json`.

All workflow files live under `.ark/` in the project root.

Do not implement product code in this turn. This skill is for planning and queue initialization only.

## Required context

Read the smallest reliable planning context first:
* `AGENTS.md` (project root)
* `.ark/agent-state.md` if it exists
* `.ark/feature_list.json`
* `.ark/final_feature_list.json` if it exists

Read `.ark/workflows/task_init_loop.md` for the detailed planning contract.

Read [references/prompt-patterns.md](references/prompt-patterns.md) when you need ready-to-use prompt examples.

Use conditional reading for everything else:
* read `.ark/codex-progress.md` only if `agent-state.md` is missing, stale, or insufficient,
* read `.ark/codex-progress-archive.md` only if older planning or migration history is actually needed,
* read `.ark/rules/` only for the rule file directly relevant to the requirement,
* read `.ark/lessons.json` if it exists and is non-empty — treat its entries as known pitfalls and architecture facts that must inform task boundaries and validation steps,
* read `.ark/project_goal.md` if it exists — check the acceptance criteria and any gap analysis before planning; a gap analysis is the primary planning constraint and overrides broad re-decomposition of the full requirement.

## Planning workflow

1. Read the incoming requirement carefully and identify the target business outcome.
   * If `.ark/lessons.json` exists and is non-empty, apply relevant lessons as constraints: avoid tasks that repeat known-bad patterns, include environment setup steps discovered in prior runs, and reflect architecture corrections into task boundaries.
   * If `.ark/project_goal.md` has a gap analysis, treat the listed gaps as the primary acceptance outcomes. Do not re-decompose the full requirement — generate only the tasks needed to close the specific gaps identified.
2. Run a memory-layer health check before planning:
   * if `.ark/codex-progress.md` is too long for default startup,
   * or `.ark/agent-state.md` is missing or clearly stale,
   * or `AGENTS.md` has drifted into duplicated generic SOP instead of lean project facts,
   * stop normal planning and use `$Context_archive` first, then resume planning.
3. Read the current `.ark/feature_list.json` and `.ark/final_feature_list.json` if it exists.
4. Choose the queue update mode before writing tasks:
   * `replace-active`: archive every current active task into `final_feature_list.json`, clear `feature_list.json`, then write only the new active queue,
   * `rewrite-pending`: preserve completed active tasks in place, archive replaced pending tasks into `final_feature_list.json`, then write the regenerated pending tasks after the completed tasks,
   * `append-phase`: keep the current active queue in place and append the new phase tasks after the existing items.
5. Preserve history according to the selected mode:
   * if `.ark/final_feature_list.json` does not exist, create it as an empty JSON array,
   * never drop a valid current task object silently,
   * preserve each archived task's existing `passes` state and fields,
   * report exactly which mode was used and what moved into `final_feature_list.json`.
6. Load only the relevant rule file from `.ark/rules/` for the current requirement.
7. Read `.ark/codex-progress.md` only if the short handoff is not enough for safe planning.
8. Before writing any task, build a requirement fulfillment map:
   * name each user-visible capability or acceptance outcome in the requirement,
   * identify the smallest coherent runnable slice that proves meaningful progress toward that outcome,
   * include all layers needed for that slice to work end-to-end,
   * defer plumbing-only work unless it is the unavoidable prerequisite for a runnable slice.
9. Reason about the likely implementation path in this repository:
   * the target user-visible outcome,
   * the likely modules, files, and layers involved,
   * the dependency order,
   * the validation path,
   * and which parts can be completed independently.
10. Classify each generated task as `docs`, `planning`, `frontend`, `backend`, or `e2e`.
11. Evaluate task scope and assign `budget_minutes` to every task.
12. Assign every new task a sequential `task_id` in the format `NNN-<slug>`, where NNN continues from the highest existing ID in the queue (e.g., `001-setup-schema`, `002-auth-endpoint`). This numbering lets users see total task count at a glance.
13. Write the updated active queue into `.ark/feature_list.json` using the repository schema.
14. Refresh `.ark/agent-state.md` when the queue shape or next recommended read path has materially changed.
15. Summarize the selected mode, what was moved into `final_feature_list.json`, the generated task groups, major assumptions, and any risks.

## Skill boundaries

Use `$Task_init` to create or rewrite the active executable queue.
Do not use `$Task_init` to:
* execute the queued tasks (use `$Auto_dev`),
* compress the repository memory layer (use `$Context_archive`).

## Task quality bar

Each generated task must satisfy all of the following:
* write all `description` and `steps` text in English,
* one task equals one coherent developer session — a meaningful, independently runnable feature slice,
* each task must complete something the user or API can observe and verify,
* every task includes `task_type`, a sequential `task_id`, and `budget_minutes`,
* tasks are ordered by dependency and business flow,
* `description` states a user-visible or business-visible result,
* `steps` are observable and verifiable from the most realistic entry point available,
* no placeholders, TODO items, or vague wording,
* all new or rewritten tasks start with `"passes": false`.

## Granularity rules

Size tasks so each one represents a meaningful, self-contained unit of work that a developer would complete in one focused session. Prefer larger, coherent slices over many tiny steps.

Use these rules:
* one task should cover a complete feature behavior at one layer — the full CRUD for a resource, one page with its core interactions, or one API flow from request to response,
* prefer vertical slices that connect data, logic, and UI/API surface end-to-end within one session,
* only split when the task would require touching genuinely independent capabilities: separate UI pages, separate unrelated endpoints, or a schema migration that must land before service logic can be written,
* do not split happy path from error handling unless the error handling is itself a distinct feature with separate validation steps,
* combine related create/read flows when they share the same context and can be validated together.

Hard boundaries:
* do not put multiple unrelated pages in one task,
* do not put unrelated endpoints in one task,
* do not put schema migration and dependent business logic in the same task when the migration must be verified before logic is written,
* do not create milestone-style tasks such as "complete user management module",
* do not create tasks whose only validation is "code exists".

## Typed task rules

Use these task types:
* `docs`: document shells, section scaffolds, small documentation fills
* `planning`: queue regeneration, work breakdowns, phase plans
* `frontend`: UI implementation, frontend state logic, component behavior, browser-visible changes
* `backend`: endpoint behavior, service logic, persistence logic, API contracts
* `e2e`: multi-layer flows that must cross frontend and backend together

Budget defaults:
* `docs`: 10
* `planning`: 10
* `frontend`: 15–20
* `backend`: 15–20
* `e2e`: 20–30

Budget policy:
* treat 20 minutes as the default target for `frontend` and `backend` tasks,
* allow up to 30 minutes for an `e2e` task that genuinely covers an end-to-end flow,
* `docs` and `planning` tasks should stay at 10 minutes,
* if a task would need more than 30 minutes, split it — but only along a natural capability boundary, not by technical layer.

Process rules:
* `docs` and `planning` tasks should be light enough to skip `.ark/init.sh`,
* `frontend`, `backend`, and `e2e` tasks should assume the full execution path including `.ark/init.sh`.

## Decomposition rules

* Prefer business-flow slices over technical-layer slices.
* Prefer "walking skeleton" order: first create the thinnest end-to-end path, then add depth, variants, error states, and polish.
* Put prerequisite infrastructure tasks before dependent feature tasks.
* A prerequisite task is allowed only when the next delivery slice cannot be implemented without it.
* Write the queue in English even if the input requirement is in another language.
* Prefer 3 to 5 validation steps per task. If significantly more are needed, the task may be too large.
* First derive the implementation map, then cut the map into tasks.
* Before finalizing, run a coverage check: every acceptance outcome from the requirement must map to at least one task.

Use this JSON shape:

```json
[
  {
    "task_id": "001-auth-schema",
    "task_type": "backend",
    "description": "Create the users table and session schema with all required fields.",
    "steps": [
      "Run the migration and confirm users table exists with correct columns.",
      "Confirm sessions table exists with user_id foreign key.",
      "Verify the migration is idempotent on a clean database."
    ],
    "budget_minutes": 15,
    "passes": false
  }
]
```

## Blockers

Stop and escalate instead of writing low-confidence tasks when:
* prerequisites are missing,
* the requirement is unclear, conflicting, or underspecified,
* the requested queue rewrite would overwrite completed history without explicit human approval,
* or the requested queue update mode is ambiguous.

When escalating, include:
* blocker category: `missing-prerequisite` or `requirement-unclear`,
* the missing or conflicting information,
* why it prevents safe task decomposition,
* the minimum clarification needed to continue.

## Memory health thresholds

Treat the memory layer as needing archive work when:
* `.ark/codex-progress.md` is roughly over 250 lines or 18 KB,
* `.ark/agent-state.md` is missing and the main log is no longer short,
* `.ark/agent-state.md` no longer matches the current queue shape or first pending task,
* or `AGENTS.md` has clearly drifted into repeated generic SOP.

Use `$Context_archive` before continuing normal planning when any threshold is met.
