from pathlib import Path


def repath(
    path,
    folder_name=None,
    prepand_folder=None,
    append_folder=None,
    file_name=None,
    prepand_filename=None,
    append_filename=None,
    extension=None,
    prepand_extension=None,
    append_extension=None,
):
    path = Path(path)

    # Handle the directory (folder) part
    parent = path.parent
    if folder_name is not None:
        parent = Path(folder_name)
    if prepand_folder is not None:
        parent = Path(prepand_folder) / parent
    if append_folder is not None:
        parent = parent / append_folder

    # Handle the file name part
    name = path.stem  # Gets the file name without the extension
    if file_name is not None:
        name = file_name
    if prepand_filename is not None:
        name = prepand_filename + name
    if append_filename is not None:
        name = name + append_filename

    # Handle the extension part
    ext = path.suffix  # Gets the file extension (including the dot)
    if extension is not None:
        ext = extension
    if prepand_extension is not None:
        ext = prepand_extension + ext
    if append_extension is not None:
        ext = ext + append_extension

    # Combine everything into a new path
    new_path = parent / (name + ext)

    return new_path
