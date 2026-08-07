# Which Version This Guide Describes

Portfolio Manager is being rebuilt on a new technology stack. This guide describes the version you can install and run today; this topic explains what is changing and what is not.

## Two versions, one database

The repository currently contains two applications that read the same SQLite database and apply the same rules:

-   **The current app** — written in Python with a Tkinter interface. This is the version that runs today, and the one every task in this guide describes.
-   **The V2 app** — a desktop application built on Tauri, React, and a Python service. It installs as a normal macOS application and needs no Python setup. It is available now, but has not yet been through formal feature-parity acceptance.

**Important:** The task steps in this guide were written against the current app. The concepts, workflows, and reference material apply to both; the installation and troubleshooting topics are specific to the current app.

## What carries over

The parts of this guide that describe how Portfolio Manager *thinks* apply to both versions without change, because the V2 app reuses the same domain logic:

-   Project, session, and milestone lifecycles and their states
-   The scoring model and the weekly review cycle
-   Week numbering, the weekly budget, and the planning workflow
-   Configuration keys and the project plan Markdown syntax

Your data carries over as well. A database created by the current app opens in the V2 app with no manual conversion, and a backup is written before any upgrade runs.

## What changes

Only the surrounding mechanics change:

-   **Installation.** The current app runs from a cloned repository and a Python virtual environment. The V2 app will install as a signed macOS application bundle, with no Python setup required.
-   **Python and Tkinter requirements.** The V2 app bundles everything it needs, so the Tkinter troubleshooting in this guide will no longer apply.
-   **One scoring detail.** The V2 app excludes cancelled milestones when calculating a project score; the current app counts them. A project with cancelled milestones may therefore score slightly differently after the switch.

