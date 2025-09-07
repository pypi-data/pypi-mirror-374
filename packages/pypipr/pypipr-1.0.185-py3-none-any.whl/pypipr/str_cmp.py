def str_cmp(t1, t2):
    """
    Membandingakan string secara incase-sensitive menggunakan lower().
    Lebih cepat dibandingkan upper(), casefold(), re.fullmatch(), len().
    perbandingan ini sangat cepat, tetapi pemanggilan fungsi ini membutuhkan
    overhead yg besar.

    ```python
    print(str_cmp('teks1', 'Teks1'))
    ```
    """
    return t1.lower() == t2.lower()
