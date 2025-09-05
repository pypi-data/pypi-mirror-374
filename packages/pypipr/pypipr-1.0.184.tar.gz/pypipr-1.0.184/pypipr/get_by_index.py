def get_by_index(obj, index, on_error=None):
    """
    Mendapatkan value dari object berdasarkan indexnya.
    Jika error out of range maka akan mengembalikan on_error.
    
    ```python
    l = [1, 3, 5]
    print(get_by_index(l, 7))
    ```
    """
    try:
        return obj[index]
    except Exception:
        return on_error
