"""Framework-independent domain layer.

Contains entities, enumerations, invariants, ISO-week and slug utilities, the
scoring policy, and domain errors. This package must not import FastAPI,
Pydantic contracts, SQLite, Tauri, or any transport/process infrastructure.
"""
