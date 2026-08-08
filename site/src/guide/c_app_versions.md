# Which Version This Guide Describes

Portfolio Manager has both a current Tauri desktop app and a legacy Tkinter app in the repository. This guide focuses on the concepts and workflows that apply to both, and calls out version-specific installation or troubleshooting where the two apps differ.

## Two versions, one database

The repository currently contains two applications that read the same SQLite database and apply the same rules:

-   **The current desktop app** — built with Tauri, React, Rust, and a local FastAPI sidecar. It installs as a normal macOS application and bundles its backend runtime.
-   **The legacy app** — written in Python with a Tkinter interface. It still runs from a cloned repository and remains useful for compatibility checks.

**Important:** The concepts, workflows, and reference material apply to both apps. Installation and troubleshooting topics identify the app they apply to.

## What carries over

The parts of this guide that describe how Portfolio Manager *thinks* apply to both versions without change, because the Tauri app preserves the same domain logic:

-   Project, session, and milestone lifecycles and their states
-   The scoring model and the weekly review cycle
-   Week numbering, the weekly budget, and the planning workflow
-   Configuration keys and the project plan Markdown syntax

Your data carries over as well. A database created by the legacy app opens in the Tauri app with no manual conversion, and a backup is written before any upgrade runs.

## What changes

Only the surrounding mechanics change:

-   **Installation.** The Tauri app installs as a macOS application bundle. The legacy app runs from a cloned repository and Python virtual environment.
-   **Python and Tkinter requirements.** The Tauri app bundles the sidecar, so Tkinter troubleshooting applies only to the legacy app.
-   **One scoring detail.** The Tauri app excludes cancelled milestones when calculating a project score; older legacy behavior counted them. A project with cancelled milestones may therefore score slightly differently after switching.
