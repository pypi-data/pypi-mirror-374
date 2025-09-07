import traceback


def traceback_filename(stack_level=-3):
    """
    Mendapatkan filename dimana fungsi yg memanggil
    fungsi dimana fungsi ini diletakkan dipanggil.

    ```py
    print(traceback_filename())
    ```
    """
    return traceback.extract_stack()[stack_level].filename
