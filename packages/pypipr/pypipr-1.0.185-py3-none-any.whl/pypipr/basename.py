import os


def basename(path):
    """
    Mengembalikan nama file dari path

    ```python
    print(basename("/ini/nama/folder/ke/file.py"))
    ```
    """
    return os.path.basename(path)
