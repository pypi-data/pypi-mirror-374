from sftpcli.packages.core import SFTPClient
from sftpcli.packages.tools import parse_args
from sftpcli.packages.utils.console import Console
from sftpcli.packages.utils import (
    Config,
    NormPath,
    write_config,
    print_tree,
    get_color_and_filetype,
)
from colorama import Fore, Style
import pathlib
import sys
import os


def main(timeout: int | None = None):
    arguments = parse_args()

    if arguments.command == "configure":
        write_config(arguments)
        sys.exit(0)
        return

    if arguments.command == "connect":
        profile = arguments.profile
        config = Config.get_config(profile)

        try:
            connection = SFTPClient(
                host=config["host"],
                port=int(config["port"]),
                username=config["username"],
                password=config.get("password"),
                pkey=config.get("key"),
                timeout=2,
            )
            connection.connect()
            connection.close()
            Console.success(
                f"🚀 Woohoo! Connected to '{profile}' successfully. You're all set!\n"
            )
            sys.exit(0)
        except Exception:
            Console.error(
                f"🚫 No luck connecting to '{profile}' — the server took too long to answer (2 sec timeout). Double-check the details?\n"
            )
            sys.exit(1)

    config = Config.get_config(arguments.profile)

    with SFTPClient(
        host=config["host"],
        port=int(config["port"]),
        username=config["username"],
        password=config.get("password"),
        pkey=config.get("key"),
        timeout=timeout,
    ) as sftp_client:
        remote_path = NormPath(config["upload_dir"])
        normalized_remote_path = remote_path.normalize(
            is_remote=True,
            remote_cwd="/",
        )

        if not sftp_client.exists(normalized_remote_path):
            Console.warn(
                f"📁 Hmm... remote folder '{normalized_remote_path}' doesn’t exist yet. No worries — I’ll create it!\n"
            )
            sftp_client.mkdir(normalized_remote_path)
            Console.success(
                f"📂 Boom! '{normalized_remote_path}' is now live on the remote server.\n"
            )

        sftp_client.sftp.chdir(normalized_remote_path)

        print(
            f"{Fore.CYAN}{Style.BRIGHT}Remote working directory → {Fore.LIGHTWHITE_EX}{normalized_remote_path}"
        )
        print()
        match arguments.command:
            case "upload":
                path = remote_path.join(
                    arguments.directory or ".",
                    is_remote=True,
                    remote_cwd=normalized_remote_path,
                )
                if not sftp_client.exists(path):
                    Console.warn(
                        f"🛠️ '{path}' is missing in action — spinning it up now..."
                    )
                    sftp_client.mkdir(path)
                    Console.success(f"✨ All set — '{path}' is now ready for action.\n")

                for local_file in arguments.files:
                    local_path = NormPath(local_file)
                    normalized_local_path = local_path.normalize(is_remote=False)
                    if not pathlib.Path(normalized_local_path).exists():
                        Console.error(
                            f"❌ File not found: '{normalized_local_path}'. Maybe double-check the path?\n"
                        )
                        continue

                    upload_path = NormPath(path).join(
                        os.path.basename(local_file),
                        is_remote=True,
                        remote_cwd=normalized_remote_path,
                    )

                    Console.info(
                        f"📤 Uploading '{normalized_local_path}' → '{upload_path}'..."
                    )
                    sftp_client.upload(
                        normalized_local_path,
                        upload_path,
                    )
                    Console.success(
                        f"🎉 Boom! '{normalized_local_path}' is now on the remote server at '{upload_path}'.\n"
                    )
            case "download":
                download_path = pathlib.Path(arguments.directory)
                download_path.mkdir(exist_ok=True)
                Console.info(
                    f"Saving downloaded files inside:\n {Fore.WHITE} - '{Fore.LIGHTCYAN_EX}{Style.BRIGHT}{download_path.resolve()}'\n"
                )

                for remote_file in arguments.files:
                    file_path = download_path.joinpath(pathlib.Path(remote_file).name)
                    _remote_file = NormPath(remote_file).normalize(
                        is_remote=True, remote_cwd=normalized_remote_path
                    )

                    Console.warn(f"Downloading {_remote_file} to {file_path}")

                    if not sftp_client.exists(_remote_file):
                        Console.error(
                            f"File '{_remote_file}' does not exist on the server.\n"
                        )
                        continue

                    if file_path.exists():
                        prompt = input(
                            f"{file_path} already exists. Do you want to override? (y/N): "
                        ).lower()
                        if prompt != "y":
                            Console.warn(f"Skipping file {file_path}\n")
                            continue

                    sftp_client.download(_remote_file, file_path)
                    Console.success(f"Downloaded {file_path} successfully.\n")

            case "remove":
                for remote_file in arguments.files:
                    path = NormPath(remote_file).normalize(
                        is_remote=True, remote_cwd=normalized_remote_path
                    )
                    try:
                        sftp_client.remove(path)
                        Console.success(f"File '{path}' removed.\n")
                    except IOError as e:
                        if e.errno is None:
                            Console.error(
                                f"'{path}' is a directory. Please use rmdir command instead."
                            )
                        else:
                            Console.error(
                                f"'{path}' doesn't exists on the remote server."
                            )
                    except Exception:
                        Console.error(f"Cannot remove '{path}'.")

            case "rename":
                old_path, new_path = arguments.old_path, arguments.new_path
                old_path = NormPath(old_path).normalize(
                    is_remote=True, remote_cwd=normalized_remote_path
                )
                new_path = NormPath(new_path).normalize(
                    is_remote=True, remote_cwd=normalized_remote_path
                )

                try:
                    sftp_client.mkdir(os.path.dirname(new_path))
                except FileExistsError:
                    pass

                try:
                    sftp_client.rename(old_path, new_path)
                    Console.success(f"File renamed: {old_path} → {new_path}")
                except Exception as e:
                    Console.error(str(e))

            case "listdir":
                _files = list(set(arguments.directories))
                for remote_dir in _files:
                    path = NormPath(remote_dir).normalize(
                        is_remote=True, remote_cwd=normalized_remote_path
                    )

                    if not sftp_client.exists(path):
                        Console.error(
                            f"Directory {path} does not exist on the server.\n"
                        )
                        continue

                    Console.info(f"Listing contents of {path}...\n")
                    files = sftp_client.listdir(path)
                    if files:
                        for file in files:
                            color, filetype = get_color_and_filetype(file)
                            filename = file.longname.replace(
                                file.filename, f"{color}{file.filename}"
                            )
                            print(
                                f"{filename}{"/" if (filetype == "directory") else ""}"
                            )
                    else:
                        Console.warn(f"{path} is empty")
                    print()

            case "tree":
                remote_dir = arguments.directory
                path = NormPath(remote_dir).normalize(
                    is_remote=True, remote_cwd=normalized_remote_path
                )

                if not sftp_client.exists(path):
                    print(f"Directory {path} does not exist on the server.\n")
                    return

                print()
                print_tree(sftp_client.sftp, path, root=normalized_remote_path)
                print()

            case "mkdir":
                for remote_dir in arguments.files:
                    path = NormPath(remote_dir).normalize(
                        is_remote=True, remote_cwd=normalized_remote_path
                    )

                    try:
                        sftp_client.mkdir(path)
                        Console.success(f"Directory '{path}' created.\n")
                    except FileExistsError:
                        Console.error(f"Directory '{path}' already exists.\n")
                        continue
                    except Exception as e:
                        Console.error(str(e))

            case "rmdir":
                for remote_dir in arguments.files:
                    path = NormPath(remote_dir).normalize(
                        is_remote=True, remote_cwd=normalized_remote_path
                    )
                    try:
                        sftp_client.rmdir(path)
                        Console.success(f"Directory '{path}' removed.")
                    except FileNotFoundError as e:
                        Console.error(str(e))
                    except Exception:
                        Console.error(
                            f"'{path}' isn't an empty directory—or maybe it’s not a directory at all. Give it a look before trying again!"
                        )
                print()

            case "exists":
                print(
                    f"{Fore.LIGHTWHITE_EX}{Style.BRIGHT}Checking if file(s) exists in the remote server"
                )
                for remote_file in arguments.files:
                    path = NormPath(remote_file).normalize(
                        is_remote=True, remote_cwd=normalized_remote_path
                    )
                    exists = sftp_client.exists(path)

                    if exists:
                        print("- ", end="")
                        Console.success(path)
                    else:
                        print("- ", end="")
                        Console.error(path)
                print()


if __name__ == "__main__":
    try:
        main(5)
    except TimeoutError:
        Console.error("Cannot connect to the remote server. (timeout: 5 seconds)\n")
        sys.exit(1)
