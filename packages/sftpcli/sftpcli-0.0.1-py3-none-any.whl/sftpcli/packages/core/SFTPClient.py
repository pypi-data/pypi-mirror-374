import posixpath
from typing import Optional, cast
import paramiko


class SFTPClient:
    """
    A secure FTP client wrapper using Paramiko for common remote file operations.

    Supports password or private-key based authentication and provides convenience
    methods for uploading, downloading, renaming, and managing files/directories.
    """

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: Optional[str] = None,
        pkey: Optional[paramiko.PKey] = None,
        timeout: int | None = None,
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.pkey = pkey
        self.__timeout = timeout

        self.__ssh: Optional[paramiko.SSHClient] = None
        self.__sftp: Optional[paramiko.SFTPClient] = None

    def connect(self):
        """Establish an SSH connection and open an SFTP session."""
        if self.__ssh and self.__sftp:
            return  # already connected

        self.__ssh = paramiko.SSHClient()
        self.__ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if self.pkey:
            self.__ssh.connect(
                self.host,
                port=self.port,
                username=self.username,
                pkey=self.pkey,
                timeout=self.__timeout,
            )
        else:
            self.__ssh.connect(
                self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=self.__timeout,
            )

        self.__sftp = self.ssh.open_sftp()

    @property
    def sftp(self) -> paramiko.SFTPClient:
        """Lazy getter for the SFTP connection."""
        if not self.__sftp:
            self.connect()
        return cast(paramiko.SFTPClient, self.__sftp)

    @sftp.setter
    def sftp(self, value):
        """Lazy setter for the SFTP connection."""
        self.__sftp = value

    @property
    def ssh(self) -> paramiko.SSHClient:
        """Lazy getter for the SSH connection."""
        if not self.__ssh:
            self.connect()
        return cast(paramiko.SSHClient, self.__ssh)

    @ssh.setter
    def ssh(self, value):
        """Lazy setter for the SSH connection."""
        self.__ssh = value

    def upload(self, local_path, remote_path):
        """Upload a file to the remote server."""
        self.sftp.put(local_path, remote_path)

    def download(self, remote_path, local_path):
        """Download a file from the remote server."""
        self.sftp.get(remote_path, local_path)

    def listdir(self, remote_path):
        """List files and directories in a remote path."""
        return self.sftp.listdir_attr(remote_path)

    def exists(self, remote_path):
        """Check whether a file or directory exists on the remote server."""
        try:
            self.sftp.stat(remote_path)
            return True
        except FileNotFoundError:
            return False

    def remove(self, remote_path):
        """Delete a file on the remote server."""
        self.sftp.remove(remote_path)

    def normalize_path(self, path: str):
        """Normalize the path (remote)"""
        return self.sftp.normalize(path)

    def mkdir(self, remote_path: str):
        """Create a new directory on the remote server."""
        remote_path = posixpath.normpath(remote_path)
        if self.exists(remote_path):
            raise FileExistsError(f"'{remote_path}' already exists.")

        dirs = remote_path.split("/")

        current_path = "/"
        for directory in dirs:
            if not directory:
                continue

            current_path = posixpath.join(current_path, posixpath.normpath(directory))
            try:
                self.sftp.mkdir(current_path)
            except Exception:
                pass

    def rmdir(self, remote_path):
        """Remove a directory from the remote server."""
        try:
            self.sftp.rmdir(remote_path)
        except FileNotFoundError:
            raise FileNotFoundError(f"Directory {remote_path} does not exist.")
        except OSError as e:
            raise OSError(f"Failed to remove directory '{remote_path}': {e}")

    def rename(self, old_path, new_path):
        """Rename a file or directory on the remote server."""
        try:
            self.sftp.rename(old_path, new_path)
        except FileNotFoundError:
            raise FileNotFoundError(f"File {old_path} does not exist on the server.")
        except OSError as e:
            raise OSError(f"Failed to rename '{old_path}': {e}")

    def chmod(self, remote_path, mode):
        """Change file permissions on the remote server."""
        try:
            self.sftp.chmod(remote_path, mode)
        except FileNotFoundError:
            raise FileNotFoundError(f"File {remote_path} does not exist on the server.")
        except Exception as e:
            raise RuntimeError(f"Failed to chmod '{remote_path}': {e}")

    def get_file_size(self, remote_path):
        """Get the size of a file on the remote server."""
        self.connect()
        try:
            return self.sftp.stat(remote_path).st_size
        except FileNotFoundError:
            print(f"File {remote_path} does not exist on the server.")
            return None
        except Exception as e:
            print(f"Error getting file size for {remote_path}: {e}")
            return None

    def close(self):
        """Close the SFTP and SSH connections."""
        if self.__sftp:
            self.__sftp.close()
            self.__sftp = None
        if self.__ssh:
            self.__ssh.close()
            self.__ssh = None

    def __enter__(self):
        """Enable use as a context manager."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Ensure proper shutdown of SSH/SFTP connections."""
        self.close()
        return False
