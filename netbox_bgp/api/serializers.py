from rest_framework.serializers import HyperlinkedIdentityField, ValidationError
from rest_framework.relations import PrimaryKeyRelatedField

from netbox.api.fields import ChoiceField, SerializedPKRelatedField
from netbox.api.serializers.nested import WritableNestedSerializer

from netbox.api.serializers import NetBoxModelSerializer
from dcim.api.nested_serializers import NestedSiteSerializer, NestedDeviceSerializer
from tenancy.api.nested_serializers import NestedTenantSerializer
from ipam.api.nested_serializers import NestedIPAddressSerializer, NestedASNSerializer, NestedPrefixSerializer
from ipam.api.field_serializers import IPNetworkField


from netbox_bgp.models import (
    BGPSession, RoutingPolicy, BGPPeerGroup,
    Community, RoutingPolicyRule, PrefixList,
    PrefixListRule, CommunityList, CommunityListRule
)

from netbox_bgp.choices import CommunityStatusChoices, SessionStatusChoices


class RoutingPolicySerializer(NetBoxModelSerializer):
    class Meta:
        model = RoutingPolicy        
        fields = ['id', 'name', 'display', 'description', 'tags', 'custom_fields', 'comments']


class NestedRoutingPolicySerializer(WritableNestedSerializer):
    url = HyperlinkedIdentityField(view_name='plugins:netbox_bgp:routingpolicy')

    class Meta:
        model = RoutingPolicy
        fields = ['id', 'url', 'name', 'display', 'description']        
        validators = []


class NestedPrefixListSerializer(WritableNestedSerializer):
    url = HyperlinkedIdentityField(view_name='plugins:netbox_bgp:prefixlist')

    class Meta:
        model = PrefixList
        fields = ['id', 'url', 'display', 'name', 'description']


class PrefixListSerializer(NetBoxModelSerializer):
    class Meta:
        model = PrefixList
        fields = ['id', 'name', 'display','description', 'family', 'tags', 'custom_fields', 'comments']


class BGPPeerGroupSerializer(NetBoxModelSerializer):
    import_policies = SerializedPKRelatedField(
        queryset=RoutingPolicy.objects.all(),
        serializer=NestedRoutingPolicySerializer,
        required=False,
        allow_null=True,
        many=True
    )
    export_policies = SerializedPKRelatedField(
        queryset=RoutingPolicy.objects.all(),
        serializer=NestedRoutingPolicySerializer,
        required=False,
        allow_null=True,
        many=True
    )

    class Meta:
        model = BGPPeerGroup
        fields = ['id', 'display', 'name', 'description', 'import_policies', 'export_policies', 'comments', 'tags', 'custom_fields' ]


class NestedBGPPeerGroupSerializer(WritableNestedSerializer):
    url = HyperlinkedIdentityField(view_name='plugins:netbox_bgp:bgppeergroup')

    class Meta:
        model = BGPPeerGroup
        fields = ['id', 'display', 'url', 'name', 'description']
        validators = []


class BGPSessionSerializer(NetBoxModelSerializer):
    status = ChoiceField(choices=SessionStatusChoices, required=False)
    site = NestedSiteSerializer(required=False, allow_null=True)
    tenant = NestedTenantSerializer(required=False, allow_null=True)
    device = NestedDeviceSerializer(required=False, allow_null=True)
    local_address = NestedIPAddressSerializer(required=True, allow_null=False)
    remote_address = NestedIPAddressSerializer(required=True, allow_null=False)
    local_as = NestedASNSerializer(required=True, allow_null=False)
    remote_as = NestedASNSerializer(required=True, allow_null=False)
    peer_group = NestedBGPPeerGroupSerializer(required=False, allow_null=True)
    prefix_list_in = NestedPrefixListSerializer(required=False, allow_null=True)
    prefix_list_out = NestedPrefixListSerializer(required=False, allow_null=True)
    import_policies = SerializedPKRelatedField(
        queryset=RoutingPolicy.objects.all(),
        serializer=NestedRoutingPolicySerializer,
        required=False,
        allow_null=True,
        many=True
    )
    export_policies = SerializedPKRelatedField(
        queryset=RoutingPolicy.objects.all(),
        serializer=NestedRoutingPolicySerializer,
        required=False,
        allow_null=True,
        many=True
    )

    class Meta:
        model = BGPSession
        fields = [
            'id', 'tags', 'custom_fields',
            'display', 'status', 'site', 'tenant',
            'device', 'local_address', 'remote_address',
            'local_as', 'remote_as', 'peer_group', 'import_policies',
            'export_policies', 'prefix_list_in','prefix_list_out',
            'created', 'last_updated',
            'name', 'description', 'comments'
            ]


    def to_representation(self, instance):
        ret = super().to_representation(instance)

        if instance is not None:
            if instance.peer_group:
                for pol in instance.peer_group.import_policies.difference(instance.import_policies.all()):
                    ret['import_policies'].append(
                        NestedRoutingPolicySerializer(pol, context={'request': self.context['request']}).data
                    )
                for pol in instance.peer_group.export_policies.difference(instance.export_policies.all()):
                    ret['export_policies'].append(
                        NestedRoutingPolicySerializer(pol, context={'request': self.context['request']}).data
                    )
        return ret


