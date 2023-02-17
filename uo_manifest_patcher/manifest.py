from uofile import UOFile, FileAction
from updatefile import UpdateFile, Version


class Manifest(UpdateFile):
    """Represents the Manifest file."""

    def __init__(self, remote_root: str, local_root: str) -> None:
        super().__init__(filename='Manifest',
                         remote_root=remote_root,
                         local_root=local_root)
        self.version: Version = Version((0, 0, 0, 0))
        self.data: dict[str, FileAction] = {}

    def _process(self, line_data: str, line_number: int):
        """Used to process a specific line from the file."""
        # Extract the version.
        if line_number == 1:
            self.version = Version(Version.parse(line_data))
            return

        # Extract the file.
        uofile = UOFile(line_data)
        if not uofile.name or len(uofile.name) == 0:
            return

        self.add_uofile(uofile)
        self.data[uofile.id] = uofile.action
