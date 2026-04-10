# Install Portfolio Manager via the Command Line

Install and launch Portfolio Manager using the shell launch script or a manual virtual-environment setup. This method is suited for development, testing, or Linux systems.

-   macOS or Linux
-   Python 3.11 or later with Tkinter support
-   Git
-   An internet connection for the initial clone


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

    Portfolio Manager opens and initializes the database and configuration file at `~/.portfolio_manager/` on first launch.


To update, run `git pull origin main` in the repository directory. The launch script automatically installs any new dependencies on the next run.

To run the test suite:

```
source .venv/bin/activate
pytest
```

