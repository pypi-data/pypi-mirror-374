# Co-created with Google Gemini
import os
import sys
import shutil
import stat
import subprocess
import traceback
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Generator, Union

class FileInfo:
    """
    A class that encapsulates information about a file or directory.
    """
    def __init__(self, path: Union[str, Path], size: int,
                 modified_time: datetime, access_time: datetime, creation_time: datetime,
                 is_dir: bool, is_file: bool,
                 permissions: str):
        self.path: str = str(path)
        self.size: int = size
        self.modified_time: datetime = modified_time
        self.access_time: datetime = access_time
        self.creation_time: datetime = creation_time
        self.is_dir: bool = is_dir
        self.is_file: bool = is_file
        self.permissions: str = permissions

class CDContextManager:
    def __init__(self, path: Union[str, Path]) -> None:
        self.original_cwd = os.getcwd()
        os.chdir(path)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.original_cwd)

class ShellAPI:
    """
    A simple API designed to replace Linux Shell scripts.
    It unifies common file system operations and Shell command execution.
    """
    def _cp(self, s: str):
        print(f'\033[93m{s}\033[0m')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            if issubclass(exc_type, subprocess.CalledProcessError):
                print(f"\nError: Command failed with exit code {exc_val.returncode}", file=sys.stderr)
                self.exit(exc_val.returncode)
            else:
                traceback.print_exception(exc_type, exc_val, exc_tb, file=sys.stderr)
                self.exit(1)

    # --- File and Directory Operations API ---

    def home_dir(self) -> Path:
        """
        Returns the current user's home directory as a pathlib.Path object.
        """
        return Path.home()

    def path(self, path: Union[str, Path]) -> Path:
        """
        Converts a path string to a pathlib.Path object.
        """
        return Path(path)

    def create_dir(self, path: Union[str, Path], *, exist_ok: bool = False) -> None:
        """
        Creates a directory.

        :param path: The path of the directory to create.
        :param exist_ok: If True, existing directories will not raise an error.
        """
        self._cp(f"Creating directory: {path}")
        os.makedirs(path, exist_ok=exist_ok)

    def remove_dir(self, path: Union[str, Path], *, ignore_missing: bool = False) -> None:
        """
        Recursively removes a directory and its contents.

        :param path: The path of the directory to remove.
        :param ignore_missing: If True, no error is raised if the directory is missing.
        """
        if ignore_missing and not os.path.isdir(path):
            return
        self._cp(f"Removing directory: {path}")
        shutil.rmtree(path)

    def remove_file(self, path: Union[str, Path], *, ignore_missing: bool = False) -> None:
        """
        Removes a file.

        :param path: The path of the file to remove.
        :param ignore_missing: If True, no error is raised if the file is missing.
        """
        if ignore_missing and not os.path.isfile(path):
            return
        self._cp(f"Removing file: {path}")
        os.remove(path)

    def copy_file(self, src: Union[str, Path], dst: Union[str, Path], *, overwrite: bool = False) -> None:
        """
        Copies a file.

        :param src: The source file path.
        :param dst: The destination file path.
        :param overwrite: If True, overwrites the destination if it exists.
        """
        self._cp(f"Copying file from '{src}' to '{dst}'")
        if not overwrite and os.path.isfile(dst):
            raise FileExistsError(f"Destination file '{dst}' already exists.")
        shutil.copy2(src, dst)

    def copy_dir(self, src: Union[str, Path], dst: Union[str, Path], *, overwrite: bool = False) -> None:
        """
        Copies a directory.

        :param src: The source directory path.
        :param dst: The destination directory path.
        :param overwrite: If True, overwrites the destination if it exists.
        """
        self._cp(f"Copying directory from '{src}' to '{dst}'")
        if os.path.isdir(dst):
            if not overwrite:
                raise FileExistsError(f"Destination directory '{dst}' already exists.")
            shutil.rmtree(dst)
        shutil.copytree(src, dst)

    def move_file(self, src: Union[str, Path], dst: Union[str, Path], *, overwrite: bool = False) -> None:
        """
        Moves a file.

        :param src: The source file path.
        :param dst: The destination file path.
        :param overwrite: If True, overwrites the destination if it exists.
        """
        self._cp(f"Moving file from '{src}' to '{dst}'")
        if os.path.isfile(dst):
            if not overwrite:
                raise FileExistsError(f"Destination file '{dst}' already exists.")
            os.remove(dst)
        shutil.move(src, dst)

    def move_dir(self, src: Union[str, Path], dst: Union[str, Path], *, overwrite: bool = False) -> None:
        """
        Moves a directory.

        :param src: The source directory path.
        :param dst: The destination directory path.
        :param overwrite: If True, overwrites the destination if it exists.
        """
        self._cp(f"Moving directory from '{src}' to '{dst}'")
        if os.path.isdir(dst):
            if not overwrite:
                raise FileExistsError(f"Destination directory '{dst}' already exists.")
            shutil.rmtree(dst)
        shutil.move(src, dst)

    def rename_file(self, src: Union[str, Path], dst: Union[str, Path]) -> None:
        """
        Renames a file.

        :param src: The source file path.
        :param dst: The destination file path.
        """
        self._cp(f"Renaming file from '{src}' to '{dst}'")
        if not os.path.isfile(src):
            raise FileNotFoundError(f"Source file '{src}' does not exist.")
        if os.path.isfile(dst):
            raise FileExistsError(f"Destination file '{dst}' already exists.")
        os.rename(src, dst)

    def rename_dir(self, src: Union[str, Path], dst: Union[str, Path]) -> None:
        """
        Renames a directory.

        :param src: The source directory path.
        :param dst: The destination directory path.
        """
        self._cp(f"Renaming directory from '{src}' to '{dst}'")
        if not os.path.isdir(src):
            raise FileNotFoundError(f"Source directory '{src}' does not exist.")
        if os.path.isdir(dst):
            raise FileExistsError(f"Destination directory '{dst}' already exists.")
        os.rename(src, dst)

    def get_file_info(self, path: Union[str, Path]) -> FileInfo:
        """
        Retrieves detailed information about a file or directory.

        :param path: The path of the file or directory.
        :return: A FileInfo object containing detailed information.
        """
        stats = os.stat(path)
        mode = stats.st_mode
        return FileInfo(
            path=path,
            size=stats.st_size,
            modified_time=datetime.fromtimestamp(stats.st_mtime),
            access_time=datetime.fromtimestamp(stats.st_atime),
            creation_time=datetime.fromtimestamp(stats.st_ctime),
            is_dir=stat.S_ISDIR(mode),
            is_file=stat.S_ISREG(mode),
            permissions=oct(mode)[-3:]
        )

    def list_dir(self, path: Union[str, Path]) -> List[str]:
        """
        Lists all files and subdirectories within a directory.

        :param path: The directory path.
        :return: A list of all entry names.
        """
        return os.listdir(path)

    def walk_dir(self, top_dir: Union[str, Path]) -> Generator[Tuple[str, str]]:
        """
        A generator that traverses a directory and all its subdirectories,
        yielding (directory_path, filename) tuples.

        :param top_dir: The root directory to start walking from.
        :yields: (dirpath, filename) tuples.
        """
        for dirpath, dirnames, filenames in os.walk(top_dir):
            for filename in filenames:
                yield (dirpath, filename)

    def cd(self, path: Union[str, Path]):
        """
        Changes the current working directory temporarily.

        This method is designed to be used as a context manager (`with` statement).
        The original working directory will be restored automatically upon exiting
        the `with` block, even if an exception occurs.

        :param path: The path to the directory to change to.
        """
        return CDContextManager(path)

    def exists(self, path: Union[str, Path]) -> bool:
        """
        Checks if a path exists.

        :param path: The file or directory path.
        :return: True if the path exists, False otherwise.
        """
        return os.path.exists(path)

    def is_file(self, path: Union[str, Path]) -> bool:
        """
        Checks if a path is a file.

        :param path: The file path.
        :return: True if the path is a file, False otherwise.
        """
        return os.path.isfile(path)

    def is_dir(self, path: Union[str, Path]) -> bool:
        """
        Checks if a path is a directory.

        :param path: The directory path.
        :return: True if the path is a directory, False otherwise.
        """
        return os.path.isdir(path)

    def get_path_parts(self, path: Union[str, Path]) -> Tuple[str, str]:
        """
        Splits a path into its directory name and file name.

        :param path: The file or directory path.
        :return: A 2-element tuple containing (directory name, file name).
        """
        return os.path.split(path)

    def join_path(self, *parts: str) -> str:
        """
        Safely joins path components.

        :param parts: Path components to join.
        :return: The joined path string.
        """
        return os.path.join(*parts)

    # --- Shell Command Execution API ---
    def run(self,
            command: str, *,
            print_output: bool = True,
            text: bool = True,
            fail_on_error: bool = True) -> subprocess.CompletedProcess:
        """
        Executes a shell command. When print_output is True, the output is streamed
        to the console in real-time. Otherwise, it is captured and returned.

        :param command: The command string to execute.
        :param print_output: If True, streams stdout and stderr to the console. Defaults to True.
        :param text: If True, output is decoded as text.
        :param fail_on_error: If True, raises a subprocess.CalledProcessError if the command fails. Defaults to True.
        :return: A subprocess.CompletedProcess object with captured output.
        """
        self._cp(command)

        if print_output:
            # Real-time print mode: Stream output directly to the console.
            result = subprocess.run(
                command,
                shell=True,
                check=fail_on_error,
                capture_output=False,
                text=text
            )
            # Return a CompletedProcess object with empty output streams
            return subprocess.CompletedProcess(
                args=result.args,
                returncode=result.returncode,
                stdout="",
                stderr=""
            )
        else:
            # Silent mode: Capture all output and return it.
            result = subprocess.run(
                command,
                shell=True,
                check=fail_on_error,
                capture_output=True,
                text=text
            )
            return result

    # --- Script Control API ---
    def exit(self, exit_code: int = 0) -> None:
        """
        Exits the script with a specified exit code.

        :param exit_code: The exit code, defaults to 0.
        """
        sys.exit(exit_code)

sh = ShellAPI()