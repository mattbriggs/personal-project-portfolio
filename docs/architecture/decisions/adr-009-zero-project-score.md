# ADR-009: Zero-active-project portfolio score

**Status:** Accepted

## Context

Open Question 1: what is the portfolio score when no scores exist for a week?

## Decision

Preserve the Tkinter behavior: `ScoringService.portfolio_score` returns **0**
when no project scores exist for the week (rather than raising or returning null).
Verified by `test_portfolio_score_zero_when_no_scores`.
