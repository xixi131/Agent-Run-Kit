# Context Archive Prompt Patterns

## Compress one repository

```text
$Context_archive Compress this repository's memory layer.
Slim AGENTS.md to project facts only.
Create or refresh agent-state.md.
Turn codex-progress.md into a short current summary plus recent entries.
Move older detailed entries into codex-progress-archive.md without losing history.
If codex-progress.md is over about 250 lines or 18 KB, treat compression as required.
```

## Refresh current handoff only

```text
$Context_archive Refresh only the current handoff memory.
Update agent-state.md and the top summary in codex-progress.md.
Do not rewrite older archive history unless it is necessary.
Use this when the queue changed but the full history does not need a fresh archive pass.
```

## Rebuild after a long task run

```text
$Context_archive Rebuild the repository memory after a long execution run.
Keep the recent high-signal entries in codex-progress.md.
Archive older details.
Make sure the next agent can start from AGENTS.md, agent-state.md, feature_list.json, and codex-progress.md only.
Use this when Auto_dev or Task_init reports that the memory layer is oversized or stale.
```

## Recommended suffix

```text
Preserve project-specific facts.
Remove duplicated generic SOP when the global skills already define it.
Do not touch product code or tests.
```
