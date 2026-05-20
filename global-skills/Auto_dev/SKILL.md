---
name: Auto_dev
description: Coordinate a parent-child Codex development loop for this repository. Use when the user asks $Auto_dev to complete one or more tasks from feature_list.json, dispatch a worker for the first pending item, apply the correct execution path by task type, verify feature_list.json and codex-progress.md were updated, and stop on any human-in-the-loop trigger.
---

# Auto_dev

Use this skill when the user wants the repository's multi-agent automation loop rather than a one-off manual coding task.

If the current `feature_list.json` is still placeholder-based, empty, or does not match the user's latest requirement, stop and use `$Task_init` first.

## Required context
Use Codex Memories as an optional recall layer when they are available, but keep repository files as the authority for task state and required rules.

Read the smallest reliable startup context first:
* `AGENTS.md`
* `agent-state.md` if it exists
* `feature_list.json`

Read [references/system-flow.md](references/system-flow.md) only if you need the full execution contract or reporting format.

Use conditional reading for everything else:
* read `codex-progress.md` only if `agent-state.md` is missing, stale, or insufficient for the assigned task,
* read `codex-progress-archive.md` only when you explicitly need older history or audit detail,
* read `project_DS/` only for the task-routed document you actually need,
* read `init.sh` only when the task type needs runtime startup or runtime verification.

## Memory-aware startup policy
Codex Memories can reduce repeated context recovery, but they are not the source of truth.
* Use injected memories for stable project conventions, recurring workflows, known pitfalls, preferred commands, and project shape hints.
* Always verify volatile state from files: current queue state in `feature_list.json`, current handoff in `agent-state.md`, recent task updates when needed, current code, and Git status.
* Do not reread `codex-progress.md`, `codex-progress-archive.md`, broad `project_DS/` docs, or old diffs just because they exist. Read them only when the memory layer and `agent-state.md` do not answer the task-local question.
* If a memory conflicts with checked-in files, trust the checked-in file and mention the conflict briefly in the report.
* Do not rely on memories for secrets, credentials, exact current branch state, or whether a task has `passes: true`.
* When finishing accepted work, keep `agent-state.md` and `codex-progress.md` concise and memory-friendly so future memory extraction captures stable lessons without forcing future agents to reread long logs.

## Parent agent workflow
1. Parse how many tasks the user wants completed. If omitted, default to `1`.
2. Run a memory-layer health check before dispatch:
   * if `codex-progress.md` is too long for default startup,
   * or `agent-state.md` is missing or clearly stale,
   * or `AGENTS.md` has drifted into duplicated generic SOP instead of lean project facts,
   * stop normal execution and use `$Context_archive` first, then resume the loop.
3. Read `feature_list.json` top to bottom and choose the first item with `"passes": false`; record its stable `task_id`.
4. If there is no pending task, stop and report that the queue is empty.
5. If the queue is placeholder-only, not executable, or clearly stale versus the user's new requirement, stop and tell the human to run `$Task_init` first.
6. Read the task's `task_id`, `task_type`, and `budget_minutes` before dispatch:
   * `docs` and `planning` are lightweight fast-path tasks,
   * `frontend`, `backend`, and `e2e` are full execution-path tasks.
7. If `task_type` is missing, treat the queue as stale and send the human to `$Task_init` to regenerate it with typed tasks.
8. If the user requested more than one task, inspect the next pending tasks up to the requested count and build a dependency plan before dispatch:
   * tasks are dependent when one produces files, APIs, schemas, state, data, docs, or UI surfaces that another task consumes,
   * tasks are dependent when their steps imply ordering, such as backend contract before frontend integration, schema before service behavior, or route before browser verification,
   * tasks are not safe to parallelize when likely write scopes overlap or when both need broad refactors in the same module,
   * tasks may run in parallel when they have independent acceptance outcomes, disjoint write scopes, and no producer-consumer relationship.
9. Dispatch the first dependency layer:
   * dispatch one worker for a single task when the next task blocks all others,
   * dispatch multiple workers in parallel when tasks in the current layer are independent,
   * keep ownership narrow and tell every worker they are not alone in the codebase, must not revert others' edits, and must stay inside their assigned responsibility.
