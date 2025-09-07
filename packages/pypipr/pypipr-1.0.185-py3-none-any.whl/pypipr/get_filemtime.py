import os


def get_filemtime(filename):
    """
    Mengambil informasi last modification time file dalam nano seconds

    ```python
    print(get_filemtime(__file__))
    ```
    """
    return os.stat(filename).st_mtime_ns
