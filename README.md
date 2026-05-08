# Agent-Run-Kit

这是一套可复用的 Codex 自动开发工作流模板，主要由两部分组成：

- `global-skills/`：三个全局 skills，复制到 `~/.codex/skills/` 使用。
- `project-template/`：项目级记忆层模板，复制到目标项目根目录使用。

## 安装全局 skills

把下面三个目录复制到对方电脑的 `~/.codex/skills/`：

```text
global-skills/Auto_dev
global-skills/Task_init
global-skills/Context_archive
```

它们分别负责：

- `$Task_init`：把需求按阶段拆成可执行任务。
- `$Auto_dev`：按任务队列调度子代理执行、验证、记录、提交。
- `$Context_archive`：上下文变长时，压缩记忆层并保留历史归档。

## 安装项目模板

把 `project-template/` 里的内容复制到目标项目根目录。

复制后重点改这几处：

- `AGENTS.md`：写项目摘要、核心规则、文档路由。
- `init.sh`：改成这个项目真实的启动或验证命令。
- `project_DS/specification/*`：替换成项目自己的前端、UI、后端、架构规范。
- `feature_list.json`：保持空数组，后续交给 `$Task_init` 生成当前任务队列。
- `final_feature_list.json`：保持空数组，`$Task_init` 会把旧队列追加到这里。

## 推荐使用流程

先让 AI 根据需求写一个阶段计划。

然后用 `$Task_init` 按阶段拆任务：

```text
$Task_init 根据第一阶段计划拆成可执行任务
```

再用 `$Auto_dev` 执行任务：

```text
$Auto_dev 完成 1 个任务
```

稳定后可以一次执行多个任务：

```text
$Auto_dev 完成 3 个任务
```

`$Auto_dev` 会先判断任务之间有没有依赖关系。没有依赖、写入范围不冲突的任务会并行派发；有依赖的任务会按顺序执行。

上下文变长时，用：

```text
$Context_archive 压缩当前项目记忆层并刷新 agent-state.md
```

## 记忆层文件

- `AGENTS.md`：项目稳定事实、核心规则、按需读文档的路由。
- `feature_list.json`：当前 active 任务队列。
- `final_feature_list.json`：历史任务队列归档，由 `$Task_init` 追加写入。
- `agent-state.md`：当前交接状态。
- `codex-progress.md`：近期进度日志。
- `codex-progress-archive.md`：更早的详细历史。
- `init.sh`：项目启动或验证入口。

## 一个建议

`AGENTS.md` 不要写太长。

推荐只放项目摘要、关键业务规则和文档路由。详细规范拆到 `project_DS/specification/`，然后在 `AGENTS.md` 里告诉代理什么时候读取哪个文件。

这样可以减少默认上下文，节省 token，也能让代理启动更快、注意力更集中。
