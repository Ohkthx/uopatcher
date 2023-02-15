from typing import Optional
import requests
import configparser
import pathlib


class Settings():
    """User defined settings that are saved locally."""
    CONFIG_FILENAME: str = "config.ini"

    def __init__(self, config: configparser.ConfigParser) -> None:
        self.config = config

    @property
    def debug(self) -> bool:
        """Used to print out more verbose information while running."""
        return self.config.getboolean('DEFAULT', 'DEBUG', fallback=False)

    @property
    def hostname(self) -> str:
        """Hostname/URI for the remote source of the updates."""
        return self.config.get('DEFAULT', 'HOST', fallback='unset')

    @property
    def port(self) -> int:
        """Port number for the remote source of the updates."""
        return self.config.getint('DEFAULT', 'PORT', fallback=8080)

    @property
    def target_dir(self) -> str:
        """Local directory for files to be saved to."""
        return self.config.get('DEFAULT', 'TARGET_DIR', fallback="temp/")

    @staticmethod
    def exists() -> bool:
        """Checks if the configuration file already exists."""
        return pathlib.Path(Settings.CONFIG_FILENAME).is_file()

    @staticmethod
    def load() -> Optional['Settings']:
        """Loads the configuration file from a local file."""
        # Cannot load a non-existing file.
        if not Settings.exists():
            return None

        # Load the file, initialize Settings.
        config = configparser.ConfigParser()
        config.read(Settings.CONFIG_FILENAME)
        return Settings(config)

    @staticmethod
    def create() -> bool:
        """Creates a new configuration file if it does not exist."""
        # If the file exists, ignore.
        if Settings.exists():
            return False

        # Create the default values that must be changed.
        config = configparser.ConfigParser()
        config['DEFAULT'] = {}
        config['DEFAULT']['DEBUG'] = "False"
        config['DEFAULT']['HOST'] = "patch.example.com"
        config['DEFAULT']['PORT'] = "8080"
        config['DEFAULT']['TARGET_DIR'] = "temp/"

        # Save it locally.
        with open(Settings.CONFIG_FILENAME, 'w', encoding='utf-8') as f:
            config.write(f)
        return True


def download_file(uri: str, filename: str,
                  target_dir: str,
                  chunk_size: int = 1024):
    """Downloads a file from a remote host into a local repository."""
    # Get the stream we will be pulling from.
    stream = requests.get(f"{uri}/{filename}", stream=True)

    # Open the local file, download the remote, saving locally.
    with open(pathlib.Path(target_dir, filename), 'wb') as f:
        for chunk in stream.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)


def main():
    """Entrancce into the application."""
    # Try to load the configuration, if it fails it will be created.
    try:
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

    uri = f"{config.hostname}:{config.port}"
    manifest: str = "Manifest"

    # Ensures the destination to be saved exists.
    print("Creating space for downloads.")
    pathlib.Path(config.target_dir).mkdir(
        parents=True, exist_ok=True)

    # Pull the Manifest file as a test.
    print(f"Getting Manifest from '{uri}/{manifest}'")
    try:
        download_file(uri, manifest, config.target_dir)
    except BaseException as exc:
        print(f"[!!] Exception: {exc}")


if __name__ == "__main__":
    main()
