from .is_iterable import is_iterable
from .to_str import to_str


def filter_empty(iterable, zero_is_empty=True, str_strip=True):
    """
    Mengembalikan iterabel yang hanya memiliki nilai

    ```python
    var = [1, None, False, 0, "0", True, {}, ['eee']]
    print(filter_empty(var))
    iprint(filter_empty(var))
    ```
    """
    for i in iterable:
        if i == 0 and zero_is_empty:
            continue
        if isinstance(i, str) and str_strip:
            i = i.strip()
        if not is_iterable(i) and not to_str(i):
            continue
        yield i
