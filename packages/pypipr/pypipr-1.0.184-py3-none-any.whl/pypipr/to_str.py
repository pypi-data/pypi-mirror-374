from .is_empty import is_empty


def to_str(value):
    """
    Mengubah value menjadi string literal

    ```python
    print(to_str(5))
    print(to_str([]))
    print(to_str(False))
    print(to_str(True))
    print(to_str(None))
    ```
    """
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, bool):
        return "1" if value else "0"
    if is_empty(value):
        return ""
    try:
        return str(value)
    except Exception:
        raise Exception(f"Tipe data {value} tidak diketahui")
