from .LINUX import LINUX
from .WINDOWS import WINDOWS


def ienv(on_windows=None, on_linux=None):
    """
    Mengambalikan hasil berdasarkan environment dimana program dijalankan

    ```py
    getch = __import__(ienv(on_windows="msvcrt", on_linux="getch"))


    f = ienv(on_windows=fwin, on_linux=flin)
    f()


    inherit = ienv(
        on_windows=[BaseForWindows, BaseEnv, object],
        on_linux=[SpecialForLinux, BaseForLinux, BaseEnv, object]
    )

    class ExampleIEnv(*inherit):
        pass
    ```
    """
    if WINDOWS:
        return on_windows
    if LINUX:
        return on_linux
    raise Exception("Environment tidak diketahui.")
