from graphene import ObjectType, Field

from netbox.graphql.scalars import BigInt
from netbox.graphql.types import NetBoxObjectType
from netbox.graphql.fields import ObjectField, ObjectListField

from . import models, filters


class CommunityType(NetBoxObjectType):
    class Meta:
        model = models.Community
        fields = '__all__'
        filterset_class = filters.CommunityFilterSet


class BgpSessionType(NetBoxObjectType):
    class Meta:
        model = models.BGPSession
        fields = '__all__'
        filterset_class = filters.BGPSessionFilterSet


class PeerGroupType(NetBoxObjectType):
    class Meta:
        model = models.BGPPeerGroup
        fields = '__all__'
        filterset_class = filters.BGPPeerGroupFilterSet


class RoutingPolicyType(NetBoxObjectType):
    class Meta:
        model = models.RoutingPolicy
        fields = '__all__'
        filterset_class = filters.RoutingPolicyFilterSet


class BGPQuery(ObjectType):
    community = ObjectField(CommunityType)
    community_list = ObjectListField(CommunityType)

    bgp_session = ObjectField(BgpSessionType)
    bgp_session_list = ObjectListField(BgpSessionType)

    peer_group = ObjectField(PeerGroupType)
    peer_group_list = ObjectListField(PeerGroupType)

    routing_policy = ObjectField(RoutingPolicyType)
    routing_policy_list = ObjectListField(RoutingPolicyType)


schema = BGPQuery
