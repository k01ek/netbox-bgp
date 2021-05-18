from django import forms
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

from extras.models import Tag
from tenancy.models import Tenant
from dcim.models import Device, Site
from ipam.models import IPAddress
from ipam.formfields import IPNetworkFormField
from utilities.forms import (
    BootstrapMixin, DynamicModelChoiceField, BulkEditForm,
    DynamicModelMultipleChoiceField, StaticSelect2,
    APISelect, APISelectMultiple, StaticSelect2Multiple, TagFilterField
)
from extras.forms import (
    CustomFieldModelForm, CustomFieldBulkEditForm, CustomFieldFilterForm
)

from .models import (
    ASN, ASNStatusChoices, Community, BGPSession,
    SessionStatusChoices, RoutingPolicy, BGPPeerGroup
)


class ASNFilterForm(BootstrapMixin, CustomFieldModelForm):
    q = forms.CharField(
        required=False,
        label='Search'
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    status = forms.MultipleChoiceField(
        choices=ASNStatusChoices,
        required=False,
        widget=StaticSelect2Multiple()
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False
    )

    tag = TagFilterField(ASN)

    class Meta:
        model = ASN
        fields = ['q', 'status', 'tenant']


class ASNForm(BootstrapMixin, CustomFieldModelForm):
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )

    def clean(self):
        cleaned_data = self.cleaned_data
        number = cleaned_data['number']
        tenant = cleaned_data.get('tenant')
        if 'number' in self.changed_data or 'tenant' in self.changed_data:
            if ASN.objects.filter(number=number, tenant=tenant).exists():
                raise forms.ValidationError('AS number with this number and tenant is already exists.')
        return super().clean()

    class Meta:
        model = ASN
        fields = [
            'number', 'description', 'status', 'site', 'tenant', 'tags',
        ]


class ASNBulkEditForm(BootstrapMixin, CustomFieldBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=ASN.objects.all(),
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
        choices=ASNStatusChoices,
        widget=StaticSelect2()
    )

    class Meta:
        nullable_fields = [
            'tenant', 'description',
        ]


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
        choices=ASNStatusChoices,
        required=False,
        widget=StaticSelect2Multiple()
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False
    )

    tag = TagFilterField(Community)

    class Meta:
        model = Community
        fields = ['q', 'status', 'tenant']


class CommunityBulkEditForm(BootstrapMixin, BulkEditForm):
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
        choices=ASNStatusChoices,
        widget=StaticSelect2()
    )

    class Meta:
        nullable_fields = [
            'tenant', 'description',
        ]


class BGPSessionForm(BootstrapMixin, CustomFieldModelForm):
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
        display_field='number',
        widget=APISelect(
            api_url='/api/plugins/bgp/asn/',
        ),
        label='Local AS'
    )
    remote_as = DynamicModelChoiceField(
        queryset=ASN.objects.all(),
        query_params={
            'site_id': '$site'
        },
        display_field='number',
        widget=APISelect(
            api_url='/api/plugins/bgp/asn/',
        ),
        label='Remote AS',
        required=False
    )
    local_address = DynamicModelChoiceField(
        queryset=IPAddress.objects.all(),
        display_field='address',
        query_params={
            'device_id': '$device'
        },
        label='Local Address'
    )
    ibgp_device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        label='iBGP Device',
        required=False
    )
    ibgp_address = DynamicModelChoiceField(
        queryset=IPAddress.objects.all(),
        display_field='address',
        query_params={
            'device_id': '$ibgp_device'
        },
        label='IP Address',
        required=False
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
            'local_as', 'remote_as', 'local_address', 'remote_address', 'ibgp_address', 'ibgp_device',
            'description', 'status', 'tenant', 'tags', 'import_policies', 'export_policies'
        ]


class BGPSessionAddForm(BGPSessionForm):
    remote_address = IPNetworkFormField(
        label='Remote Address',
        required=False
    )

    def save(self, *args, **kwargs):
        session = super().save(*args, commit=False, **kwargs)

        if self.is_ibgp():
            session.remote_address = self.cleaned_data['ibgp_address']
            session.remote_as = session.local_as

        session.save()
        return session

    def clean(self, *args, **kwargs):
        if not self.is_ebgp() and not self.is_ibgp():
            self.add_error(None, 'Please fill either eBGP or iBGP fields')
        elif self.is_ebgp() and self.is_ibgp():
            self.add_error(None, 'Please fill only one set of eBGP or iBGP fields')

        return super().clean(*args, **kwargs)

    def is_ebgp(self):
        return self.data['remote_address'] and \
                len(self.data['remote_address']) > 0 and \
                self.data['remote_as'] and \
                len(self.data['remote_as']) > 0

    def is_ibgp(self):
        return self.data['ibgp_address'] and \
                len(self.data['ibgp_address']) > 0 and \
                self.data['ibgp_device'] and \
                len(self.data['ibgp_device']) > 0

    def clean_remote_address(self):
        if self.is_ibgp():
            return None

        try:
            ip = IPAddress.objects.get(address=str(self.cleaned_data['remote_address']))
        except MultipleObjectsReturned:
            ip = IPAddress.objects.filter(address=str(self.cleaned_data['remote_address'])).first()
        except ObjectDoesNotExist:
            ip = IPAddress.objects.create(address=str(self.cleaned_data['remote_address']))
        self.cleaned_data['remote_address'] = ip
        return self.cleaned_data['remote_address']


class BGPSessionFilterForm(BootstrapMixin, CustomFieldModelForm):
    q = forms.CharField(
        required=False,
        label='Search'
    )
    remote_as = DynamicModelMultipleChoiceField(
        queryset=ASN.objects.all(),
        required=False,
        display_field='number',
        widget=APISelectMultiple(
            api_url='/api/plugins/bgp/asn/',
        )
    )
    local_as = DynamicModelMultipleChoiceField(
        queryset=ASN.objects.all(),
        required=False,
        display_field='number',
        widget=APISelectMultiple(
            api_url='/api/plugins/bgp/asn/',
        )
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    status = forms.MultipleChoiceField(
        choices=SessionStatusChoices,
        required=False,
        widget=StaticSelect2Multiple()
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

    tag = TagFilterField(BGPSession)

    class Meta:
        model = BGPSession
        fields = ['q', 'status', 'tenant', 'remote_as', 'local_as']


class RoutingPolicyFilterForm(BootstrapMixin, CustomFieldModelForm):
    q = forms.CharField(
        required=False,
        label='Search'
    )

    tag = TagFilterField(RoutingPolicy)

    class Meta:
        model = RoutingPolicy
        fields = ['q']


class RoutingPolicyForm(BootstrapMixin, CustomFieldModelForm):
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = RoutingPolicy
        fields = ['name', 'description']
