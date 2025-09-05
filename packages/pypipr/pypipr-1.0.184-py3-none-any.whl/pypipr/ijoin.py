from .filter_empty import filter_empty
from .is_iterable import is_iterable
from .to_str import to_str


def ijoin(
    iterable,
    separator="",
    start="",
    end="",
    remove_empty=False,
    recursive=True,
    recursive_flat=False,
    str_strip=False,
):
    """
    Simplify Python join functions like PHP function.
    Iterable bisa berupa sets, tuple, list, dictionary.

    ```python
    arr = {'asd','dfs','weq','qweqw'}
    print(ijoin(arr, ', '))

    arr = '/ini/path/seperti/url/'.split('/')
    print(ijoin(arr, ','))
    print(ijoin(arr, ',', remove_empty=True))

    arr = {'a':'satu', 'b':(12, 34, 56), 'c':'tiga', 'd':'empat'}
    print(ijoin(arr, separator='</li>\\n<li>', start='<li>', end='</li>',
        recursive_flat=True))
    print(ijoin(arr, separator='</div>\\n<div>', start='<div>', end='</div>'))
    print(ijoin(10, ' '))
    ```
    """
    if not is_iterable(iterable):
        iterable = [iterable]

    separator = to_str(separator)

    if isinstance(iterable, dict):
        iterable = iterable.values()

    if remove_empty:
        # iterable = (i for i in filter_empty(iterable))
        iterable = filter_empty(iterable)

    if recursive:
        rec_flat = dict(start=start, end=end)
        if recursive_flat:
            rec_flat = dict(start="", end="")

        def rec(x):
            return ijoin(
                iterable=x,
                separator=separator,
                **rec_flat,
                remove_empty=remove_empty,
                recursive=recursive,
                recursive_flat=recursive_flat,
            )

        iterable = ((rec(i) if is_iterable(i) else i) for i in iterable)

    # iterable = (str(i) for i in iterable)
    iterable = map(str, iterable)

    if str_strip:
        # iterable = (i.strip() for i in iterable)
        iterable = map(str.strip, iterable)

    result = start

    for index, value in enumerate(iterable):
        if index:
            result += separator
        result += value

    result += end

    return result
