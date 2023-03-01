import pathlib
import configparser
from typing import Optional


class Config:
    """User defined settings that are saved locally."""
    FILENAME: str = "config.ini"

    def __init__(self, config: configparser.ConfigParser) -> None:
        self.config = config

    @property
    def debug(self) -> bool:
        """Used to print out more verbose information while running."""
        return self.config.getboolean('DEFAULT', 'DEBUG', fallback=False)

    @property
    def skip_prompt(self) -> bool:
        """Check to see if the user should be prompted for information
        or not.
        """
        return self.config.getboolean('DEFAULT', 'SKIP_PROMPT', fallback=False)

    @property
    def verbose(self) -> bool:
        """Produce additional output to the user."""
        return self.config.getboolean('DEFAULT', 'VERBOSE', fallback=False)

    @property
    def local_root(self) -> str:
        """Local root directory for files to be saved to."""
        return self.config.get('DEFAULT', 'LOCAL_ROOT', fallback="temp")

    @property
    def remote_root(self) -> str:
        """Remote root/URI for the remote source of the updates."""
        return self.config.get('DEFAULT', 'REMOTE_ROOT', fallback='unset')

    @property
    def remote_port(self) -> int:
        """Remote port number for the remote source of the updates."""
        return self.config.getint('DEFAULT', 'REMOTE_PORT', fallback=8080)

    @staticmethod
    def exists() -> bool:
        """Checks if the configuration file already exists."""
        return pathlib.Path(Config.FILENAME).is_file()

    @staticmethod
    def load() -> Optional['Config']:
        """Loads the configuration file from a local file."""
        # Cannot load a non-existing file.
        if not Config.exists():
            return None

        # Load the file, initialize Config.
        config = configparser.ConfigParser()
        config.read(Config.FILENAME)
        return Config(config)

    def save(self):
        """Saves the configuration file, only really used for future
        updates where additional options exist.
        """
        with open(Config.FILENAME, 'w', encoding='utf-8') as f:
            self.config.write(f)

    @staticmethod
    def create() -> bool:
        """Creates a new configuration file if it does not exist."""
        # If the file exists, ignore.
        if Config.exists():
            return False

        # Create the default values that must be changed.
        config = configparser.ConfigParser()
        config['DEFAULT'] = {}
        config['DEFAULT']['DEBUG'] = "False"
        config['DEFAULT']['SKIP_PROMPT'] = "False"
        config['DEFAULT']['VERBOSE'] = "False"
        config['DEFAULT']['LOCAL_ROOT'] = "temp"
        config['DEFAULT']['REMOTE_ROOT'] = "patch.example.com"
        config['DEFAULT']['REMOTE_PORT'] = "8080"

        # Save it locally.
        with open(Config.FILENAME, 'w', encoding='utf-8') as f:
            config.write(f)
        return True
