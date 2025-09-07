from .is_empty import is_empty

def to_str(value):
    """
    Mengubah value menjadi string literal yang konsisten.

    Aturan:
    - str: dikembalikan apa adanya.
    - bool: True -> "1", False -> "0".
    - int/float: dikonversi via str().
    - None atau objek kosong (menurut is_empty): "".
    - fallback: str(value), atau TypeError jika gagal.
    """
    # 1. String apa adanya
    if isinstance(value, str):
        return value

    # 2. Boolean harus dicek lebih dulu (karena subclass int)
    if isinstance(value, bool):
        return "1" if value else "0"

    # 3. Numerik (int, float, tapi bukan bool)
    if isinstance(value, (int, float)):
        return str(value)

    # 4. Kosong (None, [], {}, dsb. tergantung is_empty)
    if is_empty(value):
        return ""

    # 5. Fallback: str()
    try:
        return str(value)
    except Exception as e:
        raise TypeError(f"Tipe data {type(value).__name__} tidak bisa diubah ke str") from e


# from .is_empty import is_empty
#
#
# def to_str(value):
#     """
#     Mengubah value menjadi string literal
#
#     ```python
#     print(to_str(5))
#     print(to_str([]))
#     print(to_str(False))
#     print(to_str(True))
#     print(to_str(None))
#     ```
#     """
#     if isinstance(value, str):
#         return value
#     if isinstance(value, (int, float)):
#         return str(value)
#     if isinstance(value, bool):
#         return "1" if value else "0"
#     if is_empty(value):
#         return ""
#     try:
#         return str(value)
#     except Exception:
#         raise Exception(f"Tipe data {value} tidak diketahui")