10. For each dispatched task, pass only the `task_id`, task description, `task_type`, `budget_minutes`, `steps`, expected write scope when inferable, and the repository escalation contract.
11. For a `docs` or `planning` task, start a hard timeout equal to `budget_minutes`. When the budget is reached, immediately reclaim the worker result. Do not wait for natural completion.
12. Wait for the current dependency layer to finish before dispatching tasks that depend on it.
13. If a `docs` or `planning` task exceeds its budget, or clearly requires the heavy development path to finish, stop and escalate with blocker category `task-process-mismatch`.
14. If any worker reports an escalation, stop immediately. Do not dispatch the next task until the human resolves the blocker.
15. Accept each worker result only if all of the following are true:
   * the worker reports validation against every listed step,
   * the worker reports the concrete verification path used for the task,
   * the changed files stay inside the task-scoped write responsibility,
   * and the worker did not mutate shared coordination files unless explicitly assigned to do so.
16. Parent performs all shared state updates for accepted tasks in the dependency layer:
   * set each accepted `task_id` in `feature_list.json` to `"passes": true`,
   * refresh `agent-state.md` when the first pending task or startup read path changes,
   * append one fresh matching log entry per accepted task to `codex-progress.md`.
17. Parent verifies acceptance after the shared state update:
   * every accepted `task_id` is now marked `"passes": true`,
   * `codex-progress.md` contains a fresh matching log entry for every accepted task,
   * and `agent-state.md` still matches the first pending task when it exists.
18. Parent performs all Git post-processing for accepted tasks: stage the task-scoped files plus the parent-updated coordination files and create one focused commit per accepted task, or one focused batch commit only when parallel tasks are tightly related and conflict-free.
19. If parent-side commit fails, retry at most 3 times (request elevated permissions if sandbox blocks `.git/index.lock`).
20. Run any requested or required remote Git operation through escalated permissions from the start, especially `git fetch`, `git pull`, and `git push`.
21. If the third parent-side commit attempt fails, or a remote Git operation fails after the allowed escalated attempt, stop immediately and escalate as `post-processing-blocked`.
22. Continue by dependency layer until the requested number of tasks is complete, or stop early on any escalation.

## Skill boundaries
Use `$Auto_dev` when the queue already exists and you want to execute one or more pending tasks.
Do not use `$Auto_dev` to:
* create or rewrite the queue from a new requirement,
* compress or archive repository memory files,
* or perform broad project-memory maintenance unrelated to the selected task.

Hand off instead:
* use `$Task_init` when the queue is stale, missing, or needs to be replanned,
* use `$Context_archive` when the memory layer is oversized, stale, or expensive to reread at startup.

## Task type contract
Every task in `feature_list.json` must declare:
* `task_id`: a stable unique identifier that does not change when tasks are reordered
* `task_type`: one of `docs`, `planning`, `frontend`, `backend`, or `e2e`
* `budget_minutes`: the expected maximum execution time for the worker

Default budget guidance:
* `docs`: `5`
* `planning`: `5`
* `frontend`: `15` to `25`
* `backend`: `15` to `25`
* `e2e`: `20` to `35`

## Parallel dispatch policy
When the user asks `$Auto_dev` to complete multiple tasks, parallelism is preferred only after dependency analysis.
* Build a small dependency plan from the next pending tasks before dispatch.
* Parallelize independent tasks with disjoint write scopes, for example separate docs pages, separate UI pages, or unrelated backend endpoints.
* Sequence dependent tasks, for example schema before API, API before frontend integration, parser before UI display, route before browser verification, or shared component before page usage.
* Sequence tasks when likely file ownership overlaps, even if the descriptions look independent.
* Never let parallel workers mutate `feature_list.json`, `agent-state.md`, or `codex-progress.md`; each worker owns exactly one assigned `task_id` and returns evidence to the parent.
* The parent must update and reconcile `feature_list.json`, `agent-state.md`, and `codex-progress.md` after the layer finishes.
* Report whether the run used parallel or sequential dispatch, and why.

