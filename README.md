# Portfolio Manager

Portfolio Manager is a desktop app for planning and executing work across a
portfolio of creative and technical projects. The Tauri version is the intended
daily-use app: download it, launch it like a normal desktop application, and use
it to keep projects, milestones, sessions, plans, and weekly reviews in one
local workspace.

## Download The Desktop App

The recommended way to use Portfolio Manager is the Tauri desktop build from the
project's GitHub Releases page.

1. Open **Releases** for this repository.
2. Download the newest Portfolio Manager installer or app bundle for your
   platform.
3. Install it using your operating system's normal app installation flow.
4. Launch **Portfolio Manager**.

Packaged desktop builds are intended to include the application UI and local
backend sidecar, so normal users should not need to install Python, Node, Rust,
or Tauri manually.

If a packaged release is not available yet, this repository is still useful as
the source and packaging workspace for the desktop app. See
[DEV-AND-ROADMAP.md](DEV-AND-ROADMAP.md) for current development status and
local build notes.

## What The App Helps With

- **Portfolio dashboard**: see project status, scores, weekly session totals,
  and upcoming milestones at a glance.
- **Project management**: move projects through active, backlog, and archive
  states with priority ordering.
- **Session scheduling**: plan time-boxed work sessions from 15 to 480 minutes
  and link them to projects, milestones, and weeks.
- **Weekly budget tracking**: compare planned and completed session time against
  your configured weekly capacity.
- **Milestone tracking**: track outcome-based milestones from backlog through
  planned, doing, done, or cancelled.
- **Plan documents**: keep Markdown project plans with Mermaid diagram support.
- **Weekly review**: capture structured reflections and revisit past reviews.
- **Configurable scoring**: use session completion and milestone progress to
  keep portfolio health visible.
- **Auto-save**: changes persist immediately; there is no separate save step.

## First Launch

On first launch, Portfolio Manager creates a local configuration directory and
SQLite database in your home folder:

```text
~/.portfolio_manager/config.toml
~/.portfolio_manager/portfolio.db
```

Your project data is local to your machine. The default weekly session budget is
12 hours and the default session length is 90 minutes; both can be changed from
the app settings or by editing the config file.

## Updating

For packaged desktop builds, download and install the newest release from the
repository's Releases page. Your local data lives outside the app bundle, so
updating the app should not remove your portfolio database.

Before trying pre-release builds, make a copy of:

```text
~/.portfolio_manager/portfolio.db
```

## Troubleshooting

If the app will not open on macOS, check whether the release notes mention code
signing or notarization status for that build. Early builds may require opening
the app from Finder with **Open** instead of double-clicking.

If your projects or sessions appear to be missing, confirm that the app is using
the expected database path in:

```text
~/.portfolio_manager/config.toml
```

Developer setup, legacy launch scripts, architecture notes, and the release
roadmap live in [DEV-AND-ROADMAP.md](DEV-AND-ROADMAP.md).

## License

See [LICENSE](LICENSE).
