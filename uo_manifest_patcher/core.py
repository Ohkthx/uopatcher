import os
import sys
import pathlib
from datetime import datetime

from uofile import FileAction
from hashes import Hashes
from settings import Settings
from manifest import Manifest


def pull_updates(manifest: Manifest, hashes: Hashes) -> int:
    """Pulls updates from the remote server."""
    total_size: int = 0
    for file_id, uofile in manifest.FILES.items():
        print(f"[--] Checking: '{uofile.path}'", end='\r')

        # Check if the local version exists.
        action: FileAction = FileAction.NONE
        local_hash = hashes.local_hashes.get(file_id, None)
        if not local_hash and uofile.action != FileAction.DELETE:
            # Files needs to be downloaded.
            action = FileAction.CREATE

        if not uofile.remote_hashes:
            # File does not exist in the remote, delete it locally.
            action = FileAction.DELETE
        elif local_hash and local_hash not in uofile.remote_hashes:
            # Mismatched hashes, get the remote version.
            action = FileAction.CREATE

        # Perform the non-create actions.
        if action == FileAction.NONE:
            print(f"[++] Skipping: '{file_id}'", end='\r')
            continue
        elif action == FileAction.DELETE:
            print(f"[++] Removing: '{file_id}'")
            if uofile.local_exists:
                try:
                    os.remove(uofile.local_resource)
                except FileNotFoundError:
                    print(f"[!!] File cannot be deleted: '{file_id}'")
                del hashes.local_hashes[file_id]
                del hashes.sizes[file_id]
                continue

        print(f"[--] Downloading: '{file_id}'", end='\r')
        stats = uofile.download()
        if not stats:
            print(f"[!!] Failed Download: '{file_id}'")
        else:
            # Add to the download size.
            mbps = (stats[0] / 1024 / 1024) / stats[1]
            print(f"[++] File Obtained: '{file_id}', {mbps:0.2f} mbps")
            size = hashes.sizes.get(file_id, None)
            if size and size > 0:
                total_size = total_size + size
    return total_size


def confirm_location(local_root: str) -> bool:
    """Asks the user to verify the patch location."""
    path = pathlib.Path(local_root)
    valid_input: bool = False
    if not path.is_dir():
        while not valid_input:
            res = input(f"Directory does not exist:\n{local_root}\n\n"
                        "Do you wish to continue ([Y]es / [N]o)? ")
            if res.lower() in ("y", "yes", "n", "no"):
                valid_input = True
                if res.lower() in ("y", "yes"):
                    return True
    while not valid_input:
        res = input(f"Directory exists, downloading to:\n{local_root}\n\n"
                    "Do you wish to continue ([Y]es / [N]o)? ")
        if res.lower() in ("y", "yes", "n", "no"):
            valid_input = True
            if res.lower() in ("y", "yes"):
                return True
    return False


def main():
    """Entrance into the application."""
    # Try to load the configuration, if it fails it will be created.
    try:
        print(f"\nLoading configuration file: '{Settings.CONFIG_FILENAME}'\n")
        config = Settings.load()
    except BaseException as err:
        print(f"Error while loading configuration file:\n{str(err)}")
        return

    if not config:
        print(f"Configuration file '{Settings.CONFIG_FILENAME}' "
              "does not exist.")
        if Settings.create():
            print(f"Default config: '{Settings.CONFIG_FILENAME}' created.")
        return

    # Ask the user for permission.
    if not confirm_location(config.target_dir):
        sys.exit(0)
    print("\n\nChecking for updates.")

    uri = f"{config.hostname}:{config.port}"

    # Load the local manifest, if it does not exist, get it.
    manifest = Manifest(uri, config.target_dir)
    loaded = manifest.load()
    if not loaded:
        print("[!!] Local Manifest missing, downloading new one.")
        if not manifest.update():
            raise ConnectionError("Could not download remote Manifest.")

    # Was able to load a local manifest, check for updates.
    if loaded:
        version = manifest.version
        if not manifest.update():
            raise ConnectionError("Could not download remote Manifest.")

        # Check if the local is newer or the same.
        if version >= manifest.version:
            print("Already have the most up-to-date Manifest.")

    print(f"Manifest Version: '{manifest.version}'\n")

    hashes = Hashes(uri, config.target_dir)
    print(f"Updating '{hashes.name}' file.")
    hashes.update()
    print("Generating local hashes.\n")
    hashes.build_localhash()

    timestamp: datetime = datetime.now()
    size = pull_updates(manifest, hashes)
    timelength = datetime.now() - timestamp

    size_mb = size / 1024 / 1024
    time_sec = timelength.total_seconds()
    print(f"\nDownload rate: {(size_mb / time_sec):0.2f} mbps")
    print(f"Total time: {(time_sec/60):0.2f} min")
    print(f"Total size: {(size_mb / 1024):0.2f} gb ({size_mb:0.2f} mb)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupt detected, exiting.")
        sys.exit(1)
