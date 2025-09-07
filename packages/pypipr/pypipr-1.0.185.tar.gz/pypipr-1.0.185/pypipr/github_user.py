from .console_run import console_run


def github_user(email=None, name=None):
    """
    Menyimpan email dan nama user secara global sehingga tidak perlu
    menginput nya setiap saat.

    ```py
    github_user('my@emil.com', 'MyName')
    ```
    """
    if email:
        console_run(
            "Update Github User Email", f"git config --global user.email {email}"
        )
    if name:
        console_run("Update Github User Name", f"git config --global user.name {name}")
