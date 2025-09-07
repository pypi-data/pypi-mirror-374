import os
import random
import shutil
from pathlib import Path
from tqdm import tqdm


def path_exists(input_path: Path) -> Path:
    """
    Verify that a path exists without creating it.

    Parameters
    ----------
    input_path : Path
        The filesystem path to verify.

    Returns
    -------
    Path
        The same path, if it exists.

    Raises
    ------
    FileNotFoundError
        If the path does not exist.

    Use cases
    ---------
    - For directories or files that must already be present, like a controlled
      "Recycle Bin" folder or shared mount point.
    """
    if input_path.exists():
        return input_path
    raise FileNotFoundError(f"The specified path '{input_path}' does not exist.")


def get_file_size(path: str) -> float | None:
    """
    Retrieves the size of a specified file in megabytes (MB).

    Args:
        path (str): The path to the file.

    Returns:
        float: The size of the file in MB (rounded to 2 decimal places),
               or None if an error occurred.
    """
    try:
        size_bytes = os.path.getsize(path)
        size_mb = round(size_bytes / (1024 ** 2), 2)
        return size_mb
    except OSError as ex:
        print(f"Error getting file size: {ex}")
        return None


def handle_network_path(input_path: str, return_as_str: bool = False):
    """
    Transforms the input path, replacing drive letter with the corresponding network path.

    Parameters:
    - input_path (str): The original path string.
    - return_as_str (bool): If True, return the path as a string, otherwise return as a Path object.

    Returns:
    - Path or str: The transformed path.
    """

    network_map = {
        'H:': r'\\icc-proc-vsf003\shares$',
        'M:': r'\\icc-proc-nas11.icc-proc.local\Volume1',
        'Q:': r'\\icc-proc-nas10.icc-proc.local\Volume1',
        'S:': r'\\ims-vsf051.ims.local\s-drive',
        'V:': r'\\icc-proc-nas9.icc-proc.local\volume1',
        'W:': r'\\icc-proc-nas7.icc-proc.local\volume1',
        'Y:': r'\\icc-proc-nas5.icc-proc.local\volume1',
        'Z:': r'\\icc-proc-nas4.icc-proc.local\volume1'
    }

    # Replace the drive letter with the network path
    for drive, network in network_map.items():
        if input_path.startswith(drive):
            input_path = input_path.replace(drive, network)
            break

    if return_as_str:
        return str(input_path)

    return Path(input_path)


def verify_directory(directory: str) -> Path:
    """
    Ensures that the specified directory exists, creating it if necessary.

    This function takes a directory path as input, either as a string or a pathlib.Path object, and ensures that the
    directory exists. If the directory does not exist, it creates the directory along with any necessary parent
    directories. The function then returns the pathlib.Path object of the existing or created directory.

    Args:
      directory (Union[str, Path]): The directory path to ensure exists.

    Returns:
        Path: The pathlib.Path object representing the existing or created directory.

    Example:
        dir_path = "path/to/your/directory"
        existing_or_created_directory = file_utils.directory_handler(dir_path)
    """
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def get_file_list(directory: str, shuffle: bool = False, extensions: list | str = None):
    """
    Retrieves a list of file paths from a specified directory, optionally filtered by extensions and shuffled.

    This method traverses the given directory (and its subdirectories) to compile a list of file paths.
    It can also filter the files based on provided extensions and randomize the order of the returned list.

    Args:
        directory (str): The directory path to search for files.
        shuffle (bool, optional): If True, the list of file paths is shuffled before being returned.
        extensions (list[str] or str, optional): A list of file extensions to include.
                                                 Files with extensions not in this list will be excluded.

    Returns:
        list: A list of file paths meeting the specified criteria.
    """
    root_path = Path(directory)

    # Ensure extensions is a list, even if a single string is given
    if isinstance(extensions, str):
        extensions = [extensions]

    if extensions:
        # Only files with the specified extensions
        file_list = [os.path.join(root, f) for ext in extensions for root, _, filenames in os.walk(root_path) for f in filenames if f.endswith(ext)]
    else:
        # All files in the directory
        file_list = [os.path.join(root, f) for root, _, filenames in os.walk(root_path) for f in filenames]

    if shuffle:
        random.shuffle(file_list)

    return file_list


def mass_copy_files(src: str, dst: str, extensions: list | str = None, move=False):
    """
    Copies or moves files from a source directory to a destination directory, optionally filtering by file extensions.

    This method copies or moves files, preserving their metadata. If the destination directory does not exist, it is created.
    Files already existing at the destination are not overwritten. The method can optionally filter files to copy/move
    based on their extensions.

    Args:
        src (str): The source directory path.
        dst (str): The destination directory path.
        extensions (list[str] or str, optional): File extensions to filter the files that need to be copied/moved.
        move (bool, optional): If True, files are moved instead of copied.

    Returns:
        None
    """
    # Ensure destination directory exists
    if not os.path.exists(dst):
        os.makedirs(dst)

    # Get the list of files to be copied
    files_to_copy = get_file_list(src, extensions=extensions)

    # Setup progress bar
    with tqdm(total=len(files_to_copy), ncols=250, leave=False, desc=f'Copying from {src}: ', position=0) as pbar:

        for file in files_to_copy:
            # Generate destination path
            relative_path = os.path.relpath(file, src)
            dst_path = os.path.join(dst, relative_path)

            # Create any necessary directories in destination
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)

            # Copy the file if it doesn't exist in the destination
            if not os.path.exists(dst_path):
                try:
                    if move:
                        shutil.move(file, dst_path)
                    else:
                        shutil.copy2(file, dst_path)
                except Exception as e:
                    print(f"Error copying {file} to {dst_path}: {e}")
            pbar.update(1)

