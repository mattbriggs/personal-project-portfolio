# Milestone Status Values

Reference for the five milestone status values and their effect on the project health score.

|Status|Meaning|Counts toward milestone score?|
|------|-------|------------------------------|
|Backlog|Identified but not yet active. Included in the total milestone count.|In total count \(denominator only\)|
|Planned|On the active roadmap. Work toward this outcome has started or is scheduled.|In total count \(denominator only\)|
|Doing|Active work toward achieving this outcome is in progress.|In total count \(denominator only\)|
|Done|Outcome achieved. Portfolio Manager records the completion date.|In numerator and denominator|
|Cancelled|Outcome removed from scope.|Not counted|

## Milestone Score Behavior

The milestone score component is calculated as:

```
(milestones with Done status) ÷ (all milestones except Cancelled) × 40
```

A project with no milestones earns 0 milestone points. To reach the maximum portfolio score of 100, define milestones and advance them to Done as work progresses.

