from os import path
import pathlib
import configparser
from typing import Optional


class Config:
    """User defined settings that are saved locally."""
    FILENAME: str = "config.ini"

    def __init__(self, config: configparser.ConfigParser,
                 file_path: pathlib.Path) -> None:
        self.config = config
        self.file_path = file_path

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
        return self.config.getboolean('DEFAULT', 'VERBOSE', fallback=True)

    @property
    def local_root(self) -> str:
        """Local root directory for files to be saved to."""
        return self.config.get('DEFAULT', 'LOCAL_ROOT', fallback="client")

    @property
    def remote_root(self) -> str:
        """Remote root/URI for the remote source of the updates."""
        return self.config.get('DEFAULT', 'REMOTE_ROOT', fallback='unset')

    @property
    def remote_port(self) -> int:
        """Remote port number for the remote source of the updates."""
        return self.config.getint('DEFAULT', 'REMOTE_PORT', fallback=8080)

    @staticmethod
    def exists(file_path: pathlib.Path) -> bool:
        """Checks if the configuration file already exists."""
        return file_path.is_file()

    @staticmethod
    def load(file_path: pathlib.Path) -> Optional['Config']:
        """Loads the configuration file from a local file."""
        # Cannot load a non-existing file.
        if not Config.exists(file_path):
            return None

        # Load the file, initialize Config.
        config = configparser.ConfigParser()
        config.read(file_path)
        return Config(config, file_path)

    def save(self):
        """Saves the configuration file, only really used for future
        updates where additional options exist.
        """
        config = configparser.ConfigParser()
        config['DEFAULT'] = {}
        config['DEFAULT']['DEBUG'] = str(self.debug)
        config['DEFAULT']['SKIP_PROMPT'] = str(self.skip_prompt)
        config['DEFAULT']['VERBOSE'] = str(self.verbose)
        config['DEFAULT']['LOCAL_ROOT'] = str(self.local_root)
        config['DEFAULT']['REMOTE_ROOT'] = str(self.remote_root)
        config['DEFAULT']['REMOTE_PORT'] = str(self.remote_port)

        with open(self.file_path, 'w', encoding='utf-8') as f:
            config.write(f)

    @staticmethod
    def create(file_path: pathlib.Path) -> bool:
        """Creates a new configuration file if it does not exist."""
        # If the file exists, ignore.
        if Config.exists(file_path):
            return False

        # Create the default values that must be changed.
        config = configparser.ConfigParser()
        config['DEFAULT'] = {}
        config['DEFAULT']['DEBUG'] = "False"
        config['DEFAULT']['SKIP_PROMPT'] = "False"
        config['DEFAULT']['VERBOSE'] = "True"
        config['DEFAULT']['LOCAL_ROOT'] = "client"
        config['DEFAULT']['REMOTE_ROOT'] = "patch.example.com"
        config['DEFAULT']['REMOTE_PORT'] = "8080"

        # Save it locally.
        with open(file_path, 'w', encoding='utf-8') as f:
            config.write(f)
        return True
