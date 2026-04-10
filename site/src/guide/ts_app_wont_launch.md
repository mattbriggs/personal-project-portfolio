# Portfolio Manager Does Not Launch

The application fails to open, exits immediately, or shows no window after launching from the Dock or a shell script.

You launch Portfolio Manager from the Dock icon or by running `bash launch.sh` and one of the following occurs:

-   No window appears.
-   A window flashes briefly and closes.
-   The terminal shows a Python traceback.

**Python version is below 3.11.**

1.  Check the Python version:

    ```
    python3 --version
    ```

2.  If the version is below 3.11, download and install Python 3.11 or later from [python.org](https://python.org).

3.  Delete the existing virtual environment and relaunch:

    ```
    rm -rf .venv
    bash launch.sh
    ```


**Tkinter is not installed or not linked correctly.**

1.  Test whether Tkinter is available:

    ```
    python3 -c "import tkinter; tkinter._test()"
    ```

    If a small test window appears, Tkinter is working. If the command fails, proceed to the next step.

2.  See [Tkinter Not Found](ts_tk_not_found.md) for Tkinter-specific remedies.


**A dependency is missing or the virtual environment is corrupted.**

1.  Delete the virtual environment and reinstall dependencies:

    ```
    rm -rf .venv
    bash launch.sh
    ```

    The launch script recreates the virtual environment and installs all dependencies.


**A database migration error occurred during startup.**

1.  Check the application log for migration errors:

    ```
    ls ~/.portfolio_manager/logs/
    cat ~/.portfolio_manager/logs/portfolio_manager.log
    ```

2.  If a migration error is shown, see [Database Error on Launch or During Use](ts_database_error.md).


