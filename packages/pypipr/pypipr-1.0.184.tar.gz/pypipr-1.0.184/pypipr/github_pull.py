from .console_run import console_run


def github_pull():
    """
    Menjalankan command `git pull`

    ```py
    github_pull()
    ```
    """
    console_run("git pull")
