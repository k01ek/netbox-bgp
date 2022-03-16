import django_tables2 as tables
from django.utils.safestring import mark_safe
from django_tables2.utils import A

from utilities.tables import BaseTable, ChoiceFieldColumn, ToggleColumn, TagColumn

from .models import Community, BGPSession, RoutingPolicy, BGPPeerGroup

AVAILABLE_LABEL = mark_safe('<span class="label label-success">Available</span>')
COL_TENANT = """
 {% if record.tenant %}
     <a href="{{ record.tenant.get_absolute_url }}" title="{{ record.tenant.description }}">{{ record.tenant }}</a>
 {% else %}
     &mdash;
 {% endif %}
 """

POLICIES = """
{% for rp in value.all %}
    <a href="{{ rp.get_absolute_url }}">{{ rp }}</a>{% if not forloop.last %}<br />{% endif %}
{% empty %}
    &mdash;
{% endfor %}
"""


class CommunityTable(BaseTable):
    pk = ToggleColumn()
    value = tables.LinkColumn()
    status = ChoiceFieldColumn(
        default=AVAILABLE_LABEL
    )
    tenant = tables.TemplateColumn(
        template_code=COL_TENANT
    )
    tags = TagColumn(
        url_name='plugins:netbox_bgp:community_list'
    )

    class Meta(BaseTable.Meta):
        model = Community
        fields = ('pk', 'value', 'description', 'status', 'tags')
        default_columns = (
            'pk', 'value', 'description', 'status', 'tenant'
        )


class BGPSessionTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()
    device = tables.LinkColumn()
    local_address = tables.LinkColumn()
    local_as = tables.LinkColumn()
    remote_address = tables.LinkColumn()
    remote_as = tables.LinkColumn()
    site = tables.LinkColumn()
    peer_group = tables.LinkColumn()
    status = ChoiceFieldColumn(
        default=AVAILABLE_LABEL
    )
    tenant = tables.TemplateColumn(
        template_code=COL_TENANT
    )

    class Meta(BaseTable.Meta):
        model = BGPSession
        fields = (
            'pk', 'name', 'device', 'local_address', 'local_as',
            'remote_address', 'remote_as', 'description', 'peer_group',
            'site', 'status'
        )
        default_columns = (
            'pk', 'name', 'device', 'local_address', 'local_as',
            'remote_address', 'remote_as', 'description',
            'site', 'status', 'tenant'
        )


class RoutingPolicyTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()

    class Meta(BaseTable.Meta):
        model = RoutingPolicy
        fields = ('pk', 'name', 'description')


class BGPPeerGroupTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()
    import_policies = tables.TemplateColumn(
        template_code=POLICIES,
        orderable=False
    )
    export_policies = tables.TemplateColumn(
        template_code=POLICIES,
        orderable=False
    )
    tags = TagColumn(
        url_name='plugins:netbox_bgp:peer_group_list'
    )

    class Meta(BaseTable.Meta):
        model = BGPPeerGroup
        fields = (
            'pk', 'name', 'description', 'tags',
            'import_policies', 'export_policies'
        )
        default_columns = (
            'pk', 'name', 'description'
        )
