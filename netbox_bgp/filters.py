import django_filters
import netaddr
from django.db.models import Q
from netaddr.core import AddrFormatError
from extras.filters import TagFilter

from .models import Community, BGPSession, RoutingPolicy, BGPPeerGroup
from ipam.models import IPAddress, ASN
from dcim.models import Device


class CommunityFilterSet(django_filters.FilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    tag = TagFilter()

    class Meta:
        model = Community
        fields = ['value', 'description', 'status', 'tenant']

    def search(self, queryset, name, value):
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = (
                Q(id__icontains=value)
                | Q(value__icontains=value)
                | Q(description__icontains=value)
        )
        return queryset.filter(qs_filter)


class BGPSessionFilterSet(django_filters.FilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    tag = TagFilter()

    remote_as = django_filters.ModelMultipleChoiceFilter(
        field_name='remote_as__number',
        queryset=ASN.objects.all(),
        to_field_name='asn',
        label='Remote AS (Number)',
    )
    remote_as_id = django_filters.ModelMultipleChoiceFilter(
        field_name='remote_as__id',
        queryset=ASN.objects.all(),
        to_field_name='id',
        label='Remote AS (ID)',
    )
    local_as = django_filters.ModelMultipleChoiceFilter(
        field_name='local_as__number',
        queryset=ASN.objects.all(),
        to_field_name='asn',
        label='Local AS (Number)',
    )
    local_as_id = django_filters.ModelMultipleChoiceFilter(
        field_name='local_as__id',
        queryset=ASN.objects.all(),
        to_field_name='id',
        label='Local AS (ID)',
    )
    peer_group = django_filters.ModelMultipleChoiceFilter(
        queryset=BGPPeerGroup.objects.all(),
    )
    import_policies = django_filters.ModelMultipleChoiceFilter(
        queryset=RoutingPolicy.objects.all(),
    )
    export_policies = django_filters.ModelMultipleChoiceFilter(
        queryset=RoutingPolicy.objects.all(),
    )
    local_address_id = django_filters.ModelMultipleChoiceFilter(
        field_name='local_address__id',
        queryset=IPAddress.objects.all(),
        to_field_name='id',
        label='Local Address (ID)',
    )
    local_address = django_filters.ModelMultipleChoiceFilter(
        field_name='local_address__address',
        queryset=IPAddress.objects.all(),
        to_field_name='address',
        label='Local Address',
    )
    remote_address_id = django_filters.ModelMultipleChoiceFilter(
        field_name='remote_address__id',
        queryset=IPAddress.objects.all(),
        to_field_name='id',
        label='Remote Address (ID)',
    )
    remote_address = django_filters.ModelMultipleChoiceFilter(
        field_name='remote_address__address',
        queryset=IPAddress.objects.all(),
        to_field_name='address',
        label='Remote Address',
    )
    device_id = django_filters.ModelMultipleChoiceFilter(
        field_name='device__id',
        queryset=Device.objects.all(),
        to_field_name='id',
        label='Device (ID)',
    )
    device = django_filters.ModelMultipleChoiceFilter(
        field_name='device__name',
        queryset=Device.objects.all(),
        to_field_name='name',
        label='Device (name)',
    )
    by_remote_address = django_filters.CharFilter(
        method='search_by_remote_ip',
        label='Remote Address',
    )
    by_local_address = django_filters.CharFilter(
        method='search_by_local_ip',
        label='Local Address',
    )

    class Meta:
        model = BGPSession
        fields = ['name', 'description', 'status', 'tenant']

    def search(self, queryset, name, value):
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = (
                Q(remote_as__number__icontains=value)
                | Q(name__icontains=value)
                | Q(local_as__number__icontains=value)
                | Q(description__icontains=value)
        )
        return queryset.filter(qs_filter)

    def search_by_remote_ip(self, queryset, name, value):
        if not value.strip():
            return queryset
        try:
            query = str(netaddr.IPNetwork(value).cidr)
            return queryset.filter(remote_address__address=query)
        except (AddrFormatError, ValueError):
            return queryset.none()

    def search_by_local_ip(self, queryset, name, value):
        if not value.strip():
            return queryset
        try:
            query = str(netaddr.IPNetwork(value).cidr)
            return queryset.filter(local_address__address=query)
        except (AddrFormatError, ValueError):
            return queryset.none()


class RoutingPolicyFilterSet(django_filters.FilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    tag = TagFilter()

    class Meta:
        model = RoutingPolicy
        fields = ['name', 'description']

    def search(self, queryset, name, value):
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = (
                Q(name__icontains=value)
                | Q(description__icontains=value)
        )
        return queryset.filter(qs_filter)


class BGPPeerGroupFilterSet(django_filters.FilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    tag = TagFilter()

    class Meta:
        model = BGPPeerGroup
        fields = ['name', 'description']

    def search(self, queryset, name, value):
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = (
                Q(name__icontains=value)
                | Q(description__icontains=value)
        )
        return queryset.filter(qs_filter)
