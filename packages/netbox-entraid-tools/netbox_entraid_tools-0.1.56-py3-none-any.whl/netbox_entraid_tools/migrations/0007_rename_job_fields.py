# Generated manually 2025-09-03 19:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("netbox_entraid_tools", "0006_settings_local_user_accounts"),
    ]

    operations = [
        # Rename existing fields
        migrations.RenameField(
            model_name="settings",
            old_name="job_interval_hours",
            new_name="job1_interval_hours",
        ),
        migrations.RenameField(
            model_name="settings",
            old_name="auto_schedule",
            new_name="job1_auto_schedule",
        ),
        migrations.RenameField(
            model_name="settings",
            old_name="storage_table_name",
            new_name="job1_storage_table_name",
        ),
        migrations.RenameField(
            model_name="settings",
            old_name="report_recipients",
            new_name="job1_report_recipients",
        ),
        migrations.RenameField(
            model_name="settings",
            old_name="treat_disabled_as_missing",
            new_name="job1_treat_disabled_as_missing",
        ),
        # Add new fields for Job 2
        migrations.AddField(
            model_name="settings",
            name="job2_interval_hours",
            field=models.PositiveIntegerField(default=24),
        ),
        migrations.AddField(
            model_name="settings",
            name="job2_auto_schedule",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="settings",
            name="job2_storage_table_name",
            field=models.CharField(
                blank=True,
                default="UserStatusChanges",
                max_length=100,
                help_text="Azure Table Storage name for logging user status changes.",
            ),
        ),
    ]
