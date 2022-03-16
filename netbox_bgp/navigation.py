from extras.plugins import PluginMenuButton, PluginMenuItem
from utilities.choices import ButtonColorChoices

menu_items = (
    PluginMenuItem(
        link='plugins:netbox_bgp:community_list',
        link_text='Communities',
        permissions=['netbox_bgp.view_community'],
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_bgp:community_add',
                title='Communities',
                icon_class='mdi mdi-plus-thick',
                color=ButtonColorChoices.GREEN,
                permissions=['netbox_bgp.add_community'],
            ),
        ),
    ),
    PluginMenuItem(
        link='plugins:netbox_bgp:session_list',
        link_text='Sessions',
        permissions=['netbox_bgp.view_bgpsession'],
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_bgp:session_add',
                title='Sessions',
                icon_class='mdi mdi-plus-thick',
                color=ButtonColorChoices.GREEN,
                permissions=['netbox_bgp.add_bgpsession'],
            ),
        ),
    ),
    PluginMenuItem(
        link='plugins:netbox_bgp:routing_policy_list',
        link_text='Routing Policies',
        permissions=['netbox_bgp.view_routingpolicy'],
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_bgp:routing_policy_add',
                title='Routing Policies',
                icon_class='mdi mdi-plus-thick',
                color=ButtonColorChoices.GREEN,
                permissions=['netbox_bgp.add_routingpolicy'],
            ),
        ),
    ),
    PluginMenuItem(
        link='plugins:netbox_bgp:peergroup_list',
        link_text='Peer Groups',
        permissions=['netbox_bgp.view_bgppeergroup'],
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_bgp:peergroup_add',
                title='Peer Groups',
                icon_class='mdi mdi-plus-thick',
                color=ButtonColorChoices.GREEN,
                permissions=['netbox_bgp.add_bgppeergroup'],
            ),
        ),
    )
)
