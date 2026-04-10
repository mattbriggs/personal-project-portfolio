# Database Error on Launch or During Use

Portfolio Manager fails to start or displays an error message related to the database. Most database errors are caused by a locked file, a missing directory, or a failed schema migration.

One or more of the following symptoms occur:

-   A dialog shows "Database error" on launch.
-   The application starts but projects, sessions, or milestones do not display.
-   The log file contains `sqlite3.OperationalError` entries.
-   The application crashes when creating or saving data.

**The database directory does not exist or is not writable.**

1.  Verify that `~/.portfolio_manager/` exists and is writable:

    ```
    ls -la ~/.portfolio_manager/
    ```

2.  If the directory does not exist, create it:

    ```
    mkdir -p ~/.portfolio_manager
    ```

3.  Relaunch Portfolio Manager. It will recreate the database automatically.


**A failed schema migration corrupted the database.**

1.  Check whether a backup exists:

    ```
    ls ~/.portfolio_manager/*.bak
    ```

2.  If a backup file exists, restore it:

    ```
    cp ~/.portfolio_manager/portfolio.db.bak ~/.portfolio_manager/portfolio.db
    ```

3.  Relaunch Portfolio Manager.

    The migration runs again. If it fails a second time, check the log file for the specific error and report it to the project repository.


**The database file is locked by another process.**

1.  Check whether another Portfolio Manager instance is already running and close it.

2.  If no other instance is running, verify no orphan process holds the database lock:

    ```
    lsof ~/.portfolio_manager/portfolio.db
    ```

3.  Terminate any process listed, then relaunch Portfolio Manager.


