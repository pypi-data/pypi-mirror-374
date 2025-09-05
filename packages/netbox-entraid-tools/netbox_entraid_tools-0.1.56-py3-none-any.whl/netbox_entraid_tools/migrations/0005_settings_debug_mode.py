# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("netbox_entraid_tools", "0004_settings_treat_disabled_as_missing"),
    ]

    operations = [
        migrations.AddField(
            model_name="settings",
            name="debug_mode",
            field=models.BooleanField(
                default=False,
                help_text="If enabled, displays debug information in the UI for troubleshooting.",
            ),
        ),
    ]
