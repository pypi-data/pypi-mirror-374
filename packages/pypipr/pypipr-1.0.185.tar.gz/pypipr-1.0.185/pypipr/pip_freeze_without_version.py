from .console_run import console_run
from .ijoin import ijoin
from .iopen import iopen
from .WINDOWS import WINDOWS


def pip_freeze_without_version(filename=None):
    """
    Memberikan list dari dependencies yang terinstall tanpa version.
    Bertujuan untuk menggunakan Batteries Included Python.

    ```py
    print(pip_freeze_without_version())
    ```
    """
    run = console_run("PIP Freeze", "pip list --format=freeze", capture_output=True)

    text = run.stdout
    if WINDOWS:
        text = text.decode()

    res = ijoin((i.split("=")[0] for i in text.splitlines()), separator="\n")

    if filename:
        return iopen(filename, data=res)

    return res
