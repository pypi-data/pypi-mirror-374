# netbox_entraid_tools/__init__.py
"""NetBox EntraID Tools plugin."""

import logging
from netbox.plugins import PluginConfig
from .template_content import ContactActions

# Metadata must be defined in this file
__plugin_name__ = "netbox_entraid_tools"
__verbose_name__ = "NetBox EntraID Tools"
__description__ = "Jobs and utilities for EntraID hygiene in NetBox."
__version__ = "0.1.56"
__author__ = "Bacardi -  N.I.T."
__author_email__ = "netbox@bacardi.com"
__project_url__ = "https://github.com/bacardi-code/techops-networking-netbox-entraid-tools"

log = logging.getLogger(__name__)

DEFAULTS = {
    "job_interval_hours": 6,
    "auto_schedule": True,
    "storage_account_name": "westeuncnetboxauto",
    "storage_table_name": "ContactAssignmentDeletions",
    "treat_disabled_as_missing": False,
    "debug_mode": False,  # Enable debug mode by default for troubleshooting
}


class NetBoxEntraIDToolsConfig(PluginConfig):
    """
    NetBox plugin configuration for NetBox EntraID Tools.
    """

    name = __plugin_name__
    verbose_name = __verbose_name__
    description = __description__
    version = __version__
    author = __author__
    author_email = __author_email__
    base_url = "entraid-tools"
    required_settings = []
    default_settings = DEFAULTS
    min_version = "4.2.0"

    def ready(self) -> None:
        """
        Post-migration tasks.
        """
        super().ready()

        # Set up enhanced logging
        from .common import ensure_plugin_logger

        logger = ensure_plugin_logger()
        logger.info(
            f"NetBox EntraID Tools v{__version__} initialized with enhanced logging"
        )

        # Import signals
        from . import signals  # noqa: F401


# This is the crucial part that NetBox looks for
config = NetBoxEntraIDToolsConfig
