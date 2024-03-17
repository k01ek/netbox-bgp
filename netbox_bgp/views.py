
from django.db.models import Q
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils.text import slugify

from netbox.views import generic
from ipam.models import ASN

from .models import (
    Community, BGPSession, RoutingPolicy,
    BGPPeerGroup, RoutingPolicyRule, PrefixList,
    PrefixListRule, CommunityList, CommunityListRule
)

from . import filtersets, forms, tables


# Community

class CommunityListView(generic.ObjectListView):
    queryset = Community.objects.all()
    filterset = filtersets.CommunityFilterSet
    filterset_form = forms.CommunityFilterForm
    table = tables.CommunityTable
    action_buttons = ('add',)


class CommunityView(generic.ObjectView):
    queryset = Community.objects.all()
    template_name = 'netbox_bgp/community.html'


class CommunityEditView(generic.ObjectEditView):
    queryset = Community.objects.all()
    form = forms.CommunityForm


class CommunityBulkDeleteView(generic.BulkDeleteView):
    queryset = Community.objects.all()
    table = tables.CommunityTable


class CommunityBulkEditView(generic.BulkEditView):
    queryset = Community.objects.all()
    filterset = filtersets.CommunityFilterSet
    table = tables.CommunityTable
    form = forms.CommunityBulkEditForm


class CommunityDeleteView(generic.ObjectDeleteView):
    queryset = Community.objects.all()
    default_return_url = 'plugins:netbox_bgp:community_list'


class CommunityBulkImportView(generic.BulkImportView):
    queryset = Community.objects.all()
    model_form = forms.CommunityImportForm


# Community List


class CommunityListListView(generic.ObjectListView):
    queryset = CommunityList.objects.all()
    filterset = filtersets.CommunityListFilterSet
    filterset_form = forms.CommunityListFilterForm
    table = tables.CommunityListTable
    action_buttons = ('add',)


class CommunityListEditView(generic.ObjectEditView):
    queryset = CommunityList.objects.all()
    form = forms.CommunityListForm


class CommunityListBulkDeleteView(generic.BulkDeleteView):
    queryset = CommunityList.objects.all()
    table = tables.CommunityListTable


class CommListView(generic.ObjectView):
    queryset = CommunityList.objects.all()
    template_name = 'netbox_bgp/communitylist.html'

    def get_extra_context(self, request, instance):
        rprules = instance.cmrules.all()
        rprules_table = tables.RoutingPolicyRuleTable(rprules)
        rules = instance.commlistrules.all()
        rules_table = tables.CommunityListRuleTable(rules)
        return {
            'rules_table': rules_table,
            'rprules_table': rprules_table
        }


class CommunityListDeleteView(generic.ObjectDeleteView):
    queryset = CommunityList.objects.all()
    default_return_url = 'plugins:netbox_bgp:communitylist_list'


# Community List Rule


class CommunityListRuleListView(generic.ObjectListView):
    queryset = CommunityListRule.objects.all()
    filterset = filtersets.CommunityListRuleFilterSet
    # filterset_form = RoutingPolicyRuleFilterForm
    table = tables.CommunityListRuleTable
    action_buttons = ('add',)


class CommunityListRuleEditView(generic.ObjectEditView):
    queryset = CommunityListRule.objects.all()
    form = forms.CommunityListRuleForm


class CommunityListRuleBulkDeleteView(generic.BulkDeleteView):
    queryset = CommunityListRule.objects.all()
    table = tables.CommunityListRuleTable


class CommunityListRuleDeleteView(generic.ObjectDeleteView):
    queryset = CommunityListRule.objects.all()
    default_return_url = 'plugins:netbox_bgp:communitylistrule_list'


class CommunityListRuleView(generic.ObjectView):
    queryset = CommunityListRule.objects.all()
    template_name = 'netbox_bgp/communitylistrule.html'


# Session


class BGPSessionListView(generic.ObjectListView):
    queryset = BGPSession.objects.all()
    filterset = filtersets.BGPSessionFilterSet
    filterset_form = forms.BGPSessionFilterForm
    table = tables.BGPSessionTable
    action_buttons = ('add',)


class BGPSessionEditView(generic.ObjectEditView):
    queryset = BGPSession.objects.all()
    form = forms.BGPSessionForm


