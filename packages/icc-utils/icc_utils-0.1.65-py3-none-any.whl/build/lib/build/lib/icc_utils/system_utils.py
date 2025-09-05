import sys
import os
import ctypes
import socket
from pathlib import Path
import random
from tqdm import tqdm
import shutil
import subprocess
import threading
import time
import schedule


class SystemUtils:

    @staticmethod
    def get_env_variable(var_name, default=None):
        """
        Retrieves the value of an environment variable.

        Args:
            var_name (str): The name of the environment variable.
            default (optional): The default value to return if the environment variable is not found.

        Returns:
            The value of the environment variable or the specified default value.
        """
        return os.environ.get(var_name, default)

    @staticmethod
    def get_os_details():
        """
        Returns details about the operating system.

        Returns:
            A dictionary containing the OS name, platform, and version.
        """
        return {
            "name": os.name,
            "platform": sys.platform,
            "version": os.uname().version if hasattr(os, 'uname') else "N/A"
        }

    @staticmethod
    def is_admin():
        """
        Checks if the current user has administrative privileges.

        Returns:
            True if the user has administrative privileges, False otherwise.
        """
        try:
            return os.getuid() == 0
        except AttributeError:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0

    @staticmethod
    def get_onedrive_root():
        """
        Retrieves the path to the OneDrive root folder from environment variables.

        Returns:
            The OneDrive root folder path, or None if not found.
        """
        return os.environ.get('OneDrive', default=None)

    @staticmethod
    def get_hostname():
        """
        Retrieves the network hostname of the current machine.

        Returns:
            The network hostname as a string.
        """
        return socket.gethostname()

    @staticmethod
    def list_environment_variables():
        """
        Lists all the environment variables currently set.

        Returns:
            A dictionary of environment variables and their values.
        """
        return dict(os.environ)

    @staticmethod
    def get_current_working_directory():
        """
        Gets the current working directory.

        Returns:
            The current working directory path as a string.
        """
        return os.getcwd()

    @staticmethod
    def change_current_working_directory(path):
        """
        Changes the current working directory to a specified path.

        Args:
            path (str): The path to change the current working directory to.

        Returns:
            True if the directory was successfully changed, False otherwise.
        """
        try:
            os.chdir(path)
            return True
        except Exception as ex:
            print(f"Error changing directory: {ex}")
            return False

    @staticmethod
    def path_exists(path):
        """
        Checks if a specified path exists.

        Args:
            path (str): The path to check.

        Returns:
            True if the path exists, False otherwise.
        """
        return os.path.exists(path)

    @staticmethod
    def get_file_size(path):
        """
        Retrieves the size of a specified file.

        Args:
            path (str): The path to the file.

        Returns:
            The size of the file in bytes, or None if an error occurred.
        """
        try:
            return os.path.getsize(path)
        except OSError as ex:
            print(f"Error getting file size: {ex}")
            return None

    @staticmethod
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

    @staticmethod
    def directory_handler(directory: [str, Path]):
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

    @staticmethod
    def get_file_list(directory, shuffle=False, extensions=None):
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

    def mass_copy_files(self, src, dst, extensions=None, move=False):
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
        files_to_copy = self.get_file_list(src, extensions=extensions)

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

    @staticmethod
    def find_onedrive_exe():
        """
        Locates the OneDrive executable file on the system.

        This method checks common installation paths for the OneDrive executable. It returns the path if found,
        otherwise, it returns None.

        Returns:
            str or None: The path to the OneDrive executable if found, otherwise None.
        """
        user_path = os.path.expanduser(r"~\AppData\Local\Microsoft\OneDrive\OneDrive.exe")
        x86_path = r"C:\Program Files (x86)\Microsoft OneDrive\OneDrive.exe"
        regular_path = r"C:\Program Files\Microsoft OneDrive\OneDrive.exe"

        if os.path.exists(user_path):
            return user_path
        elif os.path.exists(x86_path):
            return x86_path
        elif os.path.exists(regular_path):
            return regular_path
        else:
            return None

    def force_restart_onedrive(self):
        """
        Forcefully restarts the OneDrive application.

        This method first checks if the OneDrive process is running and terminates it if it is. Then, it restarts OneDrive.
        It handles any errors that occur during this process and prints an error message if the operation fails.

        Returns:
            None
        """

        # Command to check if OneDrive is running
        check_cmd = ["powershell", "Get-Process OneDrive -ErrorAction SilentlyContinue"]

        # Command to close OneDrive
        close_cmd = ["powershell", "Kill -Name OneDrive -Force"]

        # Command to launch OneDrive
        onedrive_path = self.find_onedrive_exe()

        launch_cmd = ["powershell", f"Start '{onedrive_path}'"]

        try:
            # Check if OneDrive is running
            result = subprocess.run(check_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # If the result's stdout is not empty, then OneDrive process exists
            if result.stdout.strip():
                subprocess.run(close_cmd, check=True)

            # Execute the launch command
            subprocess.run(launch_cmd, check=True)
        except subprocess.CalledProcessError as ex:
            print(f"Command failed with error: {ex}")

