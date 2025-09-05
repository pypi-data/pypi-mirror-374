# Generated manually 2025-09-03 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("netbox_entraid_tools", "0005_settings_debug_mode"),
    ]

    operations = [
        migrations.AddField(
            model_name="settings",
            name="local_user_accounts",
            field=models.JSONField(
                blank=True,
                default=list,
                help_text="List of local user accounts to skip when syncing status with EntraID",
            ),
        ),
    ]
