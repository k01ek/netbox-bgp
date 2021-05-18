from netbox.views import generic

from .filters import ASNFilterSet, CommunityFilterSet, BGPSessionFilterSet, RoutingPolicyFilterSet
from .models import ASN, Community, BGPSession, RoutingPolicy
from .tables import ASNTable, CommunityTable, BGPSessionTable, RoutingPolicyTable
from .forms import (
    ASNFilterForm, ASNBulkEditForm, ASNForm, CommunityForm,
    CommunityFilterForm, CommunityBulkEditForm, BGPSessionForm,
    BGPSessionFilterForm, BGPSessionAddForm, RoutingPolicyFilterForm,
    RoutingPolicyForm
)


class ASNListView(generic.ObjectListView):
    queryset = ASN.objects.all()
    filterset = ASNFilterSet
    filterset_form = ASNFilterForm
    table = ASNTable
    action_buttons = ()
    template_name = 'netbox_bgp/asn_list.html'


class ASNView(generic.ObjectView):
    queryset = ASN.objects.all()
    template_name = 'netbox_bgp/asn.html'

    def get_extra_context(self, request, instance):
        sess = BGPSession.objects.filter(remote_as=instance) | BGPSession.objects.filter(local_as=instance)
        sess_table = BGPSessionTable(sess)
        return {
            'related_session_table': sess_table
        }


class ASNEditView(generic.ObjectEditView):
    queryset = ASN.objects.all()
    model_form = ASNForm


class ASNBulkDeleteView(generic.BulkDeleteView):
    queryset = ASN.objects.all()
    table = ASNTable


class ASNBulkEditView(generic.BulkEditView):
    queryset = ASN.objects.all()
    filterset = ASNFilterSet
    table = ASNTable
    form = ASNBulkEditForm


class ASNDeleteView(generic.ObjectDeleteView):
    queryset = ASN.objects.all()


class CommunityListView(generic.ObjectListView):
    queryset = Community.objects.all()
    filterset = CommunityFilterSet
    filterset_form = CommunityFilterForm
    table = CommunityTable
    action_buttons = ()
    template_name = 'netbox_bgp/community_list.html'


class CommunityView(generic.ObjectView):
    queryset = Community.objects.all()
    template_name = 'netbox_bgp/community.html'


class CommunityEditView(generic.ObjectEditView):
    queryset = Community.objects.all()
    model_form = CommunityForm


class CommunityBulkDeleteView(generic.BulkDeleteView):
    queryset = Community.objects.all()
    table = CommunityTable


class CommunityBulkEditView(generic.BulkEditView):
    queryset = Community.objects.all()
    filterset = CommunityFilterSet
    table = CommunityTable
    form = CommunityBulkEditForm


class CommunityDeleteView(generic.ObjectDeleteView):
    queryset = Community.objects.all()


class BGPSessionListView(generic.ObjectListView):
    queryset = BGPSession.objects.all()
    filterset = BGPSessionFilterSet
    filterset_form = BGPSessionFilterForm
    table = BGPSessionTable
    action_buttons = ()
    template_name = 'netbox_bgp/bgpsession_list.html'


class BGPSessionEditView(generic.ObjectEditView):
    queryset = BGPSession.objects.all()
    model_form = BGPSessionForm
    template_name = 'netbox_bgp/bgpsession_edit.html'


class BGPSessionAddView(generic.ObjectEditView):
    queryset = BGPSession.objects.all()
    model_form = BGPSessionAddForm
    template_name = 'netbox_bgp/bgpsession_edit.html'


class BGPSessionBulkDeleteView(generic.BulkDeleteView):
    queryset = BGPSession.objects.all()
    table = BGPSessionTable


class BGPSessionView(generic.ObjectView):
    queryset = BGPSession.objects.all()
    template_name = 'netbox_bgp/bgpsession.html'

    def get_extra_context(self, request, instance):
        import_policies_table = RoutingPolicyTable(
            instance.import_policies.all(),
            orderable=False
        )
        export_policies_table = RoutingPolicyTable(
            instance.export_policies.all(),
            orderable=False
        )

        return {
            'import_policies_table': import_policies_table,
            'export_policies_table': export_policies_table
        }


class BGPSessionDeleteView(generic.ObjectDeleteView):
    queryset = BGPSession.objects.all()


class RoutingPolicyListView(generic.ObjectListView):
    queryset = RoutingPolicy.objects.all()
    filterset = RoutingPolicyFilterSet
    filterset_form = RoutingPolicyFilterForm
    table = RoutingPolicyTable
    action_buttons = ()
    template_name = 'netbox_bgp/routingpolicy_list.html'


class RoutingPolicyEditView(generic.ObjectEditView):
    queryset = RoutingPolicy.objects.all()
    model_form = RoutingPolicyForm


class RoutingPolicyBulkDeleteView(generic.BulkDeleteView):
    queryset = RoutingPolicy.objects.all()
    table = RoutingPolicyTable


class RoutingPolicyView(generic.ObjectView):
    queryset = RoutingPolicy.objects.all()
    template_name = 'netbox_bgp/routingpolicy.html'

    def get_extra_context(self, request, instance):
        sess = BGPSession.objects.filter(import_policies=instance) | BGPSession.objects.filter(export_policies=instance)
        sess = sess.distinct()
        sess_table = BGPSessionTable(sess)
        return {
            'related_session_table': sess_table
        }


class RoutingPolicyDeleteView(generic.ObjectDeleteView):
    queryset = RoutingPolicy.objects.all()
