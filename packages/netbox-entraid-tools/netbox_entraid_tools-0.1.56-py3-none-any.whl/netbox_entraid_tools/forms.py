# netbox_entraid_tools/forms.py
import re
from django import forms
from django.core.validators import validate_email
from .models import Settings


class ResolveContactJobForm(forms.Form):
    """
    Form for resolving a contact from EntraID
    """

    dry_run = forms.BooleanField(
        required=False,
        initial=True,
        label="Dry Run",
        help_text="Don't make any changes; just show what would happen",
        widget=forms.CheckboxInput(attrs={"class": "custom-control-input"}),
    )


class SettingsForm(forms.ModelForm):
    # Global setting for local user accounts to skip
    local_user_accounts_text = forms.CharField(
        label="Local User Accounts",
        required=False,
        widget=forms.Textarea(attrs={"rows": 2}),
        help_text="Comma or space separated list of local user accounts to skip when syncing with EntraID (e.g., admin, netbox, system, automation).",
    )

    # --- Job 1: Deprecate Contacts ---
    job1_storage_table_name = forms.CharField(
        label="Storage Table Name",
        help_text="Azure Table Storage name for logging contact assignment deletions.",
    )
    job1_report_recipients_text = forms.CharField(
        label="Report Recipients",
        required=False,
        widget=forms.Textarea(attrs={"rows": 2}),
        help_text="Comma or semicolon separated list of email addresses for this job's report.",
    )
    job1_interval_hours = forms.IntegerField(
        label="Job Interval (Hours)", help_text="How often the job should run."
    )
    job1_auto_schedule = forms.BooleanField(
        required=False,
        label="Auto Schedule",
        help_text="Enable automatic scheduling for this job.",
    )
    job1_treat_disabled_as_missing = forms.BooleanField(
        required=False,
        label="Treat disabled Entra users as missing",
        help_text="When enabled, disabled users (accountEnabled=false) are deprecated and pruned.",
    )

    # --- Job 2: Sync User Status ---
    job2_storage_table_name = forms.CharField(
        label="Storage Table Name",
        help_text="Azure Table Storage name for logging user status changes.",
        initial="UserStatusChanges",
    )
    job2_interval_hours = forms.IntegerField(
        label="Job Interval (Hours)",
        help_text="How often the user status sync job should run.",
    )
    job2_auto_schedule = forms.BooleanField(
        required=False,
        label="Auto Schedule",
        help_text="Enable automatic scheduling for the user status sync job.",
    )

    class Meta:
        model = Settings
        fields = (
            # Global settings
            "storage_account_name",
            "report_sender",
            "debug_mode",
            "local_user_accounts",
            # We handle the job-specific fields manually
        )

    def __init__(self, *args, **kwargs):
        """
        Populate job-specific fields from the model instance.
        """
        super().__init__(*args, **kwargs)

        if self.instance:
            # Populate global fields
            self.fields["local_user_accounts_text"].initial = ", ".join(
                self.instance.local_user_accounts or []
            )

            # Populate Job 1 fields
            self.fields["job1_storage_table_name"].initial = (
                self.instance.job1_storage_table_name
                if hasattr(self.instance, "job1_storage_table_name")
                else ""
            )
            self.fields["job1_report_recipients_text"].initial = ", ".join(
                self.instance.job1_report_recipients
                if hasattr(self.instance, "job1_report_recipients")
                else []
            )
            self.fields["job1_interval_hours"].initial = (
                self.instance.job1_interval_hours
                if hasattr(self.instance, "job1_interval_hours")
                else 6
            )
            self.fields["job1_auto_schedule"].initial = (
                self.instance.job1_auto_schedule
                if hasattr(self.instance, "job1_auto_schedule")
                else True
            )
            self.fields["job1_treat_disabled_as_missing"].initial = (
                self.instance.job1_treat_disabled_as_missing
                if hasattr(self.instance, "job1_treat_disabled_as_missing")
                else False
            )

            # Populate Job 2 fields
            self.fields["job2_storage_table_name"].initial = (
                self.instance.job2_storage_table_name
                if hasattr(self.instance, "job2_storage_table_name")
                else "UserStatusChanges"
            )
            self.fields["job2_interval_hours"].initial = (
                self.instance.job2_interval_hours
                if hasattr(self.instance, "job2_interval_hours")
                else 24
            )
            self.fields["job2_auto_schedule"].initial = (
                self.instance.job2_auto_schedule
                if hasattr(self.instance, "job2_auto_schedule")
                else True
            )

    def clean_local_user_accounts_text(self):
        raw = self.cleaned_data.get("local_user_accounts_text", "") or ""
        return [
            username.strip() for username in re.split(r"[;, ]", raw) if username.strip()
        ]

    def clean_job1_report_recipients_text(self):
        raw = self.cleaned_data.get("job1_report_recipients_text", "") or ""
        emails = [e.strip() for e in re.split(r"[;,]", raw) if e.strip()]
        for email in emails:
            validate_email(email)
        return emails

    # Removed job2_report_recipients_text method as it's no longer needed

    def save(self, *args, **kwargs):
        """
        Save data from job-specific fields back to the model instance.
        """
        # Save global settings that aren't automatically handled
        self.instance.local_user_accounts = self.cleaned_data[
            "local_user_accounts_text"
        ]

        # Save Job 1 settings
        self.instance.job1_storage_table_name = self.cleaned_data[
            "job1_storage_table_name"
        ]
        self.instance.job1_report_recipients = self.cleaned_data[
            "job1_report_recipients_text"
        ]
        self.instance.job1_interval_hours = self.cleaned_data["job1_interval_hours"]
        self.instance.job1_auto_schedule = self.cleaned_data["job1_auto_schedule"]
        self.instance.job1_treat_disabled_as_missing = self.cleaned_data[
            "job1_treat_disabled_as_missing"
        ]

        # Save Job 2 settings
        self.instance.job2_storage_table_name = self.cleaned_data[
            "job2_storage_table_name"
        ]
        self.instance.job2_interval_hours = self.cleaned_data["job2_interval_hours"]
        self.instance.job2_auto_schedule = self.cleaned_data["job2_auto_schedule"]

        return super().save(*args, **kwargs)
