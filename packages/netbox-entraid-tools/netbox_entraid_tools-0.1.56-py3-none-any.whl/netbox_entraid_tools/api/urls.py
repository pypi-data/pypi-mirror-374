from netbox.api.routers import NetBoxRouter
from . import views

router = NetBoxRouter()
router.register("settings", views.SettingsViewSet)

urlpatterns = router.urls