## Git permissions policy
Local Git operations and remote Git operations use different permission assumptions:
* Local operations such as `git status`, `git diff`, `git add`, `git commit`, and `git log` may run normally unless sandboxing blocks repository metadata writes.
* Remote operations must be run with escalated permissions immediately because they may need network and credential access. This includes `git fetch`, `git pull`, `git push`, and commands that implicitly contact a remote such as `git ls-remote` or `git submodule update --remote`.
* Do not first run remote Git commands in the restricted sandbox just to observe failure. Request/use escalation up front with a clear justification tied to the remote operation.
* Prefer narrow escalation prefix rules for the specific remote Git command family, for example `["git", "push"]`, `["git", "fetch"]`, or `["git", "pull"]`.
* Never use escalation to bypass destructive Git safety. Commands such as `git reset --hard`, force pushes, branch deletion, or checkout/revert of user changes still require explicit human instruction and careful reporting.
* If a remote Git operation fails under escalated permissions because of authentication, branch protection, conflicts, or network outage, stop and report `post-processing-blocked` with the exact command, error, and whether task content is already complete.

## Worker contract
The worker must choose the process that matches `task_type`:

### Lightweight fast path
Use this path for `docs` and `planning` tasks:
1. Get memory from `AGENTS.md`.
2. Read `agent-state.md` if it exists, then read the assigned task in `feature_list.json`.
3. Recover only the minimum extra context needed for the document or planning artifact.
4. Skip `codex-progress.md` unless `agent-state.md` and the task entry are not enough.
5. Skip `init.sh` unless the task explicitly depends on generated runtime output.
6. Implement only the assigned task.
7. Validate with lightweight checks only:
   * file exists,
   * headings or sections exist,
   * file path is discoverable,
   * basic structure check passes.
8. Do not launch browser MCP, API checks, or heavy environment startup for a pure docs/planning task.
9. If the task starts requiring code archaeology, runtime behavior confirmation, or cross-layer debugging, read only the minimum extra file needed. If it clearly requires the heavy path, stop and escalate as `task-process-mismatch`.
10. Only after all validation passes, return the validation evidence, changed file list, and a concise progress-log draft for the parent to write.
11. Do not run `git add`, `git commit`, or other Git post-processing commands.
12. Return the changed file list and a suggested focused commit message for the parent.

### Full execution path
Use this path for `frontend`, `backend`, and `e2e` tasks:
1. Get memory from `AGENTS.md`.
2. Read `agent-state.md` if it exists, then read the assigned task in `feature_list.json`.
3. Recover the minimum required extra context. Read `codex-progress.md` only if the short handoff is not enough.
4. Read only the task-routed project docs or code files needed for the current task.
5. Run `init.sh`.
6. Implement only the assigned task.
7. Validate every declared step with the real execution path that matches the task:
   * browser MCP for user-visible and end-to-end flows,
   * API request tools for backend endpoint behavior,
   * database verification when the task writes or derives persisted data.
8. If validation fails, debug across the minimum necessary chain: browser/UI -> API -> backend -> database.
9. Self-repair at most 3 times for the same failing symptom.
10. Read `codex-progress-archive.md` only if older historical context is truly needed to resolve the blocker.
11. Only after all validation passes, return the validation evidence, changed file list, and a concise progress-log draft for the parent to write.
12. Do not run `git add`, `git commit`, or other Git post-processing commands.
13. Return the changed file list and a suggested focused commit message for the parent.

## Escalation rules
Stop the automation loop and ask the human for help when:
* validation still fails after 3 repair attempts for the same symptom,
* prerequisites are missing,
* requirements are unclear,
* the task type and the required execution path do not match,
* parent-side Git post-processing still fails after 3 commit attempts,
* or `init.sh` reveals an environment failure that cannot be safely recovered.

When escalating, include:
* blocker category: `repair-loop-exceeded`, `missing-prerequisite`, `requirement-unclear`, `task-process-mismatch`, `post-processing-blocked`, or `environment-collapse`,
* current error or failing symptom,
* attempted fixes and repair-attempt count,
* verification methods already used, such as browser MCP, API requests, backend logs, or database checks,
* task type, budget, and elapsed time if budget was exceeded,
* whether content delivery is already complete and only commit is blocked,
* impacted files or modules.

## Degraded mode
If sub-agent tooling is unavailable, run the same loop locally as a single agent and clearly report that the system operated in degraded single-agent mode.

## Memory health thresholds
Treat the memory layer as needing archive/refresh work when one or more of these is true:
* `codex-progress.md` is roughly over `250` lines or over `18 KB`,
* `agent-state.md` is missing and the main log is no longer short,
* `agent-state.md` does not match the current first pending task,
* or `AGENTS.md` has clearly drifted into repeated generic SOP instead of lean project facts.

In those cases, use `$Context_archive` before continuing normal execution.
