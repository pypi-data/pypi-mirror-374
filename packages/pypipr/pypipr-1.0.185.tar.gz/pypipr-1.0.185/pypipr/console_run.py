import subprocess

from .print_log import print_log


def console_run(info, command=None, print_info=True, capture_output=False):
    """
    Menjalankan command seperti menjalankan command di Command Terminal

    ```py
    console_run('dir')
    console_run('ls')
    ```
    """
    if command is None:
        command = info

    if print_info:
        print_log(info)

    param = dict(shell=True)
    if capture_output:
        param |= dict(capture_output=True, text=True)

    return subprocess.run(command, **param)
