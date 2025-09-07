import colorama
import time


def print_colorize(
    text,
    color=colorama.Fore.GREEN,
    bright=colorama.Style.BRIGHT,
    color_end=colorama.Style.RESET_ALL,
    text_start="",
    text_end="\n",
    delay=0.05
):
    """
    Print text dengan warna untuk menunjukan text penting

    ```py
    print_colorize("Print some text")
    print_colorize("Print some text", color=colorama.Fore.RED)
    ```
    """
    print(f"{text_start}{color + bright}{text}{color_end}", end=text_end, flush=True)
    if delay:
        time.sleep(delay)