class BGPSessionAddView(generic.ObjectEditView):
    queryset = BGPSession.objects.all()
    form = forms.BGPSessionAddForm

class BGPSessionBulkImportView(generic.BulkImportView):
    queryset = BGPSession.objects.all()
    model_form = forms.BGPSessionImportForm

class BGPSessionBulkEditView(generic.BulkEditView):
    queryset = BGPSession.objects.all()
    filterset = filtersets.BGPSessionFilterSet
    table = tables.BGPSessionTable
    form = forms.BGPSessionBulkEditForm

class BGPSessionBulkDeleteView(generic.BulkDeleteView):
    queryset = BGPSession.objects.all()
    table = tables.BGPSessionTable


class BGPSessionView(generic.ObjectView):
    queryset = BGPSession.objects.all()
    template_name = 'netbox_bgp/bgpsession.html'

    def get_extra_context(self, request, instance):
        import_policies_qs = instance.import_policies.all()
        if not import_policies_qs and instance.peer_group:
            import_policies_qs = instance.peer_group.import_policies.all()
        export_policies_qs = instance.export_policies.all()
        if not export_policies_qs and instance.peer_group:
            export_policies_qs = instance.peer_group.export_policies.all()

        import_policies_table = tables.RoutingPolicyTable(
            import_policies_qs,
            orderable=False
        )
        export_policies_table = tables.RoutingPolicyTable(
            export_policies_qs,
            orderable=False
        )

        return {
            'import_policies_table': import_policies_table,
            'export_policies_table': export_policies_table
        }


class BGPSessionDeleteView(generic.ObjectDeleteView):
    queryset = BGPSession.objects.all()
    default_return_url = 'plugins:netbox_bgp:bgpsession_list'


# Routing Policy


class RoutingPolicyListView(generic.ObjectListView):
    queryset = RoutingPolicy.objects.all()
    filterset = filtersets.RoutingPolicyFilterSet
    filterset_form = forms.RoutingPolicyFilterForm
    table = tables.RoutingPolicyTable
    action_buttons = ('add',)


class RoutingPolicyEditView(generic.ObjectEditView):
    queryset = RoutingPolicy.objects.all()
    form = forms.RoutingPolicyForm


class RoutingPolicyBulkDeleteView(generic.BulkDeleteView):
    queryset = RoutingPolicy.objects.all()
    table = tables.RoutingPolicyTable


class RoutingPolicyView(generic.ObjectView):
    queryset = RoutingPolicy.objects.all()
    template_name = 'netbox_bgp/routingpolicy.html'

    def get_extra_context(self, request, instance):
        sess = BGPSession.objects.filter(
            Q(import_policies=instance)
            | Q(export_policies=instance)
            | Q(peer_group__in=instance.group_import_policies.all())
            | Q(peer_group__in=instance.group_export_policies.all())
        )
        sess = sess.distinct()
        sess_table = tables.BGPSessionTable(sess)
        rules = instance.rules.all()
        rules_table = tables.RoutingPolicyRuleTable(rules)
        return {
            'rules_table': rules_table,
            'related_session_table': sess_table
        }


class RoutingPolicyDeleteView(generic.ObjectDeleteView):
    queryset = RoutingPolicy.objects.all()
    default_return_url = 'plugins:netbox_bgp:routingpolicy_list'


# Routing Policy Rule


class RoutingPolicyRuleEditView(generic.ObjectEditView):
    queryset = RoutingPolicyRule.objects.all()
    form = forms.RoutingPolicyRuleForm


class RoutingPolicyRuleDeleteView(generic.ObjectDeleteView):
    queryset = RoutingPolicyRule.objects.all()
    default_return_url = 'plugins:netbox_bgp:routingpolicyrule_list'


class RoutingPolicyRuleView(generic.ObjectView):
    queryset = RoutingPolicyRule.objects.all()
    template_name = 'netbox_bgp/routingpolicyrule.html'

    def get_extra_context(self, request, instance):
        if request.GET.get('format') in ['json', 'yaml']:
            format = request.GET.get('format')
            if request.user.is_authenticated:
                request.user.config.set('data_format', format, commit=True)
        elif request.user.is_authenticated:
            format = request.user.config.get('data_format', 'json')
        else:
            format = 'json'

        return {
            'format': format,
        }