class NestedBGPSessionSerializer(WritableNestedSerializer):
    url = HyperlinkedIdentityField(view_name='plugins:netbox_bgp:bgpsession')

    class Meta:
        model = BGPSession
        fields = ['id', 'url', 'name', 'display','description']
        validators = []


class CommunitySerializer(NetBoxModelSerializer):
    status = ChoiceField(choices=CommunityStatusChoices, required=False)
    tenant = NestedTenantSerializer(required=False, allow_null=True)

    class Meta:
        model = Community
        fields = [
            'id', 'tags', 'custom_fields', 'display',
            'status', 'tenant', 'created', 'last_updated',
            'description',
            'value', 'site', 'role', 'comments'
        ]

class NestedCommunitySerializer(WritableNestedSerializer):
    url = HyperlinkedIdentityField(view_name='plugins:netbox_bgp:community')

    class Meta:
        model = Community
        fields = [
            'id', 'url', 'display', 'value', 'description'
        ]


class CommunityListSerializer(NetBoxModelSerializer):
    class Meta:
        model = CommunityList
        fields = ['id', 'name', 'display','description', 'tags', 'custom_fields', 'comments']


class NestedCommunityListSerializer(WritableNestedSerializer):
    url = HyperlinkedIdentityField(view_name='plugins:netbox_bgp:communitylist')

    class Meta:
        model = CommunityList
        fields = ['id', 'url', 'display', 'name', 'description']


class CommunityListRuleSerializer(NetBoxModelSerializer):
    community_list = NestedCommunityListSerializer()  
    community = NestedCommunitySerializer(required=False, allow_null=True)

    class Meta:
        model = CommunityListRule
        fields = [
            'id', 'tags', 'custom_fields', 'display',
            'community_list', 'created', 'last_updated',
            'action', 'community', 'comments', 'description',
        ]


class RoutingPolicyRuleSerializer(NetBoxModelSerializer):
    match_ip_address = SerializedPKRelatedField(
        queryset=PrefixList.objects.all(),
        serializer=NestedPrefixListSerializer,
        required=False,
        allow_null=True,
        many=True
    )
    routing_policy = NestedRoutingPolicySerializer()
    match_community = SerializedPKRelatedField(
        queryset=Community.objects.all(),
        serializer=NestedCommunitySerializer,
        required=False,
        allow_null=True,
        many=True
    )
    

    class Meta:
        model = RoutingPolicyRule
        fields = [
            'id', 'index', 'display' ,'action', 'match_ip_address', 
            'routing_policy', 'match_community', 'match_custom', 'set_actions',
            'match_ipv6_address', 'description', 'tags', 'custom_fields', 'comments'
        ]


class PrefixListRuleSerializer(NetBoxModelSerializer):
    prefix_list = NestedPrefixListSerializer()  
    prefix = NestedPrefixSerializer(required=False, allow_null=True)
    prefix_custom = IPNetworkField(required=False, allow_null=True)

    class Meta:
        model = PrefixListRule
        fields = [
            'id', 'tags', 'custom_fields', 'display',
            'prefix_list', 'created', 'last_updated',
            'index', 'action', 'description',
            'prefix_custom', 'ge', 'le', 'prefix', 'comments'
        ]
