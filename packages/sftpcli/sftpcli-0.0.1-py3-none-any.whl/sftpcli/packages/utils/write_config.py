from sftpcli.packages.utils.config import Config
from sftpcli.packages.utils.console import Console
from colorama import Fore, Style, init
from pwinput import pwinput
import sys


init(autoreset=True)


def write_config(arguments):
    """Write SFTP configuration to a file."""
    if arguments.config_path == "?":
        print(
            f"{Fore.LIGHTWHITE_EX}{Style.BRIGHT}Configuration file is currently located at:\n - {Fore.LIGHTCYAN_EX}{Config.config_path()}\n"
        )
        sys.exit(0)
    elif arguments.config_path:
        Config.set_config_path(arguments.config_path)

    if arguments.update:
        if not arguments.profile:
            Console.error(
                "❌ --profile is required when using --update. Please specify the profile to update."
            )
            sys.exit(1)

        config = Config.get_config(arguments.profile)

        profile = arguments.profile
        host = arguments.host or config["host"]
        port = arguments.port or config["port"]
        username = arguments.username or config["username"]
        password = arguments.password or config["password"]
        key = arguments.key or config["key"]
        upload_dir = str(arguments.upload_dir or config["upload_dir"])
    else:
        host: str = arguments.host or input("Enter SFTP host: ")
        port: int = arguments.port or int(input("Enter SFTP port (default 22): ") or 22)
        username: str = arguments.username or input("Enter SFTP username: ")
        password: str | None = (
            arguments.password
            or pwinput("Enter SFTP password (leave empty for key-based auth): ")
            or None
        )
        key: str | None = (
            arguments.key
            or input("Enter path to private key file (leave empty for password auth): ")
            or None
        )
        profile: str = (
            input("Enter profile name (default is 'default'): ") or "default"
            if arguments.profile == "default"
            else arguments.profile
        )

        updir = f"/home/{username}"
        upload_dir: str | None = (
            arguments.upload_dir
            or input(f"Enter upload directory (default is {updir}): ")
            or updir
        )

    if not password and not key:
        print(
            "Both password and key cannot be empty. Please provide at least one for authentication."
        )
        sys.exit(1)

    Config.save_config(
        host=host,
        port=port,
        username=username,
        password=password,
        key=key,
        profile=profile,
        upload_dir=upload_dir,
    )
