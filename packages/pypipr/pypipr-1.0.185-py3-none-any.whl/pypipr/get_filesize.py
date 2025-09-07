import os


def get_filesize(filename):
    """
    Mengambil informasi file size dalam bytes

    ```python
    print(get_filesize(__file__))
    ```
    """
    return os.stat(filename).st_size
