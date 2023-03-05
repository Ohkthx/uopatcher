#!/usr/bin/env python3

import os
import sys
import json
import pathlib
import argparse
import urllib.request
from datetime import datetime

from log import Log
from uofile import FileAction
from hashes import Hashes
from config import Config
from manifest import Manifest


class OPTS:
    LVERSION: tuple[int, int, int] = (1, 0, 4)
    RVERSION: tuple[int, int, int] = (0, 0, 0)
    ONLY_UPDATE: bool = False
    ONLY_VERSION: bool = False


# Make sure the python version satisfies the requirement.
if sys.version_info < (3, 9, 1):
    Log.error("Python needs to be at least version 3.9.1")
    sys.exit(1)


def parse_args() -> None:
    """Parse the arguments passed to the patcher."""
    parser = argparse.ArgumentParser(description="Install and Patch UO.")
    parser.add_argument("--has-update",
                        action="store_true",
                        dest="only_update",
                        help="Checks if an update is available or not.")
    parser.add_argument("--version",
                        action="store_true",
                        dest="only_version",
                        help="Returns the version of the script.")
    args = parser.parse_args()
    OPTS.ONLY_UPDATE = args.only_update
    OPTS.ONLY_VERSION = args.only_version


def print_version(version: tuple[int, int, int]):
    """Translates a version from a tuple to a string."""
    return '.'.join(map(str, version))


def needs_update() -> bool:
    """Checks to see if a newer patcher version exists on GitHub."""
    # Attempt to get the version that GitHub is currently on.
    remote_readme: str = "https://raw.githubusercontent.com/Ohkthx/uopatcher/main/README.md"
    with urllib.request.urlopen(remote_readme) as remote:
        try:
            # Read the first line and decode the version.
            encoded_version = remote.readline().decode().strip()
            decoded_version = json.loads(encoded_version)
            OPTS.RVERSION = tuple(decoded_version['version'])
        except BaseException:
            raise ValueError("Could not parse patcher's "
                             "remote version from README.md.")

    # Check for version mismatch.
    return OPTS.LVERSION < OPTS.RVERSION


def pull_updates(manifest: Manifest,
                 hashes: Hashes,
                 verbose: bool) -> int:
    """Pulls updates from the remote server."""
    total_size: int = 0
    for file_id, uofile in manifest.FILES.items():
        Log.notify(f"Checking: '{uofile.name}'", end='\r')

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

        Log.notify(f"Downloading: '{uofile.name}'", end='\r')
        stats = uofile.download(show_progress=verbose)
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
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            res = input(f" Directory does not exist:\n {local_root}\n\n"
                        " Do you wish to continue ([Y]es / [N]o)? ")
            if res.lower() in ("y", "yes", "n", "no"):
                valid_input = True
                if res.lower() in ("y", "yes"):
                    return True
    while not valid_input:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        res = input(f" Directory exists, downloading to:\n {local_root}\n\n"
                    " Do you wish to continue ([Y]es / [N]o)? ")
        if res.lower() in ("y", "yes", "n", "no"):
            valid_input = True
            if res.lower() in ("y", "yes"):
                return True
    return False


def main():
    """Entrance into the application."""
    # Try to load the configuration, if it fails it will be created.
    try:
        Log.notify(f"Loading configuration file: '{Config.FILENAME}'\n")
        config = Config.load()
    except BaseException as err:
        Log.error(f"Error while loading configuration file:\n{str(err)}")
        return

    if not config:
        Log.warn(f"Configuration file '{Config.FILENAME}' does not exist.")
        if Config.create():
            Log.notify(f"Default config: '{Config.FILENAME}' created.")
        return

    # Save the configuration in case an update added additional options.
    config.save()

    # Set the debug information.
    Log.debug_mode = config.debug
    Log.verbose_mode = config.verbose

    # Ask the user for permission.
    if not config.skip_prompt:
        if not confirm_location(config.local_root):
            sys.exit(0)
        print("")
    Log.notify("Checking for updates.")

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
            Log.notify("Already have the most up-to-date Manifest.")

    Log.notify(f"Manifest Version: '{manifest.version}'\n")

    # Build the hashes.
    hashes = Hashes(uri, config.local_root)
    Log.notify(f"Updating '{hashes.name}' file.")
    hashes.update()
    Log.notify("Generating local hashes.\n")
    hashes.build_localhash()

    # Start checking for updates.
    Log.notify("Getting updates.")
    timestamp: datetime = datetime.now()
    size = pull_updates(manifest, hashes, config.verbose)
    timelength = datetime.now() - timestamp

    # Print some statistics.
    size_mb = size / 1024 / 1024
    time_sec = timelength.total_seconds()
    print("\n")
    Log.notify("All files are up-to-date.")
    Log.notify(f"Download rate: {(size_mb / time_sec):0.2f} mbps")
    Log.notify(f"Total time: {(time_sec/60):0.2f} min")
    Log.notify(f"Total size: {(size_mb / 1024):0.2f} gb ({size_mb:0.2f} mb)")


if __name__ == "__main__":
    parse_args()
    update_exists: bool = False
    try:
        update_exists = needs_update()
    except BaseException as exc:
        Log.error(f"Critical Error: [{type(exc)}] {exc}")
        exit(1)

    # Process the arguments passed.
    if OPTS.ONLY_UPDATE:
        # Intentionally not casting to int here.
        sys.exit(1 if update_exists else 0)
    elif OPTS.ONLY_VERSION:
        print(print_version(OPTS.LVERSION))
        sys.exit(0)

    try:
        Log.notify(f"Local Patcher Version:  {print_version(OPTS.LVERSION)}")
        Log.notify(f"Remote Patcher Version: {print_version(OPTS.RVERSION)}\n")
        if update_exists:
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            Log.warn("Update for the patcher is available at:\n"
                     "\thttps://github.com/Ohkthx/uopatcher")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n")
        main()
    except SystemExit:
        pass
    except KeyboardInterrupt:
        Log.warn("Interrupt detected, exiting.")
        sys.exit(1)
    except BaseException as exc:
        Log.error(f"Critical Error: {exc}")
