from argparse import ArgumentParser
import sys
import os

BASE_CLI_NAME = os.path.basename(sys.argv[0])


def parse_args():
    parser = ArgumentParser(
        description="🚀 SFTP Client CLI – Your command-line companion for sending and fetching files to/from remote servers."
    )

    subparser = parser.add_subparsers(
        title="✨ Available Commands",
        dest="command",
        description="Choose one of the following commands to get things done.",
        metavar="commands:",
        required=True,
    )

    # Configure
    configure_config = subparser.add_parser(
        "configure",
        description="🔧 Save SFTP connection settings so you don’t have to type them every time.",
        help="Set up and save connection details (host, port, user, etc.) for easy reuse.",
        usage=f"{BASE_CLI_NAME} configure [--host] [--port] [--username] [--password] [--key] [--upload_dir] [--profile]",
    )
    configure_config.add_argument(
        "--host", help="Remote server hostname or IP.", metavar="<host>", type=str
    )
    configure_config.add_argument(
        "--port",
        help="SFTP port number (default: 22).",
        metavar="<port>",
        default=22,
        type=int,
    )
    configure_config.add_argument(
        "--username",
        help="Your login name on the remote server.",
        metavar="<username>",
        type=str,
    )
    configure_config.add_argument(
        "--password",
        help="Your secret password (shh!).",
        metavar="<password>",
        type=str,
    )
    configure_config.add_argument(
        "--key",
        help="Path to your private key for key-based login.",
        metavar="<file>",
        type=str,
    )
    configure_config.add_argument(
        "--upload_dir",
        help="Default remote upload folder (e.g., /home/user/uploads).",
        metavar="<dir>",
        type=str,
    )
    configure_config.add_argument(
        "--update",
        help="Update the config of a specific profile (must use with --profile).",
        action="store_true",
        default=False,
    )
    configure_config.add_argument(
        "--config-path",
        help="Set a new config path (e.g. --config-path /your/path) or pass ? to show the current one. Because even your config needs a home!",
        nargs="?",
        const="?"
    )
    configure_config.add_argument(
        "--profile",
        help="Optional profile name (default is 'default').",
        metavar="<name>",
        type=str,
        default="default",
    )

    # Upload
    upload_command = subparser.add_parser(
        "upload",
        description="📤 Send files from your machine to the remote server.",
        help="Upload local files to your configured SFTP server.",
    )
    upload_command.add_argument("files", nargs="*", help="Local file(s) to upload.")
    upload_command.add_argument(
        "-d",
        "--directory",
        help="Remote subdirectory to upload to.",
        metavar="<directory>",
    )

    # Download
    download_command = subparser.add_parser(
        "download",
        description="📥 Grab files from the remote server to your local machine.",
        help="Download remote files to your local system.",
    )
    download_command.add_argument(
        "files", nargs="*", help="Remote file(s) to download."
    )
    download_command.add_argument(
        "-d",
        "--directory",
        help="Local folder to save the files (default: ./downloads).",
        metavar="<directory>",
        default="downloads",
    )

    # Remove files
    remove_command = subparser.add_parser(
        "remove",
        description="🗑️ Delete file(s) from the remote server.",
        help="Remove one or more remote files.",
    )
    remove_command.add_argument(
        "files",
        nargs="*",
        help="List of remote file paths to remove.",
    )

    # List remote directory
    list_dir_command = subparser.add_parser(
        "listdir",
        description="📂 Peek into remote directories and see what’s inside.",
        help="List the contents of specified remote directories.",
    )
    list_dir_command.add_argument(
        "directories",
        nargs="*",
        help="Remote directory to list.",
        default=["."],
    )

    # Tree view of remote directory
    tree_command = subparser.add_parser(
        "tree",
        description="🌲 See a visual tree of a remote directory's contents.",
        help="Display a tree-like view of a remote directory.",
    )
    tree_command.add_argument(
        "directory",
        help="Remote directory path to display as a tree.",
        metavar="<directory>",
        default=".",
    )

    # Check if remote files/directories exist
    item_exists_command = subparser.add_parser(
        "exists",
        description="🔍 Check if a file or directory exists on the remote server.",
        help="Verify presence of remote files or folders.",
    )
    item_exists_command.add_argument(
        "files", nargs="*", help="Files or directories to check for existence."
    )

    # Make remote directory
    mkdir_command = subparser.add_parser(
        "mkdir",
        description="📁 Create one or more new folders on the remote server.",
        help="Make directories on the remote system.",
    )
    mkdir_command.add_argument("files", nargs="*", help="Remote directories to create.")

    # Remove remote directory
    rmdir_command = subparser.add_parser(
        "rmdir",
        description="🧹 Remove remote directories you no longer need.",
        help="Delete specified directories from the remote server.",
    )
    rmdir_command.add_argument("files", nargs="*", help="Remote directories to delete.")

    # Rename remote file/directory
    rename_command = subparser.add_parser(
        "rename",
        description="✏️ Rename a file or folder on the remote server.",
        help="Rename remote files or directories.",
    )
    rename_command.add_argument("old_path", help="Current name or path.")
    rename_command.add_argument("new_path", help="New name or path.")

    # Test connection
    test_connection_command = subparser.add_parser(
        "connect",
        description="🔌 Try connecting to a saved profile to test connectivity.",
        help="Test SFTP connection using a specific profile.",
    )
    test_connection_command.add_argument("profile", help="Name of the profile to test.")

    # Global profile selector
    parser.add_argument(
        "-P",
        "--profile",
        help="Specify which saved profile to use (default: 'default').",
        metavar="<name>",
        default="default",
    )

    return parser.parse_args()


if __name__ == "__main__":
    print(parse_args())
