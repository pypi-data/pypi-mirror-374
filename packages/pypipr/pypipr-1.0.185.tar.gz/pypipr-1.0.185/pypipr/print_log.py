from .print_colorize import print_colorize


def print_log(text):
    """
    Akan melakukan print ke console.
    Berguna untuk memberikan informasi proses program yg sedang berjalan.

    ```python
    print_log("Standalone Log")
    ```
    """
    print_colorize(f">>> {text}")
