import sys
import os
import platform
import socket
import ctypes

from pathlib import Path
import random
from tqdm import tqdm
import shutil
import subprocess
import threading
import time
import schedule

from typing import AnyStr, Dict


def get_env_variable(var_name: AnyStr, default: AnyStr = None) -> AnyStr:
    """
    Retrieves the value of an environment variable.

    Args:
        var_name (str): The name of the environment variable.
        default (optional): The default value to return if the environment variable is not found.

    Returns:
        The value of the environment variable or the specified default value.
    """
    return os.environ.get(var_name, default)


def list_environment_variables() -> Dict:
    """
    Lists all the environment variables currently set.

    Returns:
        A dictionary of environment variables and their values.
    """
    return dict(os.environ)


def verify_environment_variable(env_var_name: AnyStr, env_var_path: AnyStr) -> Path:
    """
    Ensure an environment variable points to the desired path.

    If the current value differs from `env_var_path`, this will:
      1) Persist the value using `setx` (Windows only, affects future shells).
      2) Set `os.environ[env_var_name]` in the current process so the new value
         is immediately visible.

    Parameters
    ----------
    env_var_name : str
        Name of the environment variable to enforce.
    env_var_path : str
        Desired path value for the variable. May include environment tokens.

    Returns
    -------
    Path
        The resolved path derived from the environment variable after reconciliation.

    Raises
    ------
    subprocess.CalledProcessError
        If persisting the value with `setx` fails.

    Notes
    -----
    - `setx` is Windows-specific. If you intend to support other platforms, consider
      guarding with `os.name == "nt"` or making this a no-op on non-Windows systems.
    - Paths containing spaces are safe since arguments are passed as a list.
    """
    current_value = os.environ.get(env_var_name)
    if current_value != env_var_path:
        try:
            subprocess.run(
                ["setx", env_var_name, env_var_path],
                check=True,
                shell=True,  # retained for parity with your current behavior
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            # Make it available to the current process immediately.
            os.environ[env_var_name] = env_var_path
        except subprocess.CalledProcessError as e:
            print(f"Failed to set environment variable '{env_var_name}': {e}")
            raise

    return Path(os.environ.get(env_var_name, env_var_path))


def get_os_details() -> Dict:
    """
    Returns detailed information about the operating system.

    Returns:
        A dictionary containing OS name, release, version, architecture,
        machine type, processor, and Python implementation.
    """
    return {
        "os_name": os.name,                          # 'nt', 'posix', etc.
        "platform": sys.platform,                    # 'win32', 'linux', 'darwin'
        "system": platform.system(),                 # 'Windows', 'Linux', 'Darwin'
        "release": platform.release(),               # e.g. '10', '11', '5.15.0-1051-azure'
        "version": platform.version(),               # OS version string
        "architecture": platform.architecture()[0],  # '64bit' or '32bit'
        "machine": platform.machine(),               # 'AMD64', 'x86_64', 'arm64'
        "processor": platform.processor(),           # Processor info (may be empty on some OS)
        "python_implementation": platform.python_implementation(),
        "python_version": platform.python_version(),
        "details": platform.platform(),              # Combined string like 'Windows-10-10.0.19045-SP0'
    }


def get_hostname() -> AnyStr:
    """
    Retrieves the network hostname of the current machine.

    Returns:
        The network hostname as a string.
    """
    return socket.gethostname()


def get_current_working_directory() -> AnyStr:
    """
    Gets the current working directory.

    Returns:
        The current working directory path as a string.
    """
    return os.getcwd()


def change_current_working_directory(path: AnyStr) -> bool:
    """
    Changes the current working directory to a specified path.

    Args:
        path (str): The path to change the current working directory to.
                    Can include ~ (home) or environment variables.

    Returns:
        bool: True if the directory was successfully changed, False otherwise.
    """
    try:
        # Expand ~ and environment variables
        resolved_path = Path(os.path.expandvars(os.path.expanduser(path)))

        # Check if directory exists
        if not resolved_path.exists():
            print(f"Error: Path does not exist -> {resolved_path}")
            return False
        if not resolved_path.is_dir():
            print(f"Error: Path is not a directory -> {resolved_path}")
            return False

        old_dir = os.getcwd()
        os.chdir(resolved_path)
        print(f"Changed working directory from {old_dir} to {resolved_path}")
        return True

    except PermissionError:
        print(f"Error: Permission denied -> {path}")
    except FileNotFoundError:
        print(f"Error: Directory not found -> {path}")
    except Exception as ex:
        print(f"Unexpected error while changing directory: {ex}")

    return False

