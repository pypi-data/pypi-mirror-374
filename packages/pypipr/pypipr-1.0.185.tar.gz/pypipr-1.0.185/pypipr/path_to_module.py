import os

from .dirpath import dirpath


def path_to_module(path, indeks=0):
    """
    Mengubah absolute path file menjadi path modul relatif terhadap cwd (current working directory),
    dengan opsi untuk memangkas bagian akhir path berdasarkan indeks.

    Parameter:
        abs_path (str): Path absolut menuju file.
        indeks (int):
            - 0 => hasil lengkap hingga file (tanpa ekstensi),
            - -1 => tanpa nama file, hanya foldernya,
            - -2 => dua folder di atasnya, dst.

    Returns:
        str: Path bergaya modul Python (dipisah dengan ".")
    """
    path = dirpath(path, abs_path=False, indeks=indeks)
    return path.replace(os.sep, ".")
