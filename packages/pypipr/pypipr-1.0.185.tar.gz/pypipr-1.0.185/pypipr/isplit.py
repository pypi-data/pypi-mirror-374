import re


def isplit(text, separator="", include_separator=False):
    """
    Memecah text menjadi list berdasarkan separator.

    ```python
    t = '/ini/contoh/path/'
    print(isplit(t, separator='/'))
    ```
    """
    if include_separator:
        separator = f"({separator})"

    result = re.split(separator, text, flags=re.IGNORECASE | re.MULTILINE)

    return result
