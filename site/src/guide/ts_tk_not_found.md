# Tkinter Not Found

Portfolio Manager requires Tkinter \(Python's standard GUI library\). This error occurs most often when Python is installed via Homebrew on macOS.

Launching Portfolio Manager produces one of the following errors:

```
ModuleNotFoundError: No module named '_tkinter'
ModuleNotFoundError: No module named 'tkinter'
```

**Python was installed via Homebrew**, which does not include Tkinter by default.

1.  Download and install the official Python 3.11 \(or later\) package for macOS from [python.org](https://python.org).

    The python.org installer includes Tkinter. Do not use the Homebrew formula.

2.  Confirm that the new Python is the active version:

    ```
    which python3
    python3 --version
    ```

    The output should show the python.org installation path \(typically `/Library/Frameworks/Python.framework/…`\).

3.  Verify Tkinter is available:

    ```
    python3 -c "import tkinter; print('Tkinter OK')"
    ```

4.  Delete the existing virtual environment and relaunch:

    ```
    rm -rf .venv
    bash launch.sh
    ```


**On Linux**, Tkinter is a separate package not always installed with Python.

1.  Install the Tkinter package for your distribution:

    Debian/Ubuntu:

    ```
    sudo apt install python3-tk
    ```

    Fedora/RHEL:

    ```
    sudo dnf install python3-tkinter
    ```

    Arch Linux:

    ```
    sudo pacman -S tk
    ```

2.  Relaunch Portfolio Manager:

    ```
    bash launch.sh
    ```


