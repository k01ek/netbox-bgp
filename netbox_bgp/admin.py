from django.contrib import admin
from .models import Community, BGPSession, BGPPeerGroup, RoutingPolicy


@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    fields = ('value', 'status', 'description')


@admin.register(BGPSession)
class BGPSessionAdmin(admin.ModelAdmin):
    fields = (
        'name', 'local_address', 'local_as', 'remote_address',
        'remote_as', 'description', 'import_policies', 'export_policies'
    )


@admin.register(BGPPeerGroup)
class BGPpeerGroupAdmin(admin.ModelAdmin):
    fields = ('name', 'description', 'import_policies', 'export_policies')


@admin.register(RoutingPolicy)
class RoutingPolicyAdmin(admin.ModelAdmin):
    fields = ('name', 'description')
