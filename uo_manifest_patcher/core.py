import os
import sys
import pathlib
from datetime import datetime

from log import Log
from uofile import FileAction
from hashes import Hashes
from config import Config
from manifest import Manifest


def pull_updates(manifest: Manifest, hashes: Hashes) -> int:
    """Pulls updates from the remote server."""
    total_size: int = 0
    for file_id, uofile in manifest.FILES.items():
        Log.info(f"Checking: '{uofile.name}'", end='\r')

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
            Log.info(f"Skipped: '{uofile.name}'", end='\r')
            continue
        elif action == FileAction.DELETE:
            Log.info(f"Removing: '{uofile.name}'", end='\r')
            if uofile.local_exists:
                try:
                    os.remove(uofile.local_resource)
                    Log.info(f"Removed: '{uofile.name}'", end='\r')
                except FileNotFoundError:
                    Log.error(f"File cannot be deleted: '{file_id}'")
                del hashes.local_hashes[file_id]
                del hashes.sizes[file_id]
                continue

        Log.info(f"Downloading: '{uofile.name}'", end='\r')
        stats = uofile.download()
        if not stats:
            Log.error(f"Failed: '{uofile.name}'")
        else:
            # Add to the download size.
            mbps = (stats[0] / 1024 / 1024) / stats[1]
            Log.info(f"Downloaded: '{uofile.name}', {mbps:0.2f} mbps")
            size = hashes.sizes.get(file_id, None)
            if size and size > 0:
                total_size = total_size + size
    Log.clear()
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
        Log.info(f"Loading configuration file: '{Config.FILENAME}'\n")
        config = Config.load()
    except BaseException as err:
        Log.error(f"Error while loading configuration file:\n{str(err)}")
        return

    if not config:
        Log.warn(f"Configuration file '{Config.FILENAME}' does not exist.")
        if Config.create():
            Log.info(f"Default config: '{Config.FILENAME}' created.")
        return

    # Set the debug information.
    Log.debug_mode = config.debug

    # Ask the user for permission.
    if not config.skip_prompt and not confirm_location(config.local_root):
        sys.exit(0)
    print("\n")
    Log.info("Checking for updates.")

    uri = f"{config.remote_root}:{config.remote_port}"

    # Load the local manifest, if it does not exist, get it.
    manifest = Manifest(uri, config.local_root)
    loaded = manifest.load()
    if not loaded:
        Log.warn("Local Manifest missing, downloading new one.")
        if not manifest.update():
            raise ConnectionError("Could not download remote Manifest.")

    # Was able to load a local manifest, check for updates.
    if loaded:
        version = manifest.version
        if not manifest.update():
            raise ConnectionError("Could not download remote Manifest.")

        # Check if the local is newer or the same.
        if version >= manifest.version:
            Log.info("Already have the most up-to-date Manifest.")

    Log.info(f"Manifest Version: '{manifest.version}'\n")

    # Build the hashes.
    hashes = Hashes(uri, config.local_root)
    Log.info(f"Updating '{hashes.name}' file.")
    hashes.update()
    Log.info("Generating local hashes.\n")
    hashes.build_localhash()

    # Start checking for updates.
    Log.info("Getting updates.")
    timestamp: datetime = datetime.now()
    size = pull_updates(manifest, hashes)
    timelength = datetime.now() - timestamp

    # Print some statistics.
    size_mb = size / 1024 / 1024
    time_sec = timelength.total_seconds()
    print("\n")
    Log.info(f"Download rate: {(size_mb / time_sec):0.2f} mbps")
    Log.info(f"Total time: {(time_sec/60):0.2f} min")
    Log.info(f"Total size: {(size_mb / 1024):0.2f} gb ({size_mb:0.2f} mb)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        Log.warn("Interrupt detected, exiting.")
        sys.exit(1)
    except BaseException as exc:
        Log.error(str(exc))
