# Install Portfolio Manager on macOS

Install the current Tauri desktop app as a macOS application bundle.

**Prerequisite:** Build the app locally or download a release DMG. Developer local build instructions live in `design/2026.08-07-Build-Local-App-Dev.md`.

## Current Tauri app

-   macOS 12 \(Monterey\) or later
-   A built `Portfolio Manager.app` bundle or DMG

1.  If you have a DMG, open it and drag `Portfolio Manager.app` to `/Applications`.

2.  If you built locally, run the helper from the repository root:

    ```
    scripts/install_macos_app.sh
    ```

    The helper signs the bundle, verifies it, and installs it into `/Applications`.

3.  Open Portfolio Manager from `/Applications`.

    Portfolio Manager opens, creates the database and configuration file at `~/.portfolio_manager/`, and displays the Dashboard.

## Legacy Tkinter Dock shortcut

Use this only if you intentionally want the older Python/Tkinter app.

-   Python 3.11 or later from [python.org](https://python.org). The python.org installer includes Tkinter.

    **CAUTION:**

    Python installed via Homebrew may not include Tkinter. Use the python.org installer to avoid launch failures.

-   Git
-   An internet connection for the initial clone

1.  Open Terminal and clone the Portfolio Manager repository:

    ```
    git clone <repository-url> portfolio-manager
    cd portfolio-manager
    ```

2.  Run the macOS shortcut creation script:

    ```
    bash create_shortcut.sh
    ```

    The script creates a `Portfolio Manager.app` bundle in `~/Applications/` and sets up a Python virtual environment in `.venv/` inside the repository.

3.  Open Finder and navigate to `~/Applications/`.

4.  Drag `Portfolio Manager.app` to the right side of the Dock.

5.  Click the Dock icon to launch Portfolio Manager for the first time.

    Portfolio Manager opens, creates the database and configuration file at `~/.portfolio_manager/`, and displays the Dashboard.


To update the legacy application, run `git pull origin main` in the repository directory. The next time you launch from the Dock, the updated code runs automatically. No reinstallation is required.
