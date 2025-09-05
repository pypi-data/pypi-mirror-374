from pathlib import Path
import posixpath

__all__ = ["NormPath"]


class NormPath:
    def __init__(self, path: str):
        self.path = path

    def __str__(self):
        return self.path

    def __repr__(self):
        return f"NormPath({self.path!r})"

    def __sanitize(self, p: str):
        return Path(p).as_posix()

    def normalize(self, is_remote: bool = False, remote_cwd: str = "/") -> str:
        """
        Normalize a file path to use forward slashes and remove redundant separators.

        Args:
            is_remote (bool): Whether the path is remote (SFTP) or local.
            remote_cwd (str): The current working directory for remote paths (used if path is relative).
        Returns:
            str: The normalized file path.
        """
        if not self.path:
            raise ValueError("The path cannot be empty.")

        if is_remote:
            # For remote paths, use posixpath to ensure forward slashes
            if not self.path.startswith("/"):
                # If the path is relative, prepend the remote current working directory
                self.path = posixpath.join(remote_cwd, self.path)
            normalized_path = Path(self.path).as_posix()
        else:
            # For local paths, use pathlib to normalize and convert to string
            normalized_path = str(Path(self.path).resolve().as_posix())

        return normalized_path

    def join(self, *paths: str, is_remote: bool = False, remote_cwd: str = "/") -> str:
        """
        Join one or more path components intelligently.

        Args:
            *paths (str): Additional path components to join.
            is_remote (bool): Whether the paths are remote (SFTP) or local.
            remote_cwd (str): The current working directory for remote paths (used if base is relative).

        Returns:
            str: The joined and normalized file path.
        """
        if not self.path:
            raise ValueError("The base path cannot be empty.")

        if is_remote:
            # For remote paths, use posixpath to join and normalize
            if not self.path.startswith("/"):
                # If the base is relative, prepend the remote current working directory
                self.path = posixpath.join(remote_cwd, self.path)
            joined_path = posixpath.join(
                self.path, *[self.__sanitize(p) for p in paths]
            )
        else:
            joined_path = str(Path(self.path).joinpath(*paths).resolve().as_posix())

        return NormPath(joined_path).normalize(
            is_remote=is_remote, remote_cwd=remote_cwd
        )
