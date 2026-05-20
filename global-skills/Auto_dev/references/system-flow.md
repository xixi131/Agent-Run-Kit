# Auto Dev System Flow

## Purpose
This repository uses a Codex-oriented multi-agent workflow built around a layered memory system:
* `AGENTS.md`
* `agent-state.md`
* `feature_list.json`
* `codex-progress.md`
* `codex-progress-archive.md`
* `init.sh`

Together they let a freshly started worker recover the project state without relying on a repeated user prompt.

Codex Memories may also provide useful recalled context from previous threads. Treat memories as a local acceleration layer for stable conventions and known pitfalls, not as the authority for current task state.

## File responsibilities
* `AGENTS.md`: default-loaded project summary, architectural constraints, worker SOP, and escalation rules.
* `agent-state.md`: short current handoff containing phase, first pending task, recommended next reads, and active blockers worth surfacing.
* `feature_list.json`: ordered task queue and state machine. The first item with `"passes": false` is the next dispatch target. Every task should include `task_id`, `task_type`, and `budget_minutes`.
* `codex-progress.md`: current summary plus recent high-signal entries for default startup. The parent writes accepted-task entries.
* `codex-progress-archive.md`: older detailed history, read only on demand.
* `init.sh`: environment bootstrap and safety check before validation.

## Execution flow
1. A human invokes `$Auto_dev` with a target task count, for example `$Auto_dev 完成 2 个任务`.
2. If `feature_list.json` is empty, placeholder-only, or stale for the current requirement, the human first invokes `$Task_init` to regenerate the queue.
3. The parent agent reads the minimal startup set first: `AGENTS.md`, `agent-state.md` if present, and `feature_list.json`.
4. Before dispatch, the parent agent checks memory health. If the memory layer is oversized or stale, it runs `$Context_archive` first and then resumes the execution loop.
5. The parent agent reads `feature_list.json` and selects pending items up to the requested task count.
6. The parent agent reads `task_type` and `budget_minutes` before dispatch.
7. When more than one task is requested, the parent agent builds a dependency plan before dispatch.
8. Independent tasks with disjoint write scopes can run in parallel. Dependent tasks or tasks with overlapping write scopes run sequentially by dependency layer.
9. `docs` and `planning` tasks use a lightweight fast path with a hard timeout. `frontend`, `backend`, and `e2e` tasks use the full execution path.
10. The parent agent dispatches one worker per task in the current dependency layer, passing each worker only its `task_id`, task, typed execution contract, validation steps, expected write scope when inferable, and escalation contract.
11. Workers must start from the same minimal set: `AGENTS.md`, `agent-state.md` if present, and the assigned task in `feature_list.json`.
12. Workers read `codex-progress.md`, `codex-progress-archive.md`, `project_DS`, and other repository files only when the task actually needs more context.
13. For a pure `docs` or `planning` task, the worker skips heavy startup and only performs lightweight validation such as file existence, section structure, and path discoverability.
14. For a `docs` or `planning` task, the parent agent must reclaim the worker as soon as `budget_minutes` is reached. It does not wait for natural completion.
15. For `frontend`, `backend`, and `e2e` tasks, the worker reads only the minimum additional local context, runs `init.sh`, implements the task, validates each declared step through the real execution path, and self-repairs at most 3 times for the same symptom.
16. Real execution-path validation means:
   * browser MCP for user-visible and end-to-end flows,
   * API request tools for backend endpoints,
   * database verification when persisted state matters.
17. If a `docs` or `planning` task exceeds budget or requires the heavy path to finish, the worker escalates `task-process-mismatch` and the parent agent stops the loop.
18. After validation passes, the worker returns validation evidence, changed files, and a concise progress-log draft.
19. The parent agent updates and reconciles shared memory files after each dependency layer: mark accepted `task_id` values as passing, refresh `agent-state.md` when needed, and append matching records to `codex-progress.md`.
20. The parent agent handles Git post-processing after acceptance and either dispatches the next dependency layer or stops with a summary.

## Parallel dispatch
Parallel execution is one of the advantages of this system when the task queue is well decomposed.
* Run tasks in parallel only when they have no producer-consumer relationship and are unlikely to touch the same files.
* Run tasks sequentially when one task creates an API, schema, route, shared component, data contract, or document section another task depends on.
* Tell parallel workers that they are not alone in the codebase and must not revert edits made by others.
* Each worker owns exactly one `task_id` and does not mutate shared coordination files unless explicitly assigned to do so.
* The parent reports whether dispatch was parallel or sequential and why.

## Memory-aware context use
* Memories can replace repeated rediscovery of stable facts such as project conventions, recurring commands, module shape, and known pitfalls.
* Memories cannot replace reading `feature_list.json` for queue state or `agent-state.md` for current handoff.
* If memories answer a context question, avoid broad log/doc reads and proceed with the task-local files.
* If memories conflict with checked-in files, trust checked-in files.
* Keep `agent-state.md` and `codex-progress.md` concise after each task so memory generation has clean evidence and future agents have a short fallback path.

## Git post-processing
* Local Git operations such as status, diff, add, commit, and log may run normally unless sandboxing blocks repository metadata writes.
* Remote Git operations must use escalated permissions immediately, especially `git fetch`, `git pull`, and `git push`.
* Do not first run remote Git commands in the restricted sandbox just to observe failure. Use escalation up front because remote operations commonly need network and credential access.
* Prefer narrow escalation prefixes such as `["git", "fetch"]`, `["git", "pull"]`, or `["git", "push"]`.
* If an escalated remote Git operation fails because of authentication, branch protection, conflicts, or network outage, stop and report `post-processing-blocked` with the command, error, and whether the task content is already complete.
