from .int_to_int import int_to_int

def ienumerate(iterator, start=0, key=int_to_int):
    """
    meningkatkan fungsi enumerate() pada python
    untuk key menggunakan huruf dan basis angka lainnya.

    ```python
    it = ["ini", "contoh", "enumerator"]
    print(ienumerate(it))
    iprint(ienumerate(it, key=int_to_chr))
    ```
    """
    for i, v in enumerate(iterator, start):
        yield (key(i), v)
