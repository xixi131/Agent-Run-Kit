---
name: Context_archive
description: Compress and maintain a repository's memory files for long-running agent work. Use when the user asks to archive or slim context, reduce startup token cost, preserve project facts while removing duplicated SOP, create or refresh agent-state.md, and roll codex-progress history into a short summary plus archive.
---

# Context_archive

Use this skill when the user wants to reduce startup context cost without losing durable project memory.

This skill manages the repository memory layer, not product features.

## Skill boundaries
Use `$Context_archive` when you need to compress, refresh, or archive the repository memory layer.
Do not use `$Context_archive` to:
* create or rewrite feature tasks,
* execute pending product tasks,
* or make unrelated product-code changes.

Hand off instead:
* use `$Task_init` when the queue itself needs planning or replanning,
* use `$Auto_dev` when the queue is ready and you want task execution.

## Goal
Keep the default startup context small, stable, and recoverable:
* `AGENTS.md` should hold project facts, routing, and durable constraints.
* `agent-state.md` should hold the current handoff state.
* `codex-progress.md` should hold a short current summary plus recent high-signal entries.
* `codex-progress-archive.md` should preserve older detailed history.

This layered layout is meant to be consumed by execution agents in this order:
* `AGENTS.md`
* `agent-state.md`
* `feature_list.json`
* `codex-progress.md`

Everything else should be read on demand.

## Design principles
Use these memory rules when compressing context:
* keep stable project facts in one small file,
* keep current execution state in one very small file,
* keep detailed history in an archive, not in the default startup path,
* prefer rolling summaries over forcing every new agent to reread long logs,
* never delete meaningful history if it can be moved into an archive,
* remove duplicated generic SOP before removing project-specific facts.

These principles are aligned with long-running-agent harness design: durable external memory, small startup context, rolling summaries, and explicit handoff artifacts.

## Required context
Read only the memory layer first:
* `AGENTS.md`
* `feature_list.json`
* `codex-progress.md`
* `agent-state.md` if it exists

Read detailed project docs only if needed to preserve project facts while slimming `AGENTS.md`.

## What this skill may change
This skill is allowed to change only the repository memory files unless the user explicitly expands scope:
* `AGENTS.md`
* `agent-state.md`
* `codex-progress.md`
* `codex-progress-archive.md`

Do not modify product code, tests, build files, or feature tasks unless the user explicitly asks.

## Workflow
1. Read the current memory files and identify:
   * project facts,
   * current execution state,
   * recent high-signal work,
   * duplicated generic workflow text,
   * and stale or oversized startup context.
2. Slim `AGENTS.md` so it keeps project facts, routing, and invariants, while pushing generic process guidance to global skills.
3. Create or refresh `agent-state.md` with:
   * current phase,
   * first pending task,
   * recommended next read path,
   * runtime notes,
   * active blockers worth surfacing at startup.
4. Rebuild `codex-progress.md` into:
   * a short current summary,
   * a queue snapshot,
   * environment notes,
   * and a small set of recent high-signal entries.
5. Move older detailed entries into `codex-progress-archive.md` if needed.
6. Verify that history was preserved and the default startup path is now:
   * `AGENTS.md`
   * `agent-state.md`
   * `feature_list.json`
   * `codex-progress.md`
7. Make sure the resulting files support execution-agent autonomy:
   * the minimal startup set is small and sufficient,
   * larger files are optional and clearly on-demand,
   * and the handoff state tells the next agent what to read only if needed.

## Compression rules
Use these rules when deciding what stays in the default path:
* keep `AGENTS.md` focused on project facts and read-routing,
* keep `agent-state.md` under roughly one screen of text when possible,
* keep `codex-progress.md` to current summary plus recent entries only,
* prefer 3 to 8 recent entries in the main log unless the project is in a turbulent phase,
* archive older detailed entries rather than truncating them away,
* if `codex-progress.md` grows long again, repeat the roll-up instead of letting it drift.

## AGENTS slimming rules
When slimming `AGENTS.md`:
* keep project summary, module map, invariants, and task-routing guidance,
* keep project-specific migration or architecture notes,
* remove repeated generic parent-child SOP when global skills already define it,
* remove repeated retry, timeout, or budgeting rules if they are not project-specific,
* do not remove actual project facts just to save tokens.

## agent-state rules
`agent-state.md` should answer these startup questions quickly:
* What phase is the project in?
* What is the first pending task?
* What should the next agent read first?
* Are there any active blockers or environment caveats?

## codex-progress rules
`codex-progress.md` should remain useful as the default recent log:
* include a short `Current Summary` section at the top,
* include a queue snapshot and runtime note if relevant,
* keep recent entries detailed enough to audit current work,
* move older entries into `codex-progress-archive.md`,
* never silently discard historical records.

## When to archive
Archive or roll up when one or more of these is true:
* the main log is clearly too long for default startup,
* the main log mostly contains older completed tasks,
* a short summary would let the next agent start faster,
* or the user explicitly asks to compress context.

Use these default thresholds for automatic triggering by other skills:
* `codex-progress.md` is roughly over `250` lines or over `18 KB`,
* `agent-state.md` is missing and the main log is no longer short,
* `agent-state.md` is stale versus the first pending task or current phase,
* or `AGENTS.md` has clearly expanded into repeated generic SOP instead of lean project facts.

`$Auto_dev` and `$Task_init` may trigger `$Context_archive` automatically when those thresholds are met.

## Validation
Before finishing, confirm:
* project-specific facts still exist in `AGENTS.md`,
* `agent-state.md` matches the current first pending task,
* `codex-progress.md` is shorter and startup-friendly,
* `codex-progress-archive.md` preserves moved history,
* the new startup path is smaller but still sufficient for a new agent.

## Output expectations
Report:
* which memory files were changed,
* what was moved into archive,
* what the new default startup read order is,
* and any remaining memory-layer risks.
