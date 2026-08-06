"""Weekly budget read model."""

from dataclasses import dataclass


@dataclass
class WeeklyBudget:
    """Planned vs. done minutes against the configured weekly budget.

    :param budget_minutes: Configured weekly budget (hours * 60).
    :param planned_minutes: Total non-cancelled session minutes this week.
    :param done_minutes: Completed session minutes this week.
    """

    budget_minutes: int
    planned_minutes: int
    done_minutes: int

    @property
    def remaining_minutes(self) -> int:
        """Budget minutes still unplanned (never negative).

        :rtype: int
        """
        return max(0, self.budget_minutes - self.planned_minutes)
