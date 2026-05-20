---
description: 父子 Agent 协作模式：读取 feature_list.json 状态机，循环执行开发、验证、日志更新与提交，直到达到目标任务数或无待办项。
---

# 自动开发工作流

## 人类使用说明

### 这份文档是做什么的

这是一份项目内的多智能体自动开发流程说明。它主要是给人类维护者看清楚这套系统怎么运转，同时也为 `AGENTS.md` 提供一个可引用的详细流程文件。

### 目录职责

- `AGENTS.md` 负责 Codex 默认加载的强约束。
- `feature_list.json` 负责任务状态机。
- `codex-progress.md` 负责人类与 agent 共用的工作日志。
- `init.sh` 负责环境初始化和启动安全线。
- `global-skills/Auto_dev` 负责触发这套自动开发系统。
- `project_DS/workflows/auto_dev_loop.md` 负责解释整套流程。

### 人类如何使用

1. 如果是新需求，先用 `$Task_init` 把需求拆成 `feature_list.json` 任务队列。
2. 再维护 `codex-progress.md`，保留最近的重要上下文。
3. 在仓库里用 `$Auto_dev 完成 1 个任务` 或 `$Auto_dev 完成 2 个任务` 触发父代理。
4. 父代理会读取状态机，派发子代理处理第一个 `passes: false` 的任务。
5. 子代理完成后会返回验证证据和变更清单；父代理更新状态、写日志并提交 commit。
6. 如果失败超过阈值，系统会停止并请求人工介入。

### 人类需要重点维护什么

- `AGENTS.md`：全局规则是否准确。
- `feature_list.json`：任务描述和验收步骤是否可执行。
- `codex-progress.md`：上下文日志是否真实、简洁、可追溯。
- `init.sh`：环境是否能被一键拉起。

## Agent Contract

### Core Roles
1. **Supervisor (Parent Agent)**: task dispatch, state-machine validation, acceptance, and progress reporting.
2. **Worker (Child Agent)**: targeted implementation, validation, and evidence reporting.

### Canonical Coordination Files
* `AGENTS.md`: default-loaded project constitution and worker SOP.
* `feature_list.json`: task state machine. Dispatch only items with `"passes": false`; every task should include a stable `task_id`.
* `codex-progress.md`: shared work log. The parent appends one entry per accepted task.
* `init.sh`: environment initialization entrypoint before validation.

### Supervisor Loop
1. Parse the user's request and determine the required number of tasks to finish.
2. Read `feature_list.json` from top to bottom.
3. Select the first item where `"passes": false`.
4. If no pending item exists, stop and report that the queue is empty.
5. If the queue is placeholder-only, not executable, or stale for the current requirement, stop and ask the human to run the planning flow first.
6. Dispatch a worker with the selected `task_id` and task only, together with its validation steps and the escalation contract. Do not broaden the scope.
7. Wait for the worker result.
8. Verify the worker result:
   * the worker reports completed validation for every listed step,
   * the worker reports the concrete verification path used for the task, such as browser MCP, API requests, and database checks when applicable,
   * and the worker changed only files inside the assigned task scope.
9. If the worker reports any escalation, stop immediately and surface the blocker to the human.
10. If worker-result verification fails, stop and surface the mismatch to the human.
11. If worker-result verification succeeds, the parent updates shared coordination files:
   * set the assigned `task_id` in `feature_list.json` to `"passes": true`,
   * append a matching entry to `codex-progress.md`,
   * and refresh `agent-state.md` when the first pending task or recommended read path changes.
12. Verify the updated coordination files, create the focused commit, decrement the remaining task count, and continue until the requested number is complete.

### Worker Loop
1. Read `AGENTS.md` and obey the repository rules before touching code.
2. Run `init.sh`. If the environment cannot be brought up safely, stop and escalate.
3. Read the assigned item from `feature_list.json`.
4. Recover only the needed context from `codex-progress.md`, focused source files, or recent Git history.
5. Implement the smallest change set that satisfies the assigned `steps`.
6. Validate every step in the task definition using the appropriate toolchain:
   * browser MCP navigation and interaction for page-level or end-to-end checks,
   * real API requests for backend endpoint checks,
   * targeted build or test commands for code-level confidence.
7. When the task changes persisted data or computed settlement results, inspect the resulting database-side state when needed to confirm the flow completed correctly.
8. If validation fails, debug through the minimum necessary chain:
   * browser/UI,
   * API request and response,
   * backend logs, code path, and service logic,
   * database state or derived records.
9. Self-repair at most 3 times for the same failing symptom. If the same blocker remains after the third attempt, stop and escalate instead of continuing.
10. Only after all validation passes, return validation evidence, changed files, and a concise progress-log draft to the supervisor.
11. Do not mutate `feature_list.json`, `agent-state.md`, or `codex-progress.md` unless the assigned task is explicitly about those files.
12. Do not run `git add`, `git commit`, or other Git post-processing commands.
13. Return control to the supervisor.

### Human-in-the-Loop Triggers
Stop the loop and ask for human input when:
* validation still fails after 3 self-repair attempts,
* the task depends on missing prerequisites,
* the task's requirement or acceptance criteria is ambiguous,
* or `init.sh` exposes an environment failure that cannot be recovered safely.

The escalation report must include:
* blocker category,
* current error,
* attempted fixes and repair-attempt count,
* verification methods already used,
* impacted files.
