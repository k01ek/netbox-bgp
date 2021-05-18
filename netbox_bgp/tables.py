import django_tables2 as tables
from django.utils.safestring import mark_safe

from utilities.tables import BaseTable, ChoiceFieldColumn, ToggleColumn

from .models import ASN, Community, BGPSession, RoutingPolicy

AVAILABLE_LABEL = mark_safe('<span class="label label-success">Available</span>')
COL_TENANT = """
 {% if record.tenant %}
     <a href="{{ record.tenant.get_absolute_url }}" title="{{ record.tenant.description }}">{{ record.tenant }}</a>
 {% else %}
     &mdash;
 {% endif %}
 """


class ASNTable(BaseTable):
    pk = ToggleColumn()
    number = tables.LinkColumn()
    status = ChoiceFieldColumn(
        default=AVAILABLE_LABEL
    )
    site = tables.LinkColumn()
    tenant = tables.TemplateColumn(
        template_code=COL_TENANT
    )

    class Meta(BaseTable.Meta):
        model = ASN
        fields = ('pk', 'number', 'description', 'status')


class CommunityTable(BaseTable):
    pk = ToggleColumn()
    value = tables.LinkColumn()
    status = ChoiceFieldColumn(
        default=AVAILABLE_LABEL
    )
    tenant = tables.TemplateColumn(
        template_code=COL_TENANT
    )

    class Meta(BaseTable.Meta):
        model = Community
        fields = ('pk', 'value', 'description', 'status')


class BGPSessionTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()
    device = tables.LinkColumn()
    local_address = tables.LinkColumn(verbose_name='Local Address')
    local_as = tables.LinkColumn(verbose_name='Local AS')
    remote_address = tables.LinkColumn(verbose_name='Remote Address')
    remote_as = tables.LinkColumn(verbose_name='Remote AS')
    ibgp_device = tables.LinkColumn(verbose_name='iBGP Device')
    site = tables.LinkColumn()
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
            'remote_address', 'remote_as', 'ibgp_device',
            'description', 'site', 'status'
        )


class RoutingPolicyTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()

    class Meta(BaseTable.Meta):
        model = RoutingPolicy
        fields = ('pk', 'name', 'description')
