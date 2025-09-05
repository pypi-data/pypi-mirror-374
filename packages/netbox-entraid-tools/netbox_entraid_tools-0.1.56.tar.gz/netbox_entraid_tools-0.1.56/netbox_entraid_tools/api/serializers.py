from rest_framework import serializers
from netbox.api.serializers import NetBoxModelSerializer
from ..models import Settings


class SettingsSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_entraid_tools-api:settings-detail"
    )

    class Meta:
        model = Settings
        fields = (
            "id",
            "url",
            "display",
            "storage_account_name",
            "report_sender",
            "debug_mode",
            "local_user_accounts",
            # Job 1 fields
            "job1_interval_hours",
            "job1_auto_schedule",
            "job1_storage_table_name",
            "job1_report_recipients",
            "job1_treat_disabled_as_missing",
            # Job 2 fields
            "job2_interval_hours",
            "job2_auto_schedule",
            "job2_storage_table_name",
            # Meta fields
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
