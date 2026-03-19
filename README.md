# qt5-github

This repository contains a small **PyQt5** application that lets you upload a local directory (the `qt5-github` folder itself) to a GitHub repository.  The tool is meant to be run from the command line or a head‑less environment, and uses a *personal access token* (PAT) for authentication.

---

## Features

* Create a new GitHub repository (or reuse an existing one).
* Commit the contents of the selected directory.
* Push the commit to the default branch of the remote repo.
* Works with an X‑server or without – set `QT_QPA_PLATFORM=offscreen` if you are in a Docker container or a head‑less machine.

## Prerequisites

* Python 3.10+ (PyQt5, requests)
* A GitHub account and a **personal access token** with the `repo` scope.

## Installation

```bash
# In the qt5-github directory
pip install -r requirements.txt
```

## Usage

```bash
# 1️⃣ Launch the GUI
python3 control_gui.py

# 2️⃣ (Optional) Run head‑less
QT_QPA_PLATFORM=offscreen python3 control_gui.py
```

In the GUI you will be asked for:

1. **GitHub Username** – the account that will own the repo.
2. **Password / PAT** – you can paste the token here or leave it blank.
3. **Token field** – alternatively you may set an environment variable `GITHUB_TOKEN` before launching the script.

The application will:

1. Create (or reuse) a repo named after the directory you selected.
2. Initialise a Git repository, add all files, and commit.
3. Push to the default branch (currently `dev` unless you renamed it to `main`).

## Creating a GitHub Personal Access Token

1. **Navigate to GitHub** → **Settings** → **Developer settings** → **Personal access tokens**.
2. Click **Generate new token**.
3. Give it a meaningful **Note** (e.g. `OpenClaw Control UI`).
4. Select the **`repo`** scope (this allows read/write access to all your private repos). If you only need to push to public repos, `repo:push` is sufficient.
5. Click **Generate token**.
6. **Copy** the token immediately – it will not be shown again.

### Using the Token

- **GUI** – paste the token into the *GitHub Token* field.
- **Environment** – export it before running:
  ```bash
  export GITHUB_TOKEN="YOUR_TOKEN"
  python3 control_gui.py
  ```

## Customising Commit Identity

The script sets a dummy identity (`you@example.com` / `Your Name`) if you haven’t configured Git globally.  You can override this with your own identity:

```bash
git config --global user.name "Your Real Name"
git config --global user.email "you@example.com"
```

## Notes

* The token is never written to disk; it is kept only in memory during the script’s lifetime.
* The repository is created with the **default branch set by GitHub** (currently `dev`).  If you want `main` to be the default, rename the branch locally (`git branch -m master main`) and push it, then change the default in the GitHub UI.
* Feel free to fork or extend this project – it is MIT licensed.

---

Happy coding!
