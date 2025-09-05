# models.py
from django.db import models
from netbox.models import NetBoxModel


class Settings(NetBoxModel):
    # Global settings
    storage_account_name = models.CharField(max_length=100, blank=True)
    report_sender = models.EmailField(blank=True, help_text="Sender email address")

    # Debug mode for displaying additional information in the UI
    debug_mode = models.BooleanField(
        default=False,
        help_text="If enabled, displays debug information in the UI for troubleshooting.",
    )

    # List of local user accounts to skip when syncing status with EntraID
    local_user_accounts = models.JSONField(
        default=list,
        blank=True,
        help_text="List of local user accounts to skip when syncing status with EntraID",
    )

    # --- Job 1: Deprecate Contacts ---
    job1_interval_hours = models.PositiveIntegerField(default=6)
    job1_auto_schedule = models.BooleanField(default=True)
    job1_storage_table_name = models.CharField(max_length=100, blank=True)
    job1_report_recipients = models.JSONField(
        default=list,
        blank=True,
        help_text="List of recipient email addresses for job1 reports",
    )
    job1_treat_disabled_as_missing = models.BooleanField(
        default=False,
        help_text="If enabled, disabled Entra users (accountEnabled=false) are treated as missing for deprecation.",
    )

    # --- Job 2: Sync User Status ---
    job2_interval_hours = models.PositiveIntegerField(default=24)
    job2_auto_schedule = models.BooleanField(default=True)
    job2_storage_table_name = models.CharField(
        max_length=100,
        blank=True,
        default="UserStatusChanges",
        help_text="Azure Table Storage name for logging user status changes.",
    )

    def __str__(self):
        return "Contacts Admin"

    class Meta:
        verbose_name = "Contacts Admin"

        permissions = [
            ("contact_admin", "Can run EntraID contact cleanup jobs"),
        ]
