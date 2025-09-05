from netbox.plugins import PluginTemplateExtension
from django.urls import reverse
from netbox_entraid_tools.common import get_debug_mode


class ContactActions(PluginTemplateExtension):
    model = "tenancy.contact"

    def buttons(self):
        contact = self.context.get("object")
        if not contact:
            return ""
        url = reverse(
            "plugins:netbox_entraid_tools:contact_resolve_entraid", args=[contact.pk]
        )
        return self.render(
            "netbox_entraid_tools/buttons/contact_actions.html",
            extra_context={"resolve_url": url},
        )

    def list_buttons(self):
        # This adds the bulk action button to the contacts list view
        # Get debug mode from utility function
        debug_mode = get_debug_mode()

        return self.render(
            "netbox_entraid_tools/buttons/contact_list_actions.html",
            extra_context={"debug_mode": debug_mode},
        )


template_extensions = [ContactActions]
