# is_empty()
__empty_list__ = [None, False, 0, -0]
__empty_list__ += ["0", "", "-0", "\n", "\t"]
__empty_list__ += [set(), dict(), list(), tuple()]


def is_empty(variable, empty=__empty_list__):
    """
    Mengecek apakah variable setara dengan nilai kosong pada empty.

    Pengecekan nilai yang setara menggunakan simbol '==', sedangkan untuk
    pengecekan lokasi memory yang sama menggunakan keyword 'is'

    ```python
    print(is_empty("teks"))
    print(is_empty(True))
    print(is_empty(False))
    print(is_empty(None))
    print(is_empty(0))
    print(is_empty([]))
    ```
    """
    for e in empty:
        if variable == e:
            return True
    return False
