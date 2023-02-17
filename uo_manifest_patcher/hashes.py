from uofile import UOFile
from updatefile import UpdateFile


class Hashes(UpdateFile):
    """Represents the Hashes file."""

    def __init__(self, remote_root: str, local_root: str) -> None:
        super().__init__(filename='Hashes',
                         remote_root=remote_root,
                         local_root=local_root)
        self.sizes: dict[str, int] = {}
        self.local_hashes: dict[str, str] = {}

    def build_localhash(self) -> None:
        """Generates all the local md5 hashes for the files"""
        for file_id, uofile in self.FILES.items():
            md5sum = uofile.get_md5sum()
            if md5sum:
                self.local_hashes[file_id] = md5sum

    def _process(self, line_data: str, _: int):
        """Extracts information for the file."""
        # Filename, Hash, Hash, Size
        data = line_data.split('\t')

        # Ignore bad inputs.
        if len(data) < 3:
            return

        uofile = UOFile(data[0])
        if not uofile.name or len(uofile.name) == 0:
            return

        # Attempt to extract the size.
        size: int = -1
        try:
            if len(data) >= 4:
                size = int(data[3])
        except BaseException:
            size = -1

        # Update the hashes.
        self.add_hashes(uofile, (data[1].lower(), data[2].lower()))
        self.sizes[uofile.id] = size
