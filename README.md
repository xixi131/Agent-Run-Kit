# Agent-Run-Kit

一套可复用的多代理自动开发工作流模板，兼容 Claude Code 和 Codex。

核心思路：用三个全局 skill 驱动一个文件级记忆层，让 AI 代理能在任意项目里自主拆任务、执行、验证、记录、提交，并根据验收标准决定是否继续迭代。

---

## 组成

```
global-skills/       ← 三个全局 skill，安装后全项目可用
  Auto_dev/          ← 任务调度、执行、验证、提交
  Task_init/         ← 需求拆分为可执行任务队列
  Context_archive/   ← 记忆层过长时压缩归档

project-template/    ← 复制到目标项目的记忆层模板
  AGENTS.md          ← 项目稳定事实、规则、文档路由
  .ark/
    project_goal.md  ← 执行目标、运行模式、验收标准
    feature_list.json
    agent-state.md
    init.sh
    rules/
    ...
```

---

## 安装

### 1. 全局 skills

把 `global-skills/` 下三个目录复制到 `~/.claude/skills/`（Claude Code）或 `~/.codex/skills/`（Codex）：

```
global-skills/Auto_dev
global-skills/Task_init
global-skills/Context_archive
```

### 2. 项目模板

把 `project-template/` 里的内容复制到目标项目根目录，然后修改：

- `AGENTS.md`：写项目摘要、核心规则、文档路由
- `.ark/init.sh`：改成项目真实的启动或验证命令
- `.ark/rules/*`：替换成项目自己的前端、后端、架构规范
- `.ark/project_goal.md`：填写需求、选择运行模式、写验收标准

---

## 三种运行模式

通过 `.ark/project_goal.md` 的 `## Mode` 字段控制，`$Auto_dev` 据此调整行为。

### workflow — 确定性流程

适合一次性操作：迁移、格式化、批量重命名等。

- worker 按步骤逐一执行，不探索范围外的代码
- worker 必须输出步骤完成块，parent 逐条核验：
  ```
  [✓] step 1: migration ran, users table exists
  [✓] step 2: sessions table exists
  [✗] step 3: idempotent rerun failed — error: table already exists
  ```
- 任务完成后直接停止，不检查验收标准，不重新规划

### agent — 单次推理执行

适合调查型任务：debug、fix、refactor、optimize。

- worker 必须先输出调查摘要再开始实现：
  ```
  [INVESTIGATION] read: auth/middleware.ts, sessions/store.ts | finding: token stored in localStorage, not httpOnly cookie
  ```
- 执行完成后做一次整体质量复查，报告差距后停止
- 不重新规划，不迭代

### loop — 验收驱动迭代

适合功能开发：implement、build、add feature。

- 每轮执行完成后，`$Auto_dev` 运行验收标准中的 shell 命令：
  ```
  - [ ] `curl -sf http://localhost:3000/api/health` exits 0
  - [ ] `npm test 2>&1 | grep "passing"` exits 0
  ```
- 标准全部通过 → 停止
- 未通过 → 写 Gap Analysis 到 `project_goal.md` → 调用 `$Task_init` 重新规划未完成任务 → 继续执行
- 同一标准连续失败 3 次 → 停止并上报

验收标准必须写成可执行的 shell 命令（exit 0 为通过），不接受"用户能登录"这类模糊描述。

---

## 使用流程

**第一步：填写目标**

在 `.ark/project_goal.md` 里写清楚需求、选好模式、写好验收标准（loop 模式必填）。

**第二步：拆任务**

```
$Task_init 根据需求拆成可执行任务
```

`$Task_init` 会：
- 把需求拆成有 `task_id`、`task_type`、`budget_minutes`、`steps` 的任务写入 `feature_list.json`
- 如果是 loop 模式且验收标准为空，会帮你起草可执行标准（需人工确认后再跑 `$Auto_dev`）
- 支持三种队列模式：`replace-active`、`rewrite-pending`、`append-phase`

**第三步：执行**

```
$Auto_dev 完成 1 个任务
```

稳定后可批量执行：

```
$Auto_dev 完成 3 个任务
```

`$Auto_dev` 会：
- 分析任务依赖关系，写入范围不冲突的任务并行执行，有依赖的顺序执行
- worker 只实现和返回验证证据，parent 统一更新记忆层文件并提交 commit
- loop 模式下自动检查验收标准，未通过则调用 `$Task_init` 重新规划并继续

**上下文过长时压缩：**

```
$Context_archive 压缩当前项目记忆层并刷新 agent-state.md
```

---

## 记忆层文件说明

| 文件 | 用途 |
|------|------|
| `AGENTS.md` | 项目稳定事实、核心规则、文档路由，代理启动时默认读取 |
| `.ark/project_goal.md` | 执行目标、运行模式（workflow/agent/loop）、验收标准 |
| `.ark/feature_list.json` | 当前 active 任务队列，`passes: false` 为待执行 |
| `.ark/final_feature_list.json` | 历史任务归档 |
| `.ark/agent-state.md` | 当前交接状态，代理启动优先读此文件 |
| `.ark/codex-progress.md` | 近期进度日志 |
| `.ark/codex-progress-archive.md` | 更早的详细历史，按需读取 |
| `.ark/lessons.json` | 已发现的非显而易见事实，下次派发前注入给 worker |
| `.ark/init.sh` | 项目启动或验证入口 |
| `.ark/rules/` | 分类规范文件，按任务类型按需读取 |

---

## AGENTS.md 写法建议

只放项目摘要、关键业务规则和文档路由，不要把所有规范堆进来。

详细规范拆到 `.ark/rules/`，在 `AGENTS.md` 的 Doc Routing 里注明"写什么类型的代码读哪个文件"。这样可以减少默认上下文，节省 token，让代理注意力更集中。
