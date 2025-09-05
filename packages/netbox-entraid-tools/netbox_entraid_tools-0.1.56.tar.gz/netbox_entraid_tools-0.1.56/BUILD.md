# Build and Deployment Guide

This document outlines the recommended process for building and deploying the NetBox EntraID Tools plugin.

## Modern Build Process

Starting October 31, 2025, the old `setup.py`-based build process will be deprecated. The project has been configured to use the modern PEP 517 build system with `pyproject.toml`.

### Building the Package

```bash
# Install build tools
pip install build

# Build both wheel and source distribution
python -m build

# The built packages will be available in the dist/ directory
```

### Version Management

The project includes a release script to handle version bumping, changelog updates, and git tagging:

```bash
# Bump patch version (z in x.y.z)
python tools/release.py patch

# Bump minor version (y in x.y.z)
python tools/release.py minor

# Bump major version (x in x.y.z)
python tools/release.py major

# Add --sign to sign git tags with GPG
python tools/release.py patch --sign

# Add --push to push changes to remote repository
python tools/release.py patch --sign --push
```

### Manual Deployment

After building, you can deploy the package to your NetBox server:

```bash
# Copy the wheel file to the server
scp dist/netbox_entraid_tools-*.whl user@netbox-server:/tmp/

# On the NetBox server, install the package
pip install /tmp/netbox_entraid_tools-*.whl

# Run migrations
python manage.py migrate netbox_entraid_tools
```

### Using pip (if package is hosted in a repository)

```bash
pip install netbox-entraid-tools
```

## Folder Version Management

The project also includes a PowerShell script to create new versioned folders:

```powershell
# Bump patch version, copy project to new folder, move to that new folder and  
# Optionally launch VSCode in the new folder.
. ./Bump-FolderVersion.ps1 #To 'dot source' the function, making it available in this session.
Bump-FolderVersion

# Specify increment type
Bump-FolderVersion #Defaults to a "patch" increment (z in x.y.z)
Bump-FolderVersion -Increment "minor" # Bump major version (y in x.y.z)
Bump-FolderVersion -Increment "major" # Bump major version (x in x.y.z)

# Don't launch VSCode in new folder automatically
Bump-FolderVersion -OpenCode:$false
```

This creates a copy of the current directory with an incremented version number in the folder name.
