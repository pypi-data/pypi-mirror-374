
from .console_run import console_run


def poetry_shell():
    """
    Masuk ke virtual environment poetry

    ```py
    poetry_shell()
    ```
    """
    venv = console_run("poetry env activate", capture_output=True)
    console_run(venv)
