from django.urls import path
from extras.views import ObjectChangeLogView
from .models import BGPSession, Community, RoutingPolicy, BGPPeerGroup

from .views import (
    CommunityListView, CommunityEditView, CommunityView,
    CommunityBulkEditView, CommunityBulkDeleteView, CommunityDeleteView,
    BGPSessionListView, BGPSessionEditView, BGPSessionBulkDeleteView,
    BGPSessionView, BGPSessionDeleteView, BGPSessionAddView,
    RoutingPolicyListView, RoutingPolicyEditView, RoutingPolicyBulkDeleteView,
    RoutingPolicyView, RoutingPolicyDeleteView, BGPPeerGroupListView,
    BGPPeerGroupEditView, BGPPeerGroupBulkDeleteView, BGPPeerGroupView,
    BGPPeerGroupDeleteView
)

urlpatterns = [
    # Community
    path('community/', CommunityListView.as_view(), name='community_list'),
    path('community/add/', CommunityEditView.as_view(), name='community_add'),
    path('community/edit/', CommunityBulkEditView.as_view(), name='community_bulk_edit'),
    path('community/delete/', CommunityBulkDeleteView.as_view(), name='community_bulk_delete'),
    path('community/<int:pk>/', CommunityView.as_view(), name='community'),
    path('community/<int:pk>/edit/', CommunityEditView.as_view(), name='community_edit'),
    path('community/<int:pk>/delete/', CommunityDeleteView.as_view(), name='community_delete'),
    path('community/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='community_changelog', kwargs={'model': Community}),
    # Sessions
    path('session/', BGPSessionListView.as_view(), name='session_list'),
    path('session/add/', BGPSessionAddView.as_view(), name='session_add'),
    path('session/delete/', BGPSessionBulkDeleteView.as_view(), name='session_bulk_delete'),
    path('session/<int:pk>/', BGPSessionView.as_view(), name='session'),
    path('session/<int:pk>/edit/', BGPSessionEditView.as_view(), name='session_edit'),
    path('session/<int:pk>/delete/', BGPSessionDeleteView.as_view(), name='session_delete'),
    path('session/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='session_changelog', kwargs={'model': BGPSession}),
    # Routing Policies
    path('routing-policy/<int:pk>/', RoutingPolicyView.as_view(), name='routing_policy'),
    path('routing-policy/', RoutingPolicyListView.as_view(), name='routing_policy_list'),
    path('routing-policy/add/', RoutingPolicyEditView.as_view(), name='routing_policy_add'),
    path('routing-policy/<int:pk>/edit/', RoutingPolicyEditView.as_view(), name='routing_policy_edit'),
    path('routing-policy/delete/', RoutingPolicyBulkDeleteView.as_view(), name='routing_policy_bulk_delete'),
    path('routing-policy/<int:pk>/delete/', RoutingPolicyDeleteView.as_view(), name='routing_policy_delete'),
    path('routing-policy/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='routing_policy_changelog', kwargs={'model': RoutingPolicy}),
    # Peer Groups
    path('peer-group/', BGPPeerGroupListView.as_view(), name='peergroup_list'),
    path('peer-group/add/', BGPPeerGroupEditView.as_view(), name='peergroup_add'),
    path('peer-group/delete/', BGPPeerGroupBulkDeleteView.as_view(), name='peergroup_bulk_delete'),
    path('peer-group/<int:pk>/', BGPPeerGroupView.as_view(), name='peergroup'),
    path('peer-group/<int:pk>/edit/', BGPPeerGroupEditView.as_view(), name='peergroup_edit'),
    path('peer-group/<int:pk>/delete/', BGPPeerGroupDeleteView.as_view(), name='peergroup_delete'),
    path('peer-group/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='peergroup_changelog', kwargs={'model': BGPPeerGroup}),
]
