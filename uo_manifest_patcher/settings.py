import pathlib
import configparser
from typing import Optional


class Settings:
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
