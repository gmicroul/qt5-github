import sys
import os
import subprocess
import requests
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QMessageBox,
)


class LoginWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        form = QFormLayout()
        self.user_edit = QLineEdit()
        self.pass_edit = QLineEdit()
        self.pass_edit.setEchoMode(QLineEdit.Password)
        form.addRow("Username:", self.user_edit)
        form.addRow("Password:", self.pass_edit)
        layout.addLayout(form)
        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.attempt_login)
        layout.addWidget(self.login_btn)
        # GitHub token input
        token_label = QLabel("GitHub Token:")
        self.token_edit = QLineEdit()
        self.token_edit.setEchoMode(QLineEdit.Password)
        token_layout = QFormLayout()
        token_layout.addRow(token_label, self.token_edit)
        layout.addLayout(token_layout)
        self.setLayout(layout)

    def attempt_login(self):
        # placeholder authentication
        user = self.user_edit.text()
        pwd = self.pass_edit.text()
        if user and pwd:
            QMessageBox.information(self, "Success", f"Logged in as {user}")
        else:
            QMessageBox.warning(self, "Error", "Please enter username and password")


class DirChooserWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.dir_label = QLabel("No directory selected")
        self.choose_btn = QPushButton("Choose directory")
        self.choose_btn.clicked.connect(self.choose_dir)
        layout.addWidget(self.dir_label)
        layout.addWidget(self.choose_btn)
        self.upload_btn = QPushButton("Upload to GitHub")
        self.upload_btn.clicked.connect(self.upload_to_github)
        layout.addWidget(self.upload_btn)
        self.setLayout(layout)

    def choose_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if dir_path:
            self.dir_label.setText(dir_path)

    def upload_to_github(self):
        # Simple implementation: create repo via GitHub API and git push
        import os
        repo_name = os.path.basename(self.dir_label.text()) or "new-repo"
        token = self.token_edit.text() or os.getenv("GITHUB_TOKEN")
        if not token:
            QMessageBox.warning(self, "Error", "GitHub token not provided")
            return
        # Create repo – if it already exists, grab that one
        import requests
        headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}
        # First try creating
        resp = requests.post("https://api.github.com/user/repos", json={"name": repo_name, "private": False}, headers=headers)
        if resp.status_code == 201:
            repo_url = resp.json()["clone_url"]
        elif resp.status_code == 422 and "name already exists" in resp.text:
            # Repo exists – fetch current user info to build URL
            user_resp = requests.get("https://api.github.com/user", headers=headers)
            if user_resp.status_code == 200:
                username = user_resp.json()["login"]
                r = requests.get(f"https://api.github.com/repos/{username}/{repo_name}", headers=headers)
                if r.status_code == 200:
                    repo_url = r.json()["clone_url"]
                else:
                    QMessageBox.warning(self, "Error", f"Cannot find existing repo: {r.text}")
                    return
            else:
                QMessageBox.warning(self, "Error", f"Cannot get user info: {user_resp.text}")
                return
        else:
            QMessageBox.warning(self, "Error", f"Repo creation failed: {resp.text}")
            return
        # Embed token in HTTPS URL to avoid interactive prompt
        if repo_url and token:
            repo_url = repo_url.replace('https://', f'https://{token}@')
        # Initialize git in selected dir
        import subprocess
        cwd = self.dir_label.text()
        subprocess.run(["git", "init"], cwd=cwd, check=True)
        subprocess.run(["git", "add", "."], cwd=cwd, check=True)
        # Configure a basic identity if not set
        subprocess.run(["git", "config", "user.email", "you@example.com"], cwd=cwd, check=False)
        subprocess.run(["git", "config", "user.name", "Your Name"], cwd=cwd, check=False)
        try:
            subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=cwd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            # Nothing to commit; create an empty commit
            subprocess.run(["git", "commit", "--allow-empty", "-m", "Initial commit"], cwd=cwd, check=True)

        # Add or update remote
        # Disable any stored credentials to force token usage
        subprocess.run(["git", "config", "--global", "credential.helper", ""], cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            subprocess.run(["git", "remote", "get-url", "origin"], cwd=cwd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # Remote exists, update URL
            subprocess.run(["git", "remote", "set-url", "origin", repo_url], cwd=cwd, check=True)
        except subprocess.CalledProcessError:
            subprocess.run(["git", "remote", "add", "origin", repo_url], cwd=cwd, check=True)
        # Determine branch to push – default to main
        default_branch = "main"
        subprocess.run(["git", "checkout", "-B", default_branch], cwd=cwd, check=True)
        subprocess.run(["git", "push", "-u", "origin", default_branch], cwd=cwd, check=False)
        QMessageBox.information(self, "Success", f"Uploaded to {repo_url}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Qt5 Github Uploader")
        central = QWidget()
        layout = QVBoxLayout()
        login_wid = LoginWidget()
        chooser_wid = DirChooserWidget()
        layout.addWidget(login_wid)
        layout.addWidget(chooser_wid)
        chooser_wid.token_edit = login_wid.token_edit
        central.setLayout(layout)
        self.setCentralWidget(central)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.resize(400, 300)
    win.show()
    sys.exit(app.exec_())
