from django.urls import reverse
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.core.exceptions import FieldError
from django.conf import settings

from taggit.managers import TaggableManager

from utilities.choices import ChoiceSet
from netbox.models import NetBoxModel
from netbox.models.features import ChangeLoggingMixin
from ipam.models import Prefix


class CommunityStatusChoices(ChoiceSet):

    STATUS_ACTIVE = 'active'
    STATUS_RESERVED = 'reserved'
    STATUS_DEPRECATED = 'deprecated'

    CHOICES = (
        (STATUS_ACTIVE, 'Active', 'blue'),
        (STATUS_RESERVED, 'Reserved', 'cyan'),
        (STATUS_DEPRECATED, 'Deprecated', 'red'),
    )


class SessionStatusChoices(ChoiceSet):

    STATUS_OFFLINE = 'offline'
    STATUS_ACTIVE = 'active'
    STATUS_PLANNED = 'planned'
    STATUS_FAILED = 'failed'

    CHOICES = (
        (STATUS_OFFLINE, 'Offline', 'orange'),
        (STATUS_ACTIVE, 'Active', 'green'),
        (STATUS_PLANNED, 'Planned', 'cyan'),
        (STATUS_FAILED, 'Failed', 'red'),
    )


class ActionChoices(ChoiceSet):

    CHOICES = [
        ('permit', 'Permit', 'green'),
        ('deny', 'Deny', 'red'),
    ]


class RoutingPolicy(NetBoxModel):
    """
    """
    name = models.CharField(
        max_length=100
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )

    class Meta:
        verbose_name_plural = 'Routing Policies'
        unique_together = ['name', 'description']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('plugins:netbox_bgp:routingpolicy', args=[self.pk])


class BGPPeerGroup(NetBoxModel):
    """
    """
    name = models.CharField(
        max_length=100
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )
    import_policies = models.ManyToManyField(
        RoutingPolicy,
        blank=True,
        related_name='group_import_policies'
    )
    export_policies = models.ManyToManyField(
        RoutingPolicy,
        blank=True,
        related_name='group_export_policies'
    )

    class Meta:
        verbose_name_plural = 'Peer Groups'
        unique_together = ['name', 'description']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('plugins:netbox_bgp:bgppeergroup', args=[self.pk])


class BGPBase(NetBoxModel):
    """
    """
    site = models.ForeignKey(
        to='dcim.Site',
        on_delete=models.PROTECT,
        related_name="%(class)s_related",
        blank=True,
        null=True
    )
    tenant = models.ForeignKey(
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    status = models.CharField(
        max_length=50,
        choices=CommunityStatusChoices,
        default=CommunityStatusChoices.STATUS_ACTIVE
    )
    role = models.ForeignKey(
        to='ipam.Role',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )

    class Meta:
        abstract = True


class Community(BGPBase):
    """
    """
    value = models.CharField(
        max_length=64,
        validators=[RegexValidator(r'\d+:\d+')]
    )

    class Meta:
        verbose_name_plural = 'Communities'

    def __str__(self):
        return self.value

    def get_status_color(self):
        return CommunityStatusChoices.colors.get(self.status)

    def get_absolute_url(self):
        return reverse('plugins:netbox_bgp:community', args=[self.pk])


class BGPSession(NetBoxModel):
    name = models.CharField(
        max_length=64,
        blank=True,
        null=True
    )
    site = models.ForeignKey(
        to='dcim.Site',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    tenant = models.ForeignKey(
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    device = models.ForeignKey(
        to='dcim.Device',
        on_delete=models.PROTECT,
        null=True,
    )
    local_address = models.ForeignKey(
        to='ipam.IPAddress',
        on_delete=models.PROTECT,
        related_name='local_address'
    )
    remote_address = models.ForeignKey(
        to='ipam.IPAddress',
        on_delete=models.PROTECT,
        related_name='remote_address'
    )
    local_as = models.ForeignKey(
        to='ipam.ASN',
        on_delete=models.PROTECT,
        related_name='local_as'
    )
    remote_as = models.ForeignKey(
        to='ipam.ASN',
        on_delete=models.PROTECT,
        related_name='remote_as'
    )
    status = models.CharField(
        max_length=50,
        choices=SessionStatusChoices,
        default=SessionStatusChoices.STATUS_ACTIVE
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )
    peer_group = models.ForeignKey(
        BGPPeerGroup,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    import_policies = models.ManyToManyField(
        RoutingPolicy,
        blank=True,
        related_name='session_import_policies'
    )
    export_policies = models.ManyToManyField(
        RoutingPolicy,
        blank=True,
        related_name='session_export_policies'
    )

    afi_safi = None  # for future use

    class Meta:
        verbose_name_plural = 'BGP Sessions'
        unique_together = ['device', 'local_address', 'local_as', 'remote_address', 'remote_as']

    def __str__(self):
        return f'{self.device}:{self.name}'

    def get_status_color(self):
        return SessionStatusChoices.colors.get(self.status)

    def get_absolute_url(self):
        return reverse('plugins:netbox_bgp:bgpsession', args=[self.pk])


class RoutingPolicyRule(NetBoxModel):
    routing_policy = models.ForeignKey(
        to=RoutingPolicy,
        on_delete=models.CASCADE,
        related_name='rules'
    )
    index = models.PositiveIntegerField()
    action = models.CharField(
        max_length=30,
        choices=ActionChoices
    )
    description = models.CharField(
        max_length=500,
        blank=True
    )
    match_community = models.ManyToManyField(
        to=Community,
        blank=True,
        related_name='+'
    )
    match_ip = models.ManyToManyField(
        to='ipam.Prefix',
        blank=True,
        related_name='+',
    )
    match_ip_cond = models.JSONField(
        blank=True,
        null=True,
    )
    match_custom = models.JSONField(
        blank=True,
        null=True,
    )
    set_actions = models.JSONField(
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ('routing_policy', 'index')
        unique_together = ('routing_policy', 'index')

    def __str__(self):
        return f'{self.routing_policy}: Rule {self.index}'

    def get_absolute_url(self):
        return reverse('plugins:netbox_bgp:routingpolicyrule', args=[self.pk])

    def get_action_color(self):
        return ActionChoices.colors.get(self.action)      

    def get_ip_conditions(self):
        queryset = Prefix.objects.none()
        if self.match_ip_cond and self.match_ip_cond != {}:
            try:
                queryset = Prefix.objects.filter(**self.match_ip_cond)
            except FieldError:
                pass
        return queryset

    def get_match_custom(self):
        # some kind of ckeck?
        result = {}
        if self.match_custom:
            result = self.match_custom
        return result

    @property
    def match_statements(self):
        result = {}
        # add communities
        result.update(
            {'community': list(self.match_community.all().values_list('value', flat=True))}
        )
        result.update(
            {'ip address': [str(prefix) for prefix in self.match_ip.all().values_list('prefix', flat=True)]}
        )
        matched_ip = self.get_ip_conditions()
        result['ip address'].extend([str(prefix) for prefix in matched_ip.values_list('prefix', flat=True)])
        custom_match = self.get_match_custom()
        # update community from custom
        result['community'].extend(custom_match.get('community', []))
        result['ip address'].extend(custom_match.get('ip address', []))
        # remove empty matches
        result = {k: v for k, v in result.items() if v}
        return result

    @property
    def set_statements(self):
        if self.set_actions:
            return self.set_actions
        return {}
