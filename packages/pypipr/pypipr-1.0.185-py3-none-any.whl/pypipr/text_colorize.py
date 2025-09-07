import colorama


def text_colorize(
    text,
    color=colorama.Fore.GREEN,
    bright=colorama.Style.BRIGHT,
    color_end=colorama.Style.RESET_ALL,
):
    """
    return text dengan warna untuk menunjukan text penting

    ```py
    text_colorize("Print some text")
    text_colorize("Print some text", color=colorama.Fore.RED)
    ```
    """
    return f"{color + bright}{text}{color_end}"