class RoutingPolicyRuleListView(generic.ObjectListView):
    queryset = RoutingPolicyRule.objects.all()
    filterset = filtersets.RoutingPolicyRuleFilterSet
    # filterset_form = RoutingPolicyRuleFilterForm
    table = tables.RoutingPolicyRuleTable
    action_buttons = ('add',)


# Peer Group


class BGPPeerGroupListView(generic.ObjectListView):
    queryset = BGPPeerGroup.objects.all()
    filterset = filtersets.BGPPeerGroupFilterSet
    filterset_form = forms.BGPPeerGroupFilterForm
    table = tables.BGPPeerGroupTable
    action_buttons = ('add',)


class BGPPeerGroupEditView(generic.ObjectEditView):
    queryset = BGPPeerGroup.objects.all()
    form = forms.BGPPeerGroupForm


class BGPPeerGroupBulkDeleteView(generic.BulkDeleteView):
    queryset = BGPPeerGroup.objects.all()
    table = tables.BGPPeerGroupTable


class BGPPeerGroupView(generic.ObjectView):
    queryset = BGPPeerGroup.objects.all()
    template_name = 'netbox_bgp/bgppeergroup.html'

    def get_extra_context(self, request, instance):
        import_policies_table = tables.RoutingPolicyTable(
            instance.import_policies.all(),
            orderable=False
        )
        export_policies_table = tables.RoutingPolicyTable(
            instance.export_policies.all(),
            orderable=False
        )

        sess = BGPSession.objects.filter(peer_group=instance)
        sess = sess.distinct()
        sess_table = tables.BGPSessionTable(sess)
        return {
            'import_policies_table': import_policies_table,
            'export_policies_table': export_policies_table,
            'related_session_table': sess_table
        }


class BGPPeerGroupDeleteView(generic.ObjectDeleteView):
    queryset = BGPPeerGroup.objects.all()
    default_return_url = 'plugins:netbox_bgp:bgppeergroup_list'


# Prefix List


class PrefixListListView(generic.ObjectListView):
    queryset = PrefixList.objects.all()
    filterset = filtersets.PrefixListFilterSet
    filterset_form = forms.PrefixListFilterForm
    table = tables.PrefixListTable
    action_buttons = ('add',)


class PrefixListEditView(generic.ObjectEditView):
    queryset = PrefixList.objects.all()
    form = forms.PrefixListForm


class PrefixListBulkDeleteView(generic.BulkDeleteView):
    queryset = PrefixList.objects.all()
    table = tables.PrefixListTable


class PrefixListView(generic.ObjectView):
    queryset = PrefixList.objects.all()
    template_name = 'netbox_bgp/prefixlist.html'

    def get_extra_context(self, request, instance):
        rprules = instance.plrules.all()
        rprules_table = tables.RoutingPolicyRuleTable(rprules)
        rules = instance.prefrules.all()
        rules_table = tables.PrefixListRuleTable(rules)

        sess = instance.session_prefix_in.all() | instance.session_prefix_out.all()
        sess_table = tables.BGPSessionTable(sess)
        return {
            'rules_table': rules_table,
            'rprules_table': rprules_table,
            'sess_table': sess_table,
        }


class PrefixListDeleteView(generic.ObjectDeleteView):
    queryset = PrefixList.objects.all()
    default_return_url = 'plugins:netbox_bgp:prefixlist_list'


# Prefix List Rule


class PrefixListRuleListView(generic.ObjectListView):
    queryset = PrefixListRule.objects.all()
    filterset = filtersets.PrefixListRuleFilterSet
    # filterset_form = RoutingPolicyRuleFilterForm
    table = tables.PrefixListRuleTable
    action_buttons = ('add',)


class PrefixListRuleEditView(generic.ObjectEditView):
    queryset = PrefixListRule.objects.all()
    form = forms.PrefixListRuleForm


class PrefixListRuleBulkDeleteView(generic.BulkDeleteView):
    queryset = PrefixListRule.objects.all()
    table = tables.PrefixListRuleTable


class PrefixListRuleDeleteView(generic.ObjectDeleteView):
    queryset = PrefixListRule.objects.all()
    default_return_url = 'plugins:netbox_bgp:prefixlistrule_list'


class PrefixListRuleView(generic.ObjectView):
    queryset = PrefixListRule.objects.all()
    template_name = 'netbox_bgp/prefixlistrule.html'
