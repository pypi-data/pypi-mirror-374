from .console_run import console_run
from .print_colorize import print_colorize


def github_push(commit_msg=None):
    """
    Menjalankan command status, add, commit dan push

    ```py
    github_push('Commit Message')
    ```
    """

    def console_input(prompt, default):
        print_colorize(prompt, text_end="")
        if default:
            print(default)
            return default
        else:
            return input()

    console_run("git status")
    msg = console_input("Commit Message if any or empty to exit : ", commit_msg)
    if msg:
        console_run("git add .")
        console_run(f'git commit -m "{msg}"')
        console_run("git push")
