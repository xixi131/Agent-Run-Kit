---
name: Task_init
description: Break a new product requirement into a very fine-grained, typed, ordered, executable feature_list.json queue. Use when the user asks to initialize, regenerate, decompose, or rewrite pending tasks from a requirement before running $Auto_dev. The generated tasks must be small and written in English.
---

# Task_init

Use this skill when the user wants Codex to turn a requirement into executable tasks in `feature_list.json`.

Do not implement product code in this turn. This skill is for planning and queue initialization only.

## Required context
Read the smallest reliable planning context first:
* `AGENTS.md`
* `agent-state.md` if it exists
* `feature_list.json`
* `final_feature_list.json` if it exists

Read [../../../project_DS/workflows/task_init_loop.md](../../../project_DS/workflows/task_init_loop.md) for the detailed planning contract.

Read [references/prompt-patterns.md](references/prompt-patterns.md) when you need ready-to-use prompt examples.

Use conditional reading for everything else:
* read `codex-progress.md` only if `agent-state.md` is missing, stale, or insufficient,
* read `codex-progress-archive.md` only if older planning or migration history is actually needed,
* read `project_DS/` only for the docs directly relevant to the requirement.

## Planning workflow
1. Read the incoming requirement carefully and identify the target business outcome.
2. Run a memory-layer health check before planning:
   * if `codex-progress.md` is too long for default startup,
   * or `agent-state.md` is missing or clearly stale,
   * or `AGENTS.md` has drifted into duplicated generic SOP instead of lean project facts,
   * stop normal planning and use `$Context_archive` first, then resume planning.
3. Read the current `feature_list.json` and `final_feature_list.json` if it exists.
4. Preserve the old active queue before writing a new one:
   * if `final_feature_list.json` does not exist, create it as an empty JSON array,
   * append every valid task object from the current `feature_list.json` to `final_feature_list.json`,
   * preserve each task's existing `passes` state and fields,
   * then clear `feature_list.json` to an empty array before writing the newly planned queue.
5. Load only the relevant docs from `project_DS/` for the current requirement. Do not scan every doc by default.
6. Read `codex-progress.md` only if the short handoff is not enough for safe planning.
7. Before writing any task, build a requirement fulfillment map:
   * name each user-visible capability or acceptance outcome in the requirement,
   * identify the smallest coherent runnable slice that proves progress toward that outcome,
   * include all layers needed for that slice to work, even if that means making the task `e2e`,
   * defer low-value plumbing-only work unless it is the next prerequisite for a runnable slice,
   * avoid tasks that merely prepare code but leave no observable demand-side behavior.
8. Then reason about the likely implementation path in this repository:
   * the target user-visible outcome,
   * the likely modules, files, and layers involved,
   * the dependency order,
   * the validation path,
   * and which parts can be completed independently.
9. Classify each generated task as `docs`, `planning`, `frontend`, `backend`, or `e2e`.
10. Evaluate task complexity and assign `budget_minutes` to every task.
11. Decompose the implementation path into ordered, executable delivery slices.
12. Write only the newly planned queue into `feature_list.json` using the repository schema.
13. Refresh `agent-state.md` when the queue shape or next recommended read path has materially changed.
14. Summarize what was moved into `final_feature_list.json`, the generated task groups, major assumptions, and any risks.

## Skill boundaries
Use `$Task_init` when you need to create or rewrite the active executable queue in `feature_list.json`.
Do not use `$Task_init` to:
* execute the queued tasks,
* validate feature behavior through the full runtime path,
* or compress/archive the repository memory layer.

Hand off instead:
* use `$Auto_dev` when the queue is ready and you want to execute pending tasks,
* use `$Context_archive` when the memory layer is oversized, stale, or expensive to reread at startup.

## Task quality bar
Each generated task must satisfy all of the following:
* write all `description` and `steps` text in English,
* one task equals one very small independently executable outcome,
* each implementation task must complete a runnable, testable slice of the requirement, not only a disconnected technical prerequisite,
* every task includes `task_type`,
* every task includes `budget_minutes`,
* tasks are ordered by dependency and business flow,
* `description` states a user-visible or business-visible result,
* `steps` are observable and verifiable,
* frontend or end-to-end tasks include browser-verifiable steps,
* backend tasks include API-request-verifiable steps,
* data-writing tasks include persisted-result verification when needed,
* no placeholders, TODO items, or vague wording,
* default to tasks that can be completed within 10 minutes,
* base the split on the implementation path, not only on requirement wording,
* each task's steps prove that the slice works from the most realistic user/API entry point available,
* all new or rewritten tasks start with `"passes": false`.

## Granularity rules
Default to over-splitting. If a task feels acceptable at medium size, split it again.

Use these rules:
* one task should usually fit in one focused implementation cycle and one focused validation cycle,
* prefer tasks that a worker can finish with one small commit,
* prefer vertical slices that connect the minimum necessary data, behavior, and UI/API surface,
* if you estimate a task would take more than 10 minutes, split it again before writing it,
* reason about how the feature will actually be built before you decide task boundaries,
* split list, detail, create, edit, delete, validation, and polish into separate tasks when possible,
* split backend contract work from frontend integration work unless they are inseparable,
* when splitting backend and frontend is necessary, make the backend task expose and verify a real API behavior, and make the frontend task consume a real or locally stubbed contract that already exists,
* split data migration or schema work from API behavior work,
* split error handling and edge cases from the happy path when possible,
* if a task would require touching many files, many pages, or many endpoints, it is probably too large.

