# Scoring Algorithm Reference

Complete specification of the project health score calculation, traffic-light thresholds, and portfolio score aggregation.

## Project Score Formula

For a given project and week key:

```
session_score    = (done_sessions ÷ planned_sessions) × 60
milestone_score  = (done_milestones ÷ total_milestones) × 40
project_score    = session_score + milestone_score
```

Where:

-   `done_sessions` — count of sessions with status `done` for the project in the week
-   `planned_sessions` — count of sessions with status `planned`, `doing`, or `done` for the project in the week
-   `done_milestones` — count of milestones with status `done`
-   `total_milestones` — count of all milestones except those with status `cancelled`

If `planned_sessions` is 0, `session_score` is 0. If `total_milestones` is 0, `milestone_score` is 0.

## Traffic-Light Thresholds

|Score|Status|Dashboard indicator|
|-----|------|-------------------|
|80–100|Green|Green badge|
|60–79|Yellow|Yellow badge|
|0–59|Red|Red badge|

## Portfolio Score Formula

```
portfolio_score = average(project_score for each active project)
```

Only active projects contribute to the portfolio score. Backlog and archived projects are excluded.

## Manual Override

A score can be overridden for a specific project and week. Overrides require a text reason and set `is_manual_override = true` in the `project_score` table. Override scores replace calculated scores in all displayed values.

## Week Key Format

Week keys use ISO 8601 calendar week notation:

```
YYYY.W
```

Examples: `2026.1` \(first week of 2026\), `2026.52` \(last full week of 2026\). Week 1 is the week containing the first Thursday of the year. Weeks always begin on Monday and end on Sunday.

