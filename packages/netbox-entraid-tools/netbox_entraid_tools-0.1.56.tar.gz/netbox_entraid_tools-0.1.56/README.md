# NetBox EntraID Tools
[![GitHub](https://img.shields.io/badge/GitHub-netbox--entraid--tools-blue?logo=github)](https://github.com/bacardi-code/techops-networking-netbox-entraid-tools)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![NetBox](https://img.shields.io/badge/NetBox-4.2.0%2B-blue)](https://github.com/netbox-community/netbox)

Jobs and utilities for EntraID hygiene in NetBox.

## Overview

This plugin is part of a larger ecosystem of EntraID (Azure AD) integrations with NetBox:

1. **NetBox Contacts Sync** ([`netbox-contacts-sync`](https://github.com/bacardi-code/techops-networking-netbox-contacts-sync)) - Windows Server-based service that syncs SharePoint contact assignments to NetBox
2. **NetBox EntraID SSO** - Allows NetBox admin login via EntraID
3. **Contact Cleanup Job** (`DeprecateContactsJob`) - Identifies and handles invalid/missing contacts
4. **Contact EntraID Resolution** - Allows manual contact resolution against EntraID

## Installation

```bash
# Using pip
pip install netbox-entraid-tools

# Manual installation from source
git clone https://github.com/bacardi-code/techops-networking-netbox-entraid-tools /downloads/netbox-entraid-tools
pushd /downloads/netbox-entraid-tools
pip install .
```

## Configuration

Add to your NetBox `configuration.py`:

```python
PLUGINS = [
    'netbox_entraid_tools',
    # ... other plugins
]

PLUGINS_CONFIG = {
    'netbox_entraid_tools': {
        # Optional settings
        # 'job_interval_hours': 6,
        # 'auto_schedule': True,
        # 'storage_account_name': 'westeuncnetboxauto',
        # 'storage_table_name': 'ContactAssignmentDeletions',
        # 'treat_disabled_as_missing': False,
        # 'debug_mode': False,
    }
}
```

Run migrations:
```bash
python manage.py migrate netbox_entraid_tools
```

## Development

1. Clone repository
2. Install requirements: `pip install -r requirements.txt`
3. Add to NetBox configuration
4. Run migrations

## Build and Version Management

For detailed information about building the package, managing versions, and deployment processes, please see the [BUILD.md](./BUILD.md) file. This includes:

- Modern build process using PEP 517
- Version management with `tools/release.py` 
- Folder version management with `Bump-FolderVersion.ps1`
- Deployment instructions

## License

Apache License 2.0
