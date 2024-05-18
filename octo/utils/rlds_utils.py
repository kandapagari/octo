import os
from typing import Set


def find_datasets(log_dirs=['logs']) -> Set[str]:
    """
    Finds dataset directories within specified log directories
    that contain 'features.json'.

    Args:
        log_dirs (list of str): Directories to search for datasets.

    Returns:
        list of str: A list of dataset directories.
    """
    dataset_dirs = set()

    def search_dirs(dir_path: str):
        # Iterate over each item in the current directory
        for item in os.listdir(dir_path):
            full_path = os.path.join(dir_path, item)
            # If the item is a directory, recursively search it
            if os.path.isdir(full_path):
                search_dirs(full_path)
            # If the item is 'features.json', add its directory to the list
            elif item == 'features.json':
                dataset_dirs.add(os.path.dirname(full_path))
                break

    # Iterate over each directory in log_dirs and search it
    for log_dir in log_dirs:
        if os.path.exists(log_dir):
            search_dirs(log_dir)
        else:
            print(f"Warning: The directory {log_dir} does not exist.")
    return dataset_dirs
