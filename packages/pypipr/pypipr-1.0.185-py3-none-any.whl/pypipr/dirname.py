from pathlib import Path

from .traceback_filename import traceback_filename


def dirname(path=None, indeks=-2):
    path = path or traceback_filename()
    path_obj = Path(path)
    parts = path_obj.parts
    return parts[indeks]
