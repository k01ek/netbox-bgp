import re

from django import forms
from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist, ValidationError
from django.utils.translation import gettext as _

from extras.models import Tag
from tenancy.models import Tenant
from dcim.models import Device, Site
from ipam.models import IPAddress, ASN
from ipam.formfields import IPNetworkFormField
from utilities.forms import (
    BootstrapMixin, DynamicModelChoiceField, BulkEditForm,
    DynamicModelMultipleChoiceField, StaticSelect,
    APISelect, APISelectMultiple, StaticSelectMultiple, TagFilterField
)
from extras.forms import (
    CustomFieldModelForm, CustomFieldBulkEditForm, CustomFieldModelFilterForm
)

from .models import (
    CommunityStatusChoices, Community, BGPSession,
    SessionStatusChoices, RoutingPolicy, BGPPeerGroup
)


from django.forms.widgets import TextInput


class CommunityForm(BootstrapMixin, forms.ModelForm):
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
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


class CommunityFilterForm(BootstrapMixin, forms.ModelForm):
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

    class Meta:
        model = Community
        fields = ['q', 'status', 'tenant']


class CommunityBulkEditForm(BulkEditForm):
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

    class Meta:
        nullable_fields = [
            'tenant', 'description',
        ]


class BGPSessionForm(CustomFieldModelForm):
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


class BGPSessionFilterForm(CustomFieldModelFilterForm):
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


class RoutingPolicyFilterForm(CustomFieldModelFilterForm):
    model = RoutingPolicy
    q = forms.CharField(
        required=False,
        label='Search'
    )

    tag = TagFilterField(model)


class RoutingPolicyForm(CustomFieldModelForm):
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = RoutingPolicy
        fields = ['name', 'description']


class BGPPeerGroupFilterForm(CustomFieldModelFilterForm):
    model = BGPPeerGroup
    q = forms.CharField(
        required=False,
        label='Search'
    )

    tag = TagFilterField(model)


class BGPPeerGroupForm(CustomFieldModelForm):
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