Hard boundaries:
* do not put multiple pages in one task,
* do not put multiple endpoints in one task unless they are the same tiny flow,
* do not put create and edit in one task,
* do not put backend implementation and end-to-end UI verification in the same task unless the change is extremely small,
* do not create milestone-style tasks such as "complete user management module",
* do not create tasks whose only validation is "code exists" unless the requested output is documentation, planning, or scaffolding,
* for docs tasks, split "create shell" and "fill content" into separate tasks,
* for docs tasks, split heading creation from behavior documentation when possible,
* if a task would need both runtime investigation and documentation write-up, split those into separate tasks when possible,
* if a task would need both tracing and implementation, split those into separate tasks when possible,
* avoid research-heavy phrases such as "source of truth" in task descriptions unless the task is explicitly a research task.

## Typed task rules
Use these task types:
* `docs`: document shells, section scaffolds, small documentation fills, docs-only cleanup
* `planning`: queue regeneration, work breakdowns, phase plans, task reshaping
* `frontend`: UI implementation, frontend state logic, component behavior, browser-visible changes
* `backend`: endpoint behavior, service logic, persistence logic, API contracts
* `e2e`: multi-layer flows that must cross frontend and backend together

Budget defaults:
* `docs`: `5`
* `planning`: `5`
* `frontend`: `8` to `10`
* `backend`: `8` to `10`
* `e2e`: `10`

Budget policy:
* treat 10 minutes as the default maximum budget for any generated task,
* use `5` for `docs` and `planning` unless there is a strong reason not to,
* use `8` to `10` for most `frontend` and `backend` tasks,
* use `10` for most `e2e` tasks by splitting setup, happy path, fallback path, and documentation into separate tasks,
* if you think a task needs more than `10`, first try to split it,
* only allow `15` for an exceptional task that truly cannot be split without losing coherence,
* do not emit `20`, `25`, or `30` minute tasks in normal planning.

Process rules:
* `docs` and `planning` tasks should be light enough to skip `init.sh`
* `frontend`, `backend`, and `e2e` tasks should assume the full execution path
* if a supposed `docs` task would require runtime verification, reclassify it or split it further
* think through the likely implementation layers before assigning task type

## Decomposition rules
* Prefer business-flow slices over technical-layer slices.
* Prefer "walking skeleton" order: first create the thinnest end-to-end path that proves the requirement can work, then add depth, variants, error states, and polish.
* Keep each task small enough for a worker to finish in one focused implementation cycle.
* Put prerequisite infrastructure tasks before dependent feature tasks.
* A prerequisite task is allowed only when the next delivery slice cannot be implemented without it; its validation must still prove usable behavior such as a real API response, generated file, visible route, or executable command.
* If the requirement is large, generate only the next coherent phase instead of padding the queue with low-confidence items.
* Avoid task descriptions such as "add API", "create table", or "refactor module" unless the user explicitly asked for an infrastructure-only change.
* Write the queue in English even if the input requirement is in another language.
* Prefer 3 to 5 validation steps per task. If more are needed, the task may be too large.
* If a task description naturally contains "and", check whether it should be split into two tasks.
* When in doubt, split the task further.
* For docs tasks, prefer verbs like `Create`, `Add`, `Rename`, `Move`, or `Check`, not exploratory phrases like `Establish the source of truth`.
* Treat any estimate above 10 minutes as a signal that the task is still too large.
* For mixed investigation-plus-writeup work, prefer two tasks: one for observation or tracing, one for documenting the result.
* First derive the implementation map, then cut the map into tasks. Do not skip the implementation-thinking step.
* Before finalizing, run a coverage check: every acceptance outcome from the requirement must map to at least one task, and every task must map back to an acceptance outcome or an unavoidable prerequisite.

Use this JSON shape:

```json
[
  {
    "task_type": "docs",
    "description": "Create an empty baseline document shell.",
    "steps": [
      "Create docs/example.md with the required top-level headings.",
      "Add a one-sentence scope note at the top of the file.",
      "Check that headings are unique and the file opens from repository root."
    ],
    "budget_minutes": 5,
    "passes": false
  }
]
```

## Blockers
Stop and escalate instead of writing low-confidence tasks when:
* prerequisites are missing,
* the requirement is unclear, conflicting, or underspecified,
* the requested queue rewrite would overwrite completed history without explicit human approval.

When escalating, include:
* blocker category: `missing-prerequisite` or `requirement-unclear`,
* the missing or conflicting information,
* why it prevents safe task decomposition,
* the minimum clarification needed to continue.

## Usage hints
Good requests look like:
* `$Task_init Break the requirement into 20 very small typed tasks and write them into feature_list.json`
* `$Task_init Re-plan feature_list.json from the PRD, but only rewrite unfinished typed tasks`
* `$Task_init Append 8 very small typed tasks for the next phase and keep completed items`

## Memory health thresholds
Treat the memory layer as needing archive/refresh work when one or more of these is true:
* `codex-progress.md` is roughly over `250` lines or over `18 KB`,
* `agent-state.md` is missing and the main log is no longer short,
* `agent-state.md` no longer matches the current queue shape or first pending task,
* or `AGENTS.md` has clearly drifted into repeated generic SOP instead of lean project facts.

In those cases, use `$Context_archive` before continuing normal planning.
