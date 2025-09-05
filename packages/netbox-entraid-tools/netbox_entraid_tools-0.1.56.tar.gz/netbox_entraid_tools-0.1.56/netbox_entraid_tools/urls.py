# netbox_entraid_tools/urls.py
from django.urls import path
from . import views

app_name = "netbox_entraid_tools"

urlpatterns = [
    path("config/", views.ConfigView.as_view(), name="config"),
    path("run/", views.RunNowView.as_view(), name="run"),
    path(
        "contact/<int:pk>/update_entraid/",
        views.UpdateContactFromEntraIDView.as_view(),
        name="resolve_contact_entraid",
    ),
    path(
        "contact/<int:pk>/resolve_entraid/",
        views.ResolveContactJobView.as_view(),
        name="contact_resolve_entraid",
    ),
    path(
        "contacts/bulk-resolve-entraid/",
        views.BulkResolveContactsView.as_view(),
        name="bulk_contact_resolve_entraid",
    ),
]
