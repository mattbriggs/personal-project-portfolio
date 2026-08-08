"""Pydantic request/response/error contracts for the ``/api/v1`` boundary.

These models are the external HTTP contract. They are intentionally distinct
from domain dataclasses and SQLite rows (SRS §3.5): database row models are never
reused as HTTP contracts.
"""
