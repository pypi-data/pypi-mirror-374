import math
import pprint

import colorama

from .is_iterable import is_iterable


def iprint(
    *args,
    color=None,
    sort_dicts=False,
    **kwargs,
):
    """
    Improve print function dengan menambahkan color dan pretty print
    Color menggunakan colorama Fore + Back + Style

    ```python
    import colorama
    iprint(
        'yang ini',
        {'12':12,'sdsd':{'12':21,'as':[88]}},
        color=colorama.Fore.BLUE + colorama.Style.BRIGHT
    )
    ```
    """

    r = []
    for i in args:
        if is_iterable(i) and not isinstance(i, (list, set, dict, tuple)):
            i = list(i)

        if not isinstance(i, str):
            i = pprint.pformat(i, depth=math.inf, sort_dicts=sort_dicts)

        if color:
            i = color + i + colorama.Style.RESET_ALL

        r.append(i)

    print(*r, **kwargs)
