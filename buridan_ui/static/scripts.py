import os


def count_python_files_in_folder(folder_name) -> int:
    """Get the total number of files in a folder"""
    total_files = 0

    for _dirpath, _dirnames, filenames in os.walk(folder_name):
        total_files += len([f for f in filenames if f.endswith(".py")])

    return total_files
