# Install the Legacy App via the Command Line

Install and launch the legacy Python/Tkinter Portfolio Manager using the shell launch script or a manual virtual-environment setup. This method is suited for compatibility testing, Linux systems, and historical workflows that still use the Tkinter interface.

-   macOS or Linux
-   Python 3.11 or later with Tkinter support
-   Git
-   An internet connection for the initial clone

**Important:** These steps install the legacy Python/Tkinter app. The current desktop app is the Tauri/React/FastAPI application; install it with the macOS app instructions or build it with the developer build guide. See [Which Version This Guide Describes](c_app_versions.md).

1.  Clone the repository:

    ```
    git clone <repository-url> portfolio-manager
    cd portfolio-manager
    ```

2.  Choose one of the following launch methods:

    -   **Shell script \(recommended\):** Run the launch script directly. It creates the virtual environment on the first run and installs all dependencies.

        ```
        bash launch.sh
        ```

    -   **Manual virtual environment:** Create and activate a virtual environment, then install the package and run the application.

        ```
        python3 -m venv .venv
        source .venv/bin/activate
        pip install -e .[dev]
        python -m portfolio_manager
        ```

    The legacy app opens and initializes the database and configuration file at `~/.portfolio_manager/` on first launch.


To update, run `git pull origin main` in the repository directory. The launch script automatically installs any new dependencies on the next run.

To run the test suite:

```
source .venv/bin/activate
pytest
```
