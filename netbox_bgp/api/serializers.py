from rest_framework.serializers import Serializer, HyperlinkedIdentityField, ValidationError
from rest_framework.relations import PrimaryKeyRelatedField

from netbox.api import ChoiceField, WritableNestedSerializer, ValidatedModelSerializer
from netbox.api.serializers import NetBoxModelSerializer
from dcim.api.nested_serializers import NestedSiteSerializer, NestedDeviceSerializer
from tenancy.api.nested_serializers import NestedTenantSerializer
from extras.api.nested_serializers import NestedTagSerializer
from ipam.api.nested_serializers import NestedIPAddressSerializer, NestedASNSerializer


from netbox_bgp.models import (
    CommunityStatusChoices, BGPSession, SessionStatusChoices, RoutingPolicy, BGPPeerGroup,
    Community, RoutingPolicyRule
)


class SerializedPKRelatedField(PrimaryKeyRelatedField):
    def __init__(self, serializer, **kwargs):
        self.serializer = serializer
        self.pk_field = kwargs.pop('pk_field', None)
        super().__init__(**kwargs)

    def to_representation(self, value):
        return self.serializer(value, context={'request': self.context['request']}).data


class RoutingPolicySerializer(NetBoxModelSerializer):
    class Meta:
        model = RoutingPolicy
        fields = '__all__'


class NestedRoutingPolicySerializer(WritableNestedSerializer):
    url = HyperlinkedIdentityField(view_name='plugins:netbox_bgp:routingpolicy')

    class Meta:
        model = RoutingPolicy
        fields = ['id', 'url', 'name', 'description']


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
        fields = '__all__'


class NestedBGPPeerGroupSerializer(WritableNestedSerializer):
    url = HyperlinkedIdentityField(view_name='plugins:netbox_bgp:bgppeergroup')

    class Meta:
        model = BGPPeerGroup
        fields = ['id', 'url', 'name', 'description']
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
        fields = '__all__'
        validators = []

    def validate(self, attrs):
        qs = BGPSession.objects.filter(
            device=attrs.get('device'),
            local_as=attrs.get('local_as'),
            local_address=attrs.get('local_address'),
            remote_as=attrs.get('remote_as'),
            remote_address=attrs.get('remote_address'),
        )
        if qs.exists():
            raise ValidationError(
                {'error': 'BGP Session with this Device, Local address, Local AS, Remote address and Remote AS already exists.'}
            )
        return attrs

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
        fields = ['id', 'url', 'name', 'description']
        validators = []

class CommunitySerializer(NetBoxModelSerializer):
    status = ChoiceField(choices=CommunityStatusChoices, required=False)
    tenant = NestedTenantSerializer(required=False, allow_null=True)

    class Meta:
        model = Community
        # fields = ['id', 'value', 'status', 'description', 'tenant', 'tags']
        fields = '__all__'


class RoutingPolicyRuleSerializer(NetBoxModelSerializer):
    class Meta:
        model = RoutingPolicyRule
        fields = '__all__'
