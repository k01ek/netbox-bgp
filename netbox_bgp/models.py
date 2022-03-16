from django.urls import reverse
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.conf import settings

from taggit.managers import TaggableManager

from utilities.choices import ChoiceSet
from utilities.querysets import RestrictedQuerySet
from netbox.models import ChangeLoggedModel

from netbox.models import CustomFieldsMixin as CustomFieldModel

from extras.models import TaggedItem
from extras.utils import extras_features


class CommunityStatusChoices(ChoiceSet):

    STATUS_ACTIVE = 'active'
    STATUS_RESERVED = 'reserved'
    STATUS_DEPRECATED = 'deprecated'

    CHOICES = (
        (STATUS_ACTIVE, 'Active'),
        (STATUS_RESERVED, 'Reserved'),
        (STATUS_DEPRECATED, 'Deprecated'),
    )

    CSS_CLASSES = {
        STATUS_ACTIVE: 'primary',
        STATUS_RESERVED: 'info',
        STATUS_DEPRECATED: 'danger',
    }


class SessionStatusChoices(ChoiceSet):

    STATUS_OFFLINE = 'offline'
    STATUS_ACTIVE = 'active'
    STATUS_PLANNED = 'planned'
    STATUS_FAILED = 'failed'

    CHOICES = (
        (STATUS_OFFLINE, 'Offline'),
        (STATUS_ACTIVE, 'Active'),
        (STATUS_PLANNED, 'Planned'),
        (STATUS_FAILED, 'Failed'),
    )

    CSS_CLASSES = {
        STATUS_OFFLINE: 'warning',
        STATUS_ACTIVE: 'success',
        STATUS_PLANNED: 'info',
        STATUS_FAILED: 'danger',
    }


@extras_features('custom_fields', 'export_templates', 'webhooks')
class RoutingPolicy(ChangeLoggedModel, CustomFieldModel):
    """
    """
    name = models.CharField(
        max_length=100
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )

    tags = TaggableManager(through=TaggedItem)

    objects = RestrictedQuerySet.as_manager()

    class Meta:
        verbose_name_plural = 'Routing Policies'
        unique_together = ['name', 'description']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('plugins:netbox_bgp:routing_policy', args=[self.pk])


@extras_features('custom_fields', 'export_templates', 'webhooks')
class BGPPeerGroup(ChangeLoggedModel, CustomFieldModel):
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

    tags = TaggableManager(through=TaggedItem)

    objects = RestrictedQuerySet.as_manager()

    class Meta:
        verbose_name_plural = 'Peer Groups'
        unique_together = ['name', 'description']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('plugins:netbox_bgp:peergroup', args=[self.pk])


class BGPBase(ChangeLoggedModel):
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
    tags = TaggableManager(through=TaggedItem)

    objects = RestrictedQuerySet.as_manager()

    class Meta:
        abstract = True


@extras_features('export_templates', 'webhooks')
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

    def get_status_class(self):
        return CommunityStatusChoices.CSS_CLASSES.get(self.status)

    def get_absolute_url(self):
        return reverse('plugins:netbox_bgp:community', args=[self.pk])


@extras_features('custom_fields', 'export_templates', 'webhooks')
class BGPSession(ChangeLoggedModel, CustomFieldModel):
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

    tags = TaggableManager(through=TaggedItem)

    objects = RestrictedQuerySet.as_manager()

    class Meta:
        verbose_name_plural = 'BGP Sessions'
        unique_together = ['device', 'local_address', 'local_as', 'remote_address', 'remote_as']

    def __str__(self):
        return f'{self.device}:{self.name}'

    def get_status_class(self):
        return SessionStatusChoices.CSS_CLASSES.get(self.status)

    def get_absolute_url(self):
        return reverse('plugins:netbox_bgp:session', args=[self.pk])
