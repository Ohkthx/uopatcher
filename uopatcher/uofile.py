import sys
import codecs
import pathlib
import hashlib
import urllib.request
from enum import Enum
from typing import Optional
from datetime import datetime

from log import Log


def progress_bar(resource: str, size: int, max_size: int,
                 start_time: datetime) -> None:
    """Shows a download progress bar for the resource."""
    percentage: float = size / max_size * 100
    size_mb = size / 1024 / 1024

    # Calculate the mb per second.
    elapsed = datetime.now() - start_time
    mbps = size_mb / elapsed.total_seconds()

    Log.info(f"Downloading: '{resource}' "
             f"[{percentage:0.2f}%] "
             f"{mbps:0.2f} mbps", end='\r')


def download_file(remote_resource: str,
                  local_resource: str,
                  chunk_size: int = 1024,
                  show_progress: bool = False,
                  ) -> tuple[int, float]:
    """Downloads a file from a remote host into a local repository.
    Returns a tuple containing (size [bytes], time [seconds])
    """
    start: datetime = datetime.now()

    # Get the stream we will be pulling from.
    request = urllib.request.urlopen(remote_resource)

    as_path = pathlib.Path(remote_resource)
    name = as_path.name

    # Calculate size of the downloaded content.
    size: int = 0
    content_length = request.getheader("content-length", None)
    if content_length:
        try:
            size = int(content_length)
        except BaseException:
            size = 0

    # Ensure the local directories exist.
    pathlib.Path(local_resource).parent.mkdir(parents=True, exist_ok=True)

    # Open the local file, download the remote, saving locally.
    has_data: bool = True
    pulled_size: int = 0
    with open(local_resource, 'wb') as f:
        while has_data:
            chunk = request.read(chunk_size)
            if not chunk or len(chunk) == 0:
                has_data = False
                continue

            # If VERBOSE is enabled in config, print the progress bar.
            if show_progress:
                pulled_size += len(chunk)
                progress_bar(name, pulled_size, size, start)

            f.write(chunk)

    elapsed = datetime.now() - start
    return size, elapsed.total_seconds()


class FileAction(Enum):
    """Actions to perform on the files."""
    NONE = "none"
    CREATE = "create"
    DELETE = "delete"


class UOFile:
    """Represents a file for Ultima Online that may need to be
    updated, removed, or untouched.
    """

    REMOTE_ROOT: str = ""
    LOCAL_ROOT: str = ""

    def __init__(self, raw_filename: str) -> None:
        cleaned = raw_filename.strip().lstrip('\\').replace('\\', '/')
        as_path = pathlib.Path(cleaned)
        self.raw_name = raw_filename
        self.parent = str(as_path.parent)
        self.name = as_path.name
        self.remote_hashes: Optional[tuple[str, str]] = None

        # Try to extract the action.
        self.action = FileAction.NONE
        if len(self.name) > 0:
            if self.name[0] not in ('-', '+'):
                return
            if self.name[0] == "-":
                self.action = FileAction.DELETE
            elif self.name[0] == "+":
                self.action = FileAction.CREATE

        # Update the name removing the action.
        if self.action != FileAction.NONE:
            self.name = self.name[1:]

    @property
    def id(self) -> str:
        """Gets the ID of the file which is typically the relative path."""
        return str(self.path)

    @property
    def path(self) -> pathlib.Path:
        """Gets the relative path for the file."""
        return pathlib.Path(self.parent, self.name)

    @property
    def remote_resource(self) -> str:
        """The remote resource where the file can be obtained."""
        return f"{UOFile.REMOTE_ROOT}/{self.path}"

    @property
    def local_resource(self) -> str:
        """The local resource where the file can be found/saved."""
        return str(pathlib.Path(UOFile.LOCAL_ROOT, self.parent, self.name))

    @property
    def local_exists(self) -> bool:
        """Checks if a local copy of the file exists."""
        return pathlib.Path(self.local_resource).is_file()

    def get_md5sum(self) -> Optional[str]:
        """Generates the md5sum for a local file if it exists."""
        if not self.local_exists:
            return None

        # Generate the md5 hash.
        hash_md5 = hashlib.md5()
        with open(self.local_resource, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest().lower()

    def download(self,
                 show_progress: bool = False,
                 ) -> Optional[tuple[int, float]]:
        """Downloads a file from the remote source.
        If successful, returns a tuple of the:
            size [bytes], time[seconds]
        """
        try:
            return download_file(self.remote_resource,
                                 self.local_resource,
                                 show_progress=show_progress)
        except KeyboardInterrupt:
            Log.warn("Interrupt detected, exiting.")
            sys.exit(1)
        except BaseException as exc:
            Log.error(f"Could not download {self.name}: {exc}")
        return None
