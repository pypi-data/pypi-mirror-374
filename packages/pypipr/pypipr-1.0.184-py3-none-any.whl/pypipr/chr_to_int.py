def chr_to_int(s, start=0, numbers="abcdefghijklmnopqrstuvwxyz"):
    """
    Fungsi ini berguna untuk mengubah urutan huruf menjadi angka.

    ```python
    print(chr_to_int('z'))  # Output: 26
    print(chr_to_int('aa'))  # Output: 27
    print(chr_to_int('abc', numbers="abc"))  # Output: 18
    ```
    """
    result = 0
    digit = len(numbers)
    for char in s:
        result = result * digit + numbers.index(char) + 1
    return result + start - 1
