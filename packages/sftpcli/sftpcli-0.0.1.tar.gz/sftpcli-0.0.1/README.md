# 🚀 SFTP Client CLI

A sleek and user-friendly command-line tool to **upload**, **download**, and **manage files** on a remote SFTP server. Configure reusable profiles, automate transfers, and even explore directories — all from your terminal.

---

## ✨ Features

-   🔐 Persistent profile-based SFTP configuration
-   📤 Upload files or entire directories
-   📥 Download remote files with ease
-   📂 Remote directory exploration (tree/list)
-   🧱 Remote file and folder management (mkdir, rmdir, remove, rename, exists)
-   🔄 Rename files/folders on the remote server
-   ⚙️ Easy to extend and customize

---

## 📦 Installation

```bash
git clone https://github.com/sachin-acharya-projects/sftp-cli.git
cd sftp-cli
pip install -r requirements.txt
```

> **Python 3.7+ required**

---

## 🚀 Quick Start

### 1. Configure a Connection Profile

```bash
python sftpcli.py configure --host sftp.example.com --port 22 --username user --password pass --upload_dir /uploads --profile myserver
```

### 2. Upload Files

```bash
python sftpcli.py upload file1.txt file2.txt -P myserver
```

### 3. Download Files

```bash
python sftpcli.py download remote1.txt remote2.txt -P myserver
```

### 4. Test Connection

```bash
python sftpcli.py connect myserver
```

---

## 📚 Full Command List

| Command     | Description                                        |
| ----------- | -------------------------------------------------- |
| `configure` | Save SFTP connection details as a reusable profile |
| `upload`    | Upload local files to the remote server            |
| `download`  | Download files from the remote server              |
| `listdir`   | List contents of remote directories                |
| `mkdir`     | Create directories on the remote server            |
| `rmdir`     | Remove remote directories (must be empty)          |
| `remove`    | Delete specific files from the remote server       |
| `rename`    | Rename a file or folder on the remote server       |
| `exists`    | Check if files or directories exist on the remote  |
| `tree`      | Display a tree view of a remote directory          |
| `connect`   | Test connection to a configured SFTP profile       |

---

## 🛠️ Example Usages

### Upload files to a subdirectory

```bash
python sftpcli.py upload file.txt -d /custom/path -P myserver
```

### View a tree of a remote folder

```bash
python sftpcli.py tree /uploads -P myserver
```

### Delete remote files

```bash
python sftpcli.py remove /uploads/old1.txt /uploads/old2.txt -P myserver
```

### Rename a remote file

```bash
python sftpcli.py rename /uploads/oldname.txt /uploads/newname.txt -P myserver
```

---

## 📁 Profiles

Use `--profile` or `-P` to specify which SFTP profile to use. If omitted, the `default` profile is used.

Example:

```bash
python sftpcli.py upload file.txt -P work-server
```

---

## 🧪 Development

Feel free to modify, extend, or integrate into your own automation workflows!

### Run Locally

```bash
python sftpcli.py <command> [options]
```

### Example Test Command

```bash
python sftpcli.py connect default
```

---

## 💡 Tips

-   Use `--help` with any command to see available options:

    ```bash
    python sftpcli.py upload --help
    ```

-   Profile configuration is saved for reuse. No need to re-enter credentials each time.

---

## 📜 License

MIT License. Use freely, modify responsibly.

---

## 🤝 Contributing

Have ideas? Found a bug? PRs and issues are welcome!
