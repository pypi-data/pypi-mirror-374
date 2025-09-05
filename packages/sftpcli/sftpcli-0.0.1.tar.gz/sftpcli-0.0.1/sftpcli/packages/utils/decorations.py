from colorama import Fore, init
import stat


init(autoreset=True)


def get_color_and_filetype(file_attr):
    # ANSI color codes
    COLOR_BLUE = Fore.LIGHTBLUE_EX  # directory
    COLOR_WHITE = Fore.LIGHTWHITE_EX  # regular file
    COLOR_GREEN = Fore.GREEN  # executable file
    COLOR_CYAN = Fore.CYAN  # symlink
    COLOR_MAGENTA = Fore.MAGENTA  # socket
    COLOR_YELLOW = Fore.YELLOW  # block/char device
    COLOR_RED = Fore.LIGHTRED_EX  # unknown

    mode = file_attr.st_mode
    if stat.S_ISDIR(mode):
        return COLOR_BLUE, "directory"
    elif stat.S_ISLNK(mode):
        return COLOR_CYAN, "link"
    elif stat.S_ISSOCK(mode):
        return COLOR_MAGENTA, "socket"
    elif stat.S_ISBLK(mode) or stat.S_ISCHR(mode):
        return COLOR_YELLOW, ""
    elif stat.S_ISREG(mode):
        if mode & stat.S_IXUSR:
            return (
                COLOR_GREEN,
                "executable",
            )  # executable file
        else:
            return COLOR_WHITE, "file"
    else:
        return COLOR_RED, ""


def print_tree(sftp, path, root: str | None = ".", prefix=""):
    try:
        items = sftp.listdir_attr(path)
    except IOError as e:
        print(prefix + "Error reading directory:", e)
        return

    if root:
        print(f"{Fore.LIGHTBLUE_EX}{root}")
        print("│")

    # Sort: dirs first, then files
    items.sort(key=lambda x: (not stat.S_ISDIR(x.st_mode), x.filename.lower()))

    total = len(items)
    for idx, item in enumerate(items):
        is_last = idx == total - 1
        connector = "└──── " if is_last else "├── "

        color, _ = get_color_and_filetype(item)
        # if connector != "├── ":
        #     print(f"{prefix}│")
        print(f"{prefix}{connector}{color}{item.filename}{Fore.RESET}")

        if stat.S_ISDIR(item.st_mode):
            new_path = f"{path}/{item.filename}".replace("//", "/")
            new_prefix = prefix + ("    " if is_last else "│   ")
            print_tree(sftp, new_path, prefix=new_prefix, root=None)
