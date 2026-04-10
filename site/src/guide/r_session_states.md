# Session Status Values

Reference for the five session status values, their meaning, and their effect on scoring and budget calculations.

|Status|Meaning|Counts toward budget?|Counts toward score?|
|------|-------|---------------------|--------------------|
|Backlog|Captured but not committed to a week. The session exists as an intention.|No|No|
|Planned|Committed to a scheduled date. Reflects an intention to work on the project this week.|Yes \(as planned time\)|Yes \(as a planned session in the denominator\)|
|Doing|Work is currently in progress.|Yes \(as planned time\)|Yes \(as a planned session in the denominator\)|
|Done|Work is complete. Portfolio Manager records the completion timestamp.|Yes \(as done time\)|Yes \(as a completed session in the numerator and denominator\)|
|Cancelled|Session was abandoned. Can be deleted.|No|No|

## Valid Status Transitions

Sessions can move between states as follows:

-   Backlog → Planned, Doing, Done, Cancelled
-   Planned → Doing, Done, Cancelled
-   Doing → Done, Cancelled
-   Done → \(terminal; edit the session to change if needed\)
-   Cancelled → \(terminal; delete or edit to reactivate\)

