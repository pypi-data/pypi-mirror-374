# Gitflow

This file show the recommendations related with Gitflow situations.

---

- [**Branching**](#branching)
  - [**Default branch**](#default-branch)
  - [**Protected branch**](#protected-branch)
  - [**Temporal branch**](#temporal-branch)
- [**Changes**](#changes)
  - [**From temporal branch**](#from-temporal-branch)
    - [**Create new branch**](#create-new-branch)
    - [**Create new Pull Request (PR)**](#create-new-pull-request-pr)
    - [**Merge changes**](#merge-changes)
  - [**Between protected branches**](#between-protected-branches)
    - [**Create new Pull Request (PR)**](#create-new-pull-request-pr-1)
    - [**Merge changes**](#merge-changes-1)
- [**Tagging**](#tagging)
  - [**Recommendations**](#recommendations)
  - [**Changelog**](#changelog)
  - [**Create tag**](#create-tag)

---

## **Branching**
---
### **Default branch**
The default recommended branch is **main**.

### **Protected branch**
The protected branches are usually related with an environment, this is the relationship recommended:

| Branch  | Environment    | ENV |
| :-----: | :------------: | :-: |
| main    | production     | PRO |

### **Temporal branch**
When a change comes from a temporal branch, this branch must be removed after the merge is performed.
A temporal branch could be a **feature/MYFEATURE** or **fix/MYFIX** one.

---

## **Changes**
---
### **From temporal branch**

Changes from a temporal branch could be done when a new **feature** or **fix** will be added to a **protected branch**.

When a change comes **from a temporal branch** implies that this **temporal branch WILL be removed**.

The merge method can be whatever the user desires based in the commit history desired in the target branch.

#### **Create new branch**

- Create a new **feature/PROJECT-XXXX** branch, where PROJECT and XXXX are the project and the code of the task in Jira:
    ```
    git checkout -b feature/PROJECT-XXXX
    ```
- Make some changes.
- Add changes to the branch.
  - Can be added file by file:
    ```
    git add file1 file2 folder1
    ```
  - Can be added all changed files:
    ```
    git add .
    ```
- Create commit message:
    ```
    git commit -m "PROJECT-XXXX My explanation of changes."
    ```
- Push branch:
    ```
    git push origin feature/PROJECT-XXXX
    ```

#### **Create new Pull Request (PR)**

  - Go to Repository menu (top menu under repository name) --> **Pull requests** --> **New pull request** (green button at the right)
    - **base**: This is the merge **target** branch (ie: main)
    - **compare**: This is the merge **source** branch (ie: feature/PROJECT-XXXX)
  - Click at **Create pull request**
    - Recommended name: **sourcebranchname** to **targetbranchname** (ie: feature/PROJECT-XXXX to main)
    - Choose **reviewers/assignees** in the right menu.
  - Click at **Create pull request**

#### **Merge changes**

The recommended merge method **from a temporal branch** that will be **removed** when merged is **"Squash and merge"**. This will **merge all the commits** from the source branch **in only one commit** that simplifies the push message.

If this merge method is **NOT DESIRED** and want to keep all the commits history from the temporal branch, follow the link **"command line instructions"** in the message at the right of the "Squash and merge" button. This will merge with all the commits without adding extra commits or removing it from the history.

Those are the steps:

- Step 1: Clone the repository or update your local repository with the latest changes.
    ```
    git pull origin main
    ```

- Step 2: Switch to the base branch of the pull request.
    ```
    git checkout main
    ```

- Step 3: Merge the head branch into the base branch.
    ```
    git merge feature/PROJECT-XXXX
    ```

- Step 4: Push the changes.
    ```
    git push -u origin main
    ```
---
### **Between protected branches**

Changes between protected branches could be done when an environment promotion is needed. For example, merge **develop** to **main** is like **DEV** to **PRO** environment promotion.

When a change comes **from a protected branch** implies that this **protected branch can NOT be removed**.

The **merge method** can **NOT** be **squash** or **rebase** cause will broke the stability between protected branches, so the solution is to **merge from command line**.

#### **Create new Pull Request (PR)**

  - Go to Repository menu (top menu under repository name) --> **Pull requests** --> **New pull request** (green button at the right)
    - **base**: This is the merge **target** branch (ie: main)
    - **compare**: This is the merge **source** branch (ie: develop)
  - Click at **Create pull request**
    - Recommended name: **source-environment-name** to **target-environment-name** (ie: DEV to PRO)
    - Choose **reviewers/assignees** in the right menu.
  - Click at **Create pull request**

#### **Merge changes**

The mandatory merge method **from a protected branch** is the **"Command line"** method. This will merge with all the commits without adding extra commits or removing it from the history.

Those are the steps:

- Step 1: Clone the repository or update your local repository with the latest changes.
    ```
    git pull origin main
    ```

- Step 2: Switch to the base branch of the pull request.
    ```
    git checkout main
    ```

- Step 3: Merge the head branch into the base branch.
    ```
    git merge develop
    ```

- Step 4: Push the changes.
    ```
    git push -u origin main
    ```

After this, the pull request will detect automatically the merge and put the status as "merged".

---

## **Releases & Tagging**
---
### **Overview**

We use an automated helper (`tools/release.py`) plus a GitHub Actions workflow to cut releases. This flow:

- Bumps the version in `netbox_entraid_tools/__init__.py`
- Generates a grouped CHANGELOG entry from Conventional Commits since the last tag
- Commits the changes and creates an annotated tag (prefixed with `v`)
- Optionally builds, signs, and uploads Python packages

The Python package name is fixed as `netbox-entraid-tools` (set in both `pyproject.toml` and `setup.py`). This ensures distribution filenames like `netbox-entraid-tools-X.Y.Z.whl` and `.tar.gz` and prevents the repo name from affecting the package name.

### **Tag format**

- Tags use `vMAJOR.MINOR.PATCH` (example: `v0.1.54`) to align with tooling and common ecosystem conventions.

### **Changelog**

`tools/release.py` prepends a new entry to `CHANGELOG.md` grouped by Features/Fixes/etc. based on commit messages. Follow [Conventional Commits](https://www.conventionalcommits.org/) for clean sections.

### **Run a release (local)**

From the repository root on a clean working tree:

```
python tools/release.py patch --sign --push --build --sign-artifacts --upload
```

Flags:
- `major|minor|patch` or `--set X.Y.Z`: version bump
- `--sign`: GPG-sign the git tag
- `--push`: push branch and tags
- `--build`: build sdist and wheel (`python -m build`)
- `--sign-artifacts`: GPG-sign files in `dist/`
- `--upload`: upload `dist/*` via Twine (requires `TWINE_USERNAME`/`TWINE_PASSWORD`)
- `--allow-retag`: if the target tag already exists locally or on `origin`, delete and recreate it (use with care)

### **Run a release (GitHub Actions)**

Use the manual workflow "Release (manual)". Inputs:

- `part`: `major` | `minor` | `patch`
- `sign_tag` (bool)
- `build` (bool, default true)
- `sign_artifacts` (bool)
- `upload` (bool)

Secrets used when enabled:
- `GPG_PRIVATE_KEY`, `GPG_PASSPHRASE` for tag/artifact signing
- `TWINE_USERNAME`, `TWINE_PASSWORD` for PyPI upload

The workflow executes `tools/release.py` with the selected flags, pushes the tag/branch, and optionally builds/signs/uploads.

Safety checks:
- The release helper refuses to run on a detached HEAD; checkout a branch before releasing.
- If a tag already exists, the release aborts unless `--allow-retag` is passed; with it, the script will delete and recreate the tag locally and on `origin`.