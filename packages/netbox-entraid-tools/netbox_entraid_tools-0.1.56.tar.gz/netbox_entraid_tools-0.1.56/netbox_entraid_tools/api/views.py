from netbox.api.viewsets import NetBoxModelViewSet
from ..models import Settings
from .serializers import SettingsSerializer


class SettingsViewSet(NetBoxModelViewSet):
    queryset = Settings.objects.all()
    serializer_class = SettingsSerializer
