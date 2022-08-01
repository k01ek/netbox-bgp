import re

from django import forms
from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist, ValidationError
from django.utils.translation import gettext as _

from extras.models import Tag
from tenancy.models import Tenant
from dcim.models import Device, Site
from ipam.models import IPAddress, Prefix, ASN
from ipam.formfields import IPNetworkFormField
from utilities.forms import (
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField, StaticSelect,
    APISelect, APISelectMultiple, StaticSelectMultiple, TagFilterField
)
from netbox.forms import NetBoxModelForm, NetBoxModelBulkEditForm, NetBoxModelFilterSetForm

from .models import (
    CommunityStatusChoices, Community, BGPSession,
    SessionStatusChoices, RoutingPolicy, BGPPeerGroup, RoutingPolicyRule
)


from django.forms.widgets import TextInput


class CommunityForm(NetBoxModelForm):
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )
    status = forms.ChoiceField(
        required=False,
        choices=CommunityStatusChoices,
        widget=StaticSelect()
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )

    class Meta:
        model = Community
        fields = [
            'value', 'description', 'status', 'tenant', 'tags',
        ]


class CommunityFilterForm(NetBoxModelFilterSetForm):
    q = forms.CharField(
        required=False,
        label='Search'
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    status = forms.MultipleChoiceField(
        choices=CommunityStatusChoices,
        required=False,
        widget=StaticSelectMultiple()
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False
    )

    tag = TagFilterField(Community)

    model = Community


class CommunityBulkEditForm(NetBoxModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Community.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )
    status = forms.ChoiceField(
        required=False,
        choices=CommunityStatusChoices,
        widget=StaticSelect()
    )

    model = Community
    nullable_fields = [
       'tenant', 'description',
    ]


class BGPSessionForm(NetBoxModelForm):
    name = forms.CharField(
        max_length=64,
        required=True
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False
    )
    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        }
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    local_as = DynamicModelChoiceField(
        queryset=ASN.objects.all(),
        query_params={
            'site_id': '$site'
        },
        label=_('Local AS')
    )
    remote_as = DynamicModelChoiceField(
        queryset=ASN.objects.all(),
        label=_('Remote AS')
    )
    local_address = DynamicModelChoiceField(
        queryset=IPAddress.objects.all(),
        query_params={
            'device_id': '$device'
        }
    )
    remote_address = DynamicModelChoiceField(
        queryset=IPAddress.objects.all(),
    )
    peer_group = DynamicModelChoiceField(
        queryset=BGPPeerGroup.objects.all(),
        required=False,
        widget=APISelect(
            api_url='/api/plugins/bgp/peer-group/',
        )
    )
    import_policies = DynamicModelMultipleChoiceField(
        queryset=RoutingPolicy.objects.all(),
        required=False,
        widget=APISelectMultiple(
            api_url='/api/plugins/bgp/routing-policy/'
        )
    )
    export_policies = DynamicModelMultipleChoiceField(
        queryset=RoutingPolicy.objects.all(),
        required=False,
        widget=APISelectMultiple(
            api_url='/api/plugins/bgp/routing-policy/'
        )
    )

    class Meta:
        model = BGPSession
        fields = [
            'name', 'site', 'device',
            'local_as', 'remote_as', 'local_address', 'remote_address',
            'description', 'status', 'peer_group', 'tenant', 'tags', 'import_policies', 'export_policies'
        ]
        fieldsets = (
            ('Session', ('name', 'site', 'device', 'description', 'status', 'peer_group', 'tenant', 'tags')),
            ('Remote', ('remote_as', 'remote_address')),
            ('Local', ('local_as', 'local_address')),
            ('Policies', ('import_policies', 'export_policies'))
        )
        widgets = {
            'status': StaticSelect(),
        }


class BGPSessionAddForm(BGPSessionForm):
    remote_address = IPNetworkFormField()

    def clean_remote_address(self):
        try:
            ip = IPAddress.objects.get(address=str(self.cleaned_data['remote_address']))
        except MultipleObjectsReturned:
            ip = IPAddress.objects.filter(address=str(self.cleaned_data['remote_address'])).first()
        except ObjectDoesNotExist:
            ip = IPAddress.objects.create(address=str(self.cleaned_data['remote_address']))
        self.cleaned_data['remote_address'] = ip
        return self.cleaned_data['remote_address']


