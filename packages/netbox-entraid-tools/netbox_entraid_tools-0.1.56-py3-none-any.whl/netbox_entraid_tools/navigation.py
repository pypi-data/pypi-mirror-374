# netbox_entraid_tools/navigation.py
from netbox.plugins import PluginMenuItem, PluginMenuButton
from netbox.choices import ButtonColorChoices

# Define action buttons that will appear on the main plugin page
entraid_buttons = [
    PluginMenuButton(
        link="plugins:netbox_entraid_tools:run",
        title="Tidy Contacts Now",
        icon_class="mdi mdi-play-circle",
        color=ButtonColorChoices.GREEN,
    ),
]

# This creates the main menu item that will show up in the "Plugins" dropdown
menu_items = (
    PluginMenuItem(
        link="plugins:netbox_entraid_tools:config",
        link_text="EntraID Tools",
        buttons=entraid_buttons,
    ),
)
