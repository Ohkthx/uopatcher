from log import Log
from uofile import UOFile


class UpdateFile(UOFile):
    """Represents a file that is required for the updates."""
    FILES: dict[str, UOFile] = {}

    def __init__(self,
                 filename: str,
                 remote_root: str,
                 local_root: str) -> None:
        UOFile.REMOTE_ROOT = remote_root
        UOFile.LOCAL_ROOT = local_root
        super().__init__(filename)

    @staticmethod
    def add_uofile(uofile: UOFile) -> None:
        """Adds a UOFile to be tracked."""
        UpdateFile.FILES[str(uofile.path)] = uofile

    @staticmethod
    def add_hashes(uofile: UOFile, hashes: tuple[str, str]) -> None:
        """Adds the remote hashes expect for a specific file."""
        local_file = UpdateFile.FILES.get(str(uofile.path), None)

        # Add the new UOFile to be tracked.
        if not local_file:
            uofile.remote_hashes = hashes
            UpdateFile.add_uofile(uofile)
            return

        # Update the existing one.
        local_file.remote_hashes = hashes

    def load(self) -> bool:
        """Loads the local version of the file."""
        if not self.local_exists:
            return False

        with open(self.local_resource, 'r', encoding='utf-8') as f:
            for n, line in enumerate(f):
                self._process(line.strip(), n + 1)

        # Trigger the post-processor if it has been set.
        try:
            self._post_process()
        except NotImplementedError:
            pass
        return True

    def update(self) -> bool:
        """Updates the file from the remote source."""
        try:
            if self.download():
                return self.load()
        except BaseException as exc:
            Log.error(f"Could not update {self.name}: {exc}")
        return False

    def _process(self, line_data: str, line_number: int):
        """Used to process a specific line from the file."""
        raise NotImplementedError("Update file needs to override processor.")

    def _post_process(self):
        """Called after the loading of the file has completed."""
        raise NotImplementedError("Post-processor is not set.")


class Version:
    def __init__(self, version: tuple[int, int, int, int]):
        self.value = version

    def __str__(self) -> str:
        return str(self.value).lstrip("(").rstrip(")").replace(", ", ".")

    def __lt__(self, other):
        """Allows for less-than comparisons between versions."""
        if not isinstance(other, Version):
            raise ValueError("Cannot compare versions, not the same type.")
        return self.value < other.value

    def __le__(self, other):
        """Allows for less-than or equal comparisons between versions."""
        if not isinstance(other, Version):
            raise ValueError("Cannot compare versions, not the same type.")
        return self.value <= other.value

    def __gt__(self, other):
        """Allows for greater-than comparisons between versions."""
        if not isinstance(other, Version):
            raise ValueError("Cannot compare versions, not the same type.")
        return self.value > other.value

    def __ge__(self, other):
        """Allows for greater-than or equal comparisons between versions."""
        if not isinstance(other, Version):
            raise ValueError("Cannot compare versions, not the same type.")
        return self.value >= other.value

    def __eq__(self, other):
        """Allows for checking equivalency between versions."""
        if not isinstance(other, Version):
            raise ValueError("Cannot compare versions, not the same type.")
        return self.value == other.value

    @staticmethod
    def parse(data: str) -> tuple[int, int, int, int]:
        raw: str = data.lstrip("[").rstrip("]")
        try:
            return tuple(map(int, raw.split(".")))
        except BaseException:
            raise ValueError(f"Could not parse the version: {data}")
