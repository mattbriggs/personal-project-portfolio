# Design Patterns

Portfolio Manager applies eight design patterns at well-defined seams. Each is documented here with the rationale and a minimal code example.

---

## MVC (Model-View-Controller)

**Where:** Full application.

**Rationale:** Separates display concerns (Tkinter widgets) from business logic (services) and data access (repositories). Views never import repositories.

```
User Action → View → Controller → Service → Repository → DB
                                          ← Model ←
             View ← Controller (via EventBus or direct return)
```

---

## Repository

**Where:** `repositories/` — one class per entity (`ProjectRepository`, `SessionRepository`, etc.).

**Rationale:** Abstracts all SQL from services and controllers. Enables testing with fakes or an in-memory database without touching production code.

```python
class ProjectRepository(BaseRepository):
    def get(self, project_id: int) -> Project:
        row = self._db.fetchone("SELECT * FROM project WHERE id = ?", (project_id,))
        if row is None:
            raise NotFoundError("Project", project_id)
        return _row_to_project(row)
```

---

## Strategy

**Where:** `services/scoring_service.py` — `ScoringStrategy` ABC + `DefaultScoringStrategy`.

**Rationale:** The scoring algorithm is swappable at construction time. Replace it without modifying any callers.

```python
class ScoringStrategy(ABC):
    @abstractmethod
    def compute_score(
        self, planned: int, completed: int,
        total_milestones: int, completed_milestones: int
    ) -> int: ...

class DefaultScoringStrategy(ScoringStrategy):
    def compute_score(self, planned, completed, total_milestones, completed_milestones):
        session_score   = (completed / planned * 60) if planned > 0 else 0
        milestone_score = (completed_milestones / total_milestones * 40) if total_milestones > 0 else 0
        return min(100, round(session_score + milestone_score))

# Inject a custom strategy:
scoring_svc = ScoringService(session_repo, milestone_repo, score_repo,
                              strategy=MyCustomStrategy())
```

---

## Observer (EventBus)

**Where:** `events/event_bus.py` — used by all services and controllers.

**Rationale:** Decouples services from views. A service emits a named event; any interested view (via its controller) refreshes itself.

```python
bus = EventBus.get()

# Subscribe (in a controller):
bus.subscribe(SESSION_COMPLETED, self._on_session_completed)

# Emit (in a service):
bus.emit(SESSION_COMPLETED, session_id=42, project_id=7)
```

Named event constants are defined in `events/event_bus.py`:
`PROJECT_CREATED`, `SESSION_COMPLETED`, `MILESTONE_UPDATED`, etc.

---

## Singleton

**Where:** `DatabaseConnection` and `EventBus`.

**Rationale:** One shared database connection prevents locking conflicts and ensures all repositories operate within the same SQLite connection. The event bus must also be shared globally.

```python
# Initialise once at startup:
db = DatabaseConnection.initialise(Path("~/.portfolio_manager/portfolio.db"))

# Access anywhere:
db = DatabaseConnection.get()
```

---

## Factory (implied)

**Where:** `repositories/` row-to-domain conversion functions (`_row_to_project`, `_row_to_session`, etc.).

**Rationale:** Centralises the mapping from raw `sqlite3.Row` dicts to typed domain dataclasses. One location to update when a schema column changes.

---

## Template Method

**Where:** `services/plan_service.py` — `PlanService.render_html()`.

**Rationale:** The HTML rendering pipeline is fixed (Markdown → HTML body → inject Mermaid script → wrap in shell), but the Markdown converter is injected and the Mermaid script is a replaceable constant.

```python
def render_html(self, markdown_text: str) -> str:
    self._md.reset()
    body_html = self._md.convert(markdown_text)   # step 1
    return _HTML_TEMPLATE.format(                  # steps 2–3
        mermaid_script=_MERMAID_SCRIPT,
        body=body_html,
    )
```

---

## Transaction Context Manager

**Where:** `db/connection.py` — `DatabaseConnection.transaction()`.

**Rationale:** Guarantees `BEGIN` / `COMMIT` / `ROLLBACK` discipline for all multi-step writes. Used in every repository write method.

```python
with self._db.transaction():
    self._db.execute("UPDATE session SET status = ? WHERE id = ?", ("completed", sid))
    self._db.execute("INSERT INTO project_score ...")
# COMMIT on exit; ROLLBACK if any exception is raised
```
