# Architecture

## Overview

Portfolio Manager uses a layered **Model-View-Controller (MVC)** architecture augmented with a **Service Layer** for business logic and a **Repository Layer** for data access. This separation ensures views contain no business logic and all SQL is confined to repositories.

```mermaid
graph TD
    subgraph "Presentation Layer"
        V1[DashboardView]
        V2[SessionView]
        V3[ProjectView]
        V4[MilestoneView]
        V5[WeeklyReviewView]
        V6[SettingsView]
    end

    subgraph "Controller Layer"
        C1[DashboardController]
        C2[SessionController]
        C3[ProjectController]
        C4[MilestoneController]
        C5[ReviewController]
        C6[SettingsController]
    end

    subgraph "Service Layer"
        S1[ProjectService]
        S2[SessionService]
        S3[ScoringService]
        S4[PlanService]
        S5[WeekService]
    end

    subgraph "Repository Layer"
        R1[ProjectRepository]
        R2[SessionRepository]
        R3[MilestoneRepository]
        R4[ReviewRepository]
        R5[ScoreRepository]
    end

    subgraph "Infrastructure"
        DB[(SQLite Database)]
        LOG[Logger]
        CFG[Config / Settings]
        BUS[EventBus]
    end

    V1 --> C1
    V2 --> C2
    V3 --> C3
    V4 --> C4
    V5 --> C5
    V6 --> C6

    C1 --> S1
    C1 --> S3
    C2 --> S2
    C3 --> S1
    C3 --> S4
    C4 --> R3
    C5 --> R4
    C6 --> CFG

    S1 --> R1
    S2 --> R2
    S3 --> R2
    S3 --> R3
    S3 --> R5
    S4 --> R1
    S5 -.-> BUS

    R1 --> DB
    R2 --> DB
    R3 --> DB
    R4 --> DB
    R5 --> DB
```

---

## Layer Responsibilities

| Layer | Responsibility |
|-------|---------------|
| **Views** | Render Tkinter widgets; fire user events; call controller methods |
| **Controllers** | Translate UI actions to service calls; bind views to event bus |
| **Services** | Enforce business rules; orchestrate repositories; emit domain events |
| **Repositories** | Execute SQL; map rows to domain objects; enforce transaction boundaries |
| **Infrastructure** | Singleton DB connection; logging setup; TOML config; event bus |

---

## Application Startup Sequence

```mermaid
sequenceDiagram
    participant L as launch.sh
    participant A as app.py
    participant CFG as Settings
    participant DB as DatabaseConnection
    participant MIG as migrations.py
    participant GUI as MainWindow

    L->>A: python -m portfolio_manager
    A->>CFG: load_settings()
    CFG-->>A: Settings object (or defaults)
    A->>DB: DatabaseConnection.initialise(path)
    DB-->>A: connection ready
    A->>MIG: run_migrations(db)
    MIG-->>A: schema up to date
    A->>GUI: build MainWindow(controllers)
    GUI->>GUI: DashboardView.refresh()
    GUI-->>A: Tk mainloop
```

---

## Project Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Active : create project
    Active --> Backlog : deprioritize
    Backlog --> Active : reactivate
    Active --> Archive : complete or stop
    Backlog --> Archive : abandon
    Archive --> [*] : read-only history
```

---

## Session Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Backlog : create session
    Backlog --> Planned : plan
    Planned --> Doing : start
    Doing --> Done : complete
    Planned --> Done : mark done
    Backlog --> Cancelled : cancel
    Planned --> Cancelled : cancel
    Doing --> Cancelled : cancel
    Done --> [*] : archived with project
    Cancelled --> [*] : delete
```

---

## Milestone Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Backlog : create milestone
    Backlog --> Planned : plan
    Planned --> Doing : start work
    Doing --> Done : complete
    Planned --> Done : mark done directly
    Backlog --> Cancelled : cancel
    Planned --> Cancelled : cancel
    Doing --> Cancelled : cancel
    Done --> [*] : (remains in history)
```

---

## Source Structure

```
src/portfolio_manager/
├── __main__.py          # python -m portfolio_manager entry point
├── app.py               # Bootstrap: wires all layers, returns MainWindow
├── exceptions.py        # Custom exception hierarchy
│
├── config/
│   └── settings.py      # Settings dataclass + TOML loader
│
├── db/
│   ├── connection.py    # Singleton DatabaseConnection
│   ├── migrations.py    # Versioned migration runner
│   └── schema.sql       # Initial DDL
│
├── models/              # Dataclass domain objects (no DB logic)
├── repositories/        # SQL access (one per entity)
├── services/            # Business logic (one per domain)
├── controllers/         # UI ↔ service mediation
├── views/               # Tkinter frames and widgets
├── events/              # EventBus (Observer pattern)
└── utils/               # Date helpers, logging setup
```
