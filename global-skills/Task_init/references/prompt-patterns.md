# Task Init Prompt Patterns

## Fresh requirement

```text
$Task_init Break the requirement below into 20 very small tasks and write them into feature_list.json.
Before writing tasks, move the current feature_list.json tasks into final_feature_list.json, clear feature_list.json, then write only the new active queue.
First build a requirement fulfillment map, then derive the smallest runnable delivery slices that prove the requirement is becoming real.
If the memory layer is clearly oversized or stale, run $Context_archive first.
All descriptions and validation steps must be in English.
Every task must include task_type and budget_minutes.
Default to tasks that take at most 10 minutes.

<paste the requirement here>
```

## Rewrite pending items only

```text
$Task_init Re-plan feature_list.json from the requirement below.
Before writing tasks, move the current feature_list.json tasks into final_feature_list.json, clear feature_list.json, then write only the new active queue.
First build a requirement fulfillment map, then derive the smallest runnable delivery slices that prove the requirement is becoming real.
If the memory layer is clearly oversized or stale, run $Context_archive first.
All descriptions and validation steps must be in English.
Every task must include task_type and budget_minutes.
Default to tasks that take at most 10 minutes.

<paste the requirement here>
```

## Append a new phase

```text
$Task_init Plan 8 very small tasks for the next phase based on the goal below.
Before writing tasks, move the current feature_list.json tasks into final_feature_list.json, clear feature_list.json, then write only the new active queue.
First build a requirement fulfillment map, then derive the smallest runnable delivery slices that prove the phase is becoming real.
If the memory layer is clearly oversized or stale, run $Context_archive first.
Write all task text in English.
Every task must include task_type and budget_minutes.
Default to tasks that take at most 10 minutes.

<paste the phase goal here>
```

## Recommended suffix

```text
If any task feels medium-sized, split it into smaller tasks before writing the queue.
First derive the requirement fulfillment map and implementation path, then split that path into runnable delivery slices.
Every implementation task must map back to an acceptance outcome or an unavoidable prerequisite.
Every implementation task must validate real behavior through the most realistic UI, API, file, or command entry point available.
For docs tasks, split document shell creation from content fill-in.
Use `budget_minutes: 5` for `docs` and `planning` tasks by default.
Use `budget_minutes: 8-10` for most `frontend` and `backend` tasks, and `10` for most `e2e` tasks.
If any task seems to need more than 10 minutes, split it again before writing the queue.
Refresh `agent-state.md` if planning materially changes the next pending task or recommended read path.
```
