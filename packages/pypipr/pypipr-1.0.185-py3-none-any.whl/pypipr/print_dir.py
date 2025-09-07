import colorama

from .is_empty import is_empty
from .print_colorize import print_colorize


def print_dir(var, colorize=True):
    """
    Print property dan method yang tersedia pada variabel

    ```python
    import pathlib
    p = pathlib.Path("https://www.google.com/")
    print_dir(p, colorize=False)
    ```
    """
    d = dir(var)
    m = max(len(i) for i in d)
    for i in d:
        try:
            a = getattr(var, i)
            r = a() if callable(a) else a
            if colorize:
                color = colorama.Fore.GREEN
                if is_empty(r):
                    color = colorama.Fore.LIGHTRED_EX
                if i.startswith("__"):
                    color = colorama.Fore.CYAN
                print_colorize(f"{i: >{m}}", text_end=" : ", color=color)
                print(r)
            else:
                print(f"{i: >{m}} : {r}")
        except Exception:
            pass