class BGPSessionFilterForm(NetBoxModelFilterSetForm):
    model = BGPSession
    q = forms.CharField(
        required=False,
        label='Search'
    )
    remote_as_id = DynamicModelMultipleChoiceField(
        queryset=ASN.objects.all(),
        required=False,
        label=_('Remote AS')
    )
    local_as_id = DynamicModelMultipleChoiceField(
        queryset=ASN.objects.all(),
        required=False,
        label=_('Local AS')
    )
    by_local_address = forms.CharField(
        required=False,
        label='Local Address'
    )
    by_remote_address = forms.CharField(
        required=False,
        label='Remote Address'
    )
    device_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label=_('Device')
    )
    status = forms.MultipleChoiceField(
        choices=SessionStatusChoices,
        required=False,
        widget=StaticSelectMultiple()
    )
    peer_group = DynamicModelMultipleChoiceField(
        queryset=BGPPeerGroup.objects.all(),
        required=False,
        widget=APISelectMultiple(
            api_url='/api/plugins/bgp/peer-group/'
        )
    )
    import_policies = DynamicModelMultipleChoiceField(
        queryset=RoutingPolicy.objects.all(),
        required=False,
        widget=APISelectMultiple(
            api_url='/api/plugins/bgp/routing-policy/'
        )
    )
    export_policies = DynamicModelMultipleChoiceField(
        queryset=RoutingPolicy.objects.all(),
        required=False,
        widget=APISelectMultiple(
            api_url='/api/plugins/bgp/routing-policy/'
        )
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )

    tag = TagFilterField(model)


class RoutingPolicyFilterForm(NetBoxModelFilterSetForm):
    model = RoutingPolicy
    q = forms.CharField(
        required=False,
        label='Search'
    )

    tag = TagFilterField(model)


class RoutingPolicyForm(NetBoxModelForm):
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = RoutingPolicy
        fields = ['name', 'description']


class BGPPeerGroupFilterForm(NetBoxModelFilterSetForm):
    model = BGPPeerGroup
    q = forms.CharField(
        required=False,
        label='Search'
    )

    tag = TagFilterField(model)


class BGPPeerGroupForm(NetBoxModelForm):
    import_policies = DynamicModelMultipleChoiceField(
        queryset=RoutingPolicy.objects.all(),
        required=False,
        widget=APISelectMultiple(
            api_url='/api/plugins/bgp/routing-policy/'
        )
    )
    export_policies = DynamicModelMultipleChoiceField(
        queryset=RoutingPolicy.objects.all(),
        required=False,
        widget=APISelectMultiple(
            api_url='/api/plugins/bgp/routing-policy/'
        )
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = BGPPeerGroup
        fields = ['name', 'description', 'import_policies', 'export_policies', 'tags']


class RoutingPolicyRuleForm(NetBoxModelForm):
    match_community = DynamicModelMultipleChoiceField(
        queryset=Community.objects.all(),
        required=False,
    )
    match_ip = DynamicModelMultipleChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        label='Match Prefix',
    )
    match_ip_cond = forms.JSONField(
        label='Match filtered prefixes',
        help_text='Filter for Prefixes, e.g., {"site__name": "site1", "tenant__name": "tenant1"}',
        required=False,
    )
    match_custom = forms.JSONField(
        label='Custom Match',
        help_text='Any custom match statements, e.g., {"ip nexthop": "1.1.1.1"}',
        required=False,
    )
    set_actions = forms.JSONField(
        label='Set statements',
        help_text='Set statements, e.g., {"as-path prepend": [12345,12345]}',
        required=False
    )

    class Meta:
        model = RoutingPolicyRule
        fields = [
            'routing_policy', 'index', 'action', 'match_community',
            'match_ip', 'match_ip_cond', 'match_custom',
            'set_actions', 'description',
        ]
