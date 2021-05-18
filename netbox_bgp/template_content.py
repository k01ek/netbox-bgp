from django.db.models import Q
from extras.plugins import PluginTemplateExtension

from .models import BGPSession
from .tables import BGPSessionTable


class DeviceBGPSession(PluginTemplateExtension):
    model = 'dcim.device'

    def left_page(self):
        if self.context['config'].get('device_ext_page') == 'left':
            return self.x_page()
        return ''

    def right_page(self):
        if self.context['config'].get('device_ext_page') == 'right':
            return self.x_page()
        return ''

    def full_width_page(self):
        if self.context['config'].get('device_ext_page') == 'full_width':
            return self.x_page()
        return ''

    def x_page(self):
        obj = self.context['object']
        sess = BGPSession.objects.filter(Q(device=obj) | Q(ibgp_device=obj))
        sess_table = BGPSessionTable(sess)
        return self.render(
            'netbox_bgp/device_extend.html',
            extra_context={
                'related_session_table': sess_table
            }
        )


template_extensions = [DeviceBGPSession]
