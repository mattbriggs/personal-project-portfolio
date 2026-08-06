"""Domain status enumerations.

Preserved verbatim from the original Tkinter application so existing database
rows and scoring rules remain valid. Values are plain string literals to match
the SQLite ``CHECK`` constraints in the schema.
"""

from typing import Literal

#: Project lifecycle status.
ProjectStatus = Literal["active", "backlog", "archive"]

#: Session lifecycle status. ``backlog`` and ``cancelled`` do not count toward
#: score or weekly budget.
SessionStatus = Literal["backlog", "planned", "doing", "done", "cancelled"]

#: Milestone lifecycle status. ``cancelled`` milestones are excluded from
#: scoring.
MilestoneStatus = Literal["backlog", "planned", "doing", "done", "cancelled"]

#: Traffic-light score status.
ScoreStatus = Literal["green", "yellow", "red"]

PROJECT_STATUSES: frozenset[str] = frozenset({"active", "backlog", "archive"})
SESSION_STATUSES: frozenset[str] = frozenset({"backlog", "planned", "doing", "done", "cancelled"})
MILESTONE_STATUSES: frozenset[str] = frozenset({"backlog", "planned", "doing", "done", "cancelled"})
SCORE_STATUSES: frozenset[str] = frozenset({"green", "yellow", "red"})
