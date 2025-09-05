from sftpcli.packages.utils.console import Console
import configparser
from colorama import Fore, init
from configparser import ConfigParser
import os
import sys

init(autoreset=True)


class Config:
    CONFIG_FILEPATH = os.path.join(os.environ["USERPROFILE"], ".sftp-cli", "config.ini")

    @classmethod
    def config_path(cls):
        cls._create_config(cls.CONFIG_FILEPATH)
        config = ConfigParser()
        config.read(cls.CONFIG_FILEPATH)

        if config.has_section(".settings"):
            if config.has_option(".settings", "config-path"):
                path = config.get(".settings", "config-path")
                if os.path.exists(path):
                    return path

                Console.warn(
                    f"Configuration file at '{path}' doesn't exist. Defaulting to {cls.CONFIG_FILEPATH}"
                )
                return cls.CONFIG_FILEPATH

        return cls.CONFIG_FILEPATH

    @classmethod
    def set_config_path(cls, path: str):
        if os.path.exists(path) and not os.path.isdir(path):
            Console.error(f"'{path}' must be a directory.")
            sys.exit(1)

        path = os.path.abspath(os.path.join(path, ".sftp-cli", "config.ini"))
        cls._create_config(path)
        config = ConfigParser()
        config.read(cls.CONFIG_FILEPATH)

        if not config.has_section(".settings"):
            config.add_section(".settings")

        config.set(".settings", "config-path", path)
        with open(cls.CONFIG_FILEPATH, "w") as file:
            config.write(file)
            Console.success(f"'{path}' is added to custom config-path settings.")

    @classmethod
    def _create_config(cls, config_path: str):
        config_path = os.path.abspath(config_path)
        config_dir = os.path.dirname(config_path)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir, exist_ok=True)

        if not os.path.exists(config_path):
            open(config_path, "w").close()

    @classmethod
    def save_config(
        cls,
        host: str,
        port: int,
        username: str,
        upload_dir: str = "/home/sftp-user/uploads",
        password: str | None = None,
        key: str | None = None,
        profile: str = "default",
    ):
        """Save SFTP configuration to a file."""
        if not password and not key:
            raise ValueError(
                "Either password or key must be provided for authentication."
            )

        config_filepath = cls.config_path()
        cls._create_config(config_filepath)

        config = ConfigParser()
        if os.path.exists(config_filepath):
            config.read(config_filepath)

        print(f"{Fore.WHITE}Saving configuration to {config_filepath}...")
        if not config.has_section(profile):
            config.add_section(profile)

        config.set(profile, "host", host)
        config.set(profile, "port", str(port or 22))
        config.set(profile, "username", username)
        if password and not key:
            config.set(profile, "password", password)

        if key and not password:
            config.set(profile, "key", key)

        if not password and not key:
            print(
                f"{Fore.LIGHTRED_EX}Both password and key cannot be empty. Please provide at least one for authentication."
            )
            sys.exit(1)

        if password and key:
            print(
                f"{Fore.LIGHTRED_EX}Both password and key cannot be provided. Please use one method of authentication."
            )
            sys.exit(1)

        config.set(profile, "upload_dir", upload_dir)

        with open(config_filepath, "w") as config_file:
            config.write(config_file)

        print(f"{Fore.GREEN}Configuration saved successfully to {config_filepath}\n")

    @classmethod
    def get_config(cls, profile: str = "default"):
        """Retrieve SFTP configuration from a file."""
        config_filepath = cls.config_path()
        if not os.path.exists(config_filepath):
            print(f"{Fore.LIGHTRED_EX}Configuration file not found: {config_filepath}")
            sys.exit(1)

        config = ConfigParser()
        config.read(config_filepath)

        if not config.has_section(profile):
            print(f"{Fore.LIGHTRED_EX}Profile '{profile}' not found in configuration.")
            sys.exit(1)

        try:
            return {
                "host": config.get(profile, "host"),
                "port": config.getint(profile, "port", fallback=22),
                "username": config.get(profile, "username"),
                "password": config.get(profile, "password", fallback=None),
                "key": config.get(profile, "key", fallback=None),
                "upload_dir": config.get(
                    profile,
                    "upload_dir",
                    fallback=f"/home/{config.get(profile, 'username')}/uploads",
                ),
            }
        except configparser.NoOptionError:
            print(
                f"{Fore.LIGHTRED_EX}Required configuration options are missing in profile '{profile}'."
            )
            sys.exit(1)
