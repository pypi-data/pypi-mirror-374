from .console_run import console_run


def poetry_publish(token=None):
    """
    Publish project to pypi,org

    ```py
    poetry_publish()
    ```
    """
    if token:
        console_run("update token", f"poetry config pypi-token.pypi {token}")
    console_run("Build", "poetry build")
    console_run("Publish to PyPi.org", "poetry publish")
