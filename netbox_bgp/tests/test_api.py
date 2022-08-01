import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase


from users.models import Token

from tenancy.models import Tenant
from dcim.models import Site, DeviceRole, DeviceType, Manufacturer, Device, Interface
from ipam.models import IPAddress, ASN, RIR

from netbox_bgp.models import Community, BGPPeerGroup, BGPSession


class BaseTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser', is_superuser=True)
        self.token = Token.objects.create(user=self.user)
        # todo change to Client
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.gql_client = Client(HTTP_AUTHORIZATION=f'Token {self.token.key}')


class CommunityTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.base_url_lookup = 'plugins-api:netbox_bgp-api:community'
        self.community1 = Community.objects.create(value='65000:65000', description='test_community')

    def test_list_community(self):
        url = reverse(f'{self.base_url_lookup}-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_get_community(self):
        url = reverse(f'{self.base_url_lookup}-detail', kwargs={'pk': self.community1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['value'], self.community1.value)
        self.assertEqual(response.data['description'], self.community1.description)

    def test_create_community(self):
        url = reverse(f'{self.base_url_lookup}-list')
        data = {'value': '65001:65001', 'description': 'test_community1'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Community.objects.get(pk=response.data['id']).value, '65001:65001')
        self.assertEqual(Community.objects.get(pk=response.data['id']).description, 'test_community1')

    def test_update_community(self):
        pass

    def test_delete_community(self):
        pass

    def test_graphql(self):
        url = reverse('graphql')
        query = 'query community($id: Int!){community(id: $id){value}}'
        response = self.gql_client.post(
            url,
            json.dumps({'query': query, 'variables': {'id': self.community1.pk}}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content)['data']['community']['value'], self.community1.value)

    def test_graphql_list(self):
        url = reverse('graphql')
        query = '{community_list{value}}'
        response = self.gql_client.post(
            url,
            json.dumps({'query': query}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PeerGroupTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.base_url_lookup = 'plugins-api:netbox_bgp-api:peergroup'
        self.peer_group = BGPPeerGroup.objects.create(name='peer_group', description='peer_group_description')

    def test_list_peer_group(self):
        url = reverse(f'{self.base_url_lookup}-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_get_peer_group(self):
        url = reverse(f'{self.base_url_lookup}-detail', kwargs={'pk': self.peer_group.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.peer_group.name)
        self.assertEqual(response.data['description'], self.peer_group.description)

    def test_create_peer_group(self):
        url = reverse(f'{self.base_url_lookup}-list')
        data = {'name': 'test_peer_group', 'description': 'peer_group_desc'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BGPPeerGroup.objects.get(pk=response.data['id']).name, 'test_peer_group')
        self.assertEqual(BGPPeerGroup.objects.get(pk=response.data['id']).description, 'peer_group_desc')

    def test_update_peer_group(self):
        pass

    def test_delete_peer_group(self):
        pass

    def test_graphql(self):
        url = reverse('graphql')
        query = 'query peer_group($id: Int!){peer_group(id: $id){name}}'
        response = self.gql_client.post(
            url,
            json.dumps({'query': query, 'variables': {'id': self.peer_group.pk}}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content)['data']['peer_group']['name'], self.peer_group.name)

    def test_graphql_list(self):
        url = reverse('graphql')
        query = '{peer_group_list{name}}'
        response = self.gql_client.post(
            url,
            json.dumps({'query': query}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SessionTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.base_url_lookup = 'plugins-api:netbox_bgp-api:session'
        site = Site.objects.create(name='test', slug='test')
        manufacturer = Manufacturer.objects.create(name='Juniper', slug='juniper')
        device_role = DeviceRole.objects.create(name='Firewall', slug='firewall')
        device_type = DeviceType.objects.create(slug='srx3600', model='SRX3600', manufacturer=manufacturer)
        self.device = Device.objects.create(
            device_type=device_type, name='device1', device_role=device_role, site=site,
        )
        intf = Interface.objects.create(name='test_intf', device=self.device)
        local_ip = IPAddress.objects.create(address='1.1.1.1/32')
        remote_ip = IPAddress.objects.create(address='2.2.2.2/32')
        self.local_ip = IPAddress.objects.create(address='3.3.3.3/32')
        self.remote_ip = IPAddress.objects.create(address='4.4.4.4/32')
        intf.ip_addresses.add(local_ip)
        self.device.save()
        self.rir = RIR.objects.create(name="rir")
        self.local_as = ASN.objects.create(asn=65000, rir=self.rir, description='local_as')
        self.remote_as = ASN.objects.create(asn=65001, rir=self.rir, description='remote_as')
        local_as = ASN.objects.create(asn=65002, rir=self.rir, description='local_as')
        remote_as = ASN.objects.create(asn=65003, rir=self.rir, description='remote_as')
        self.peer_group = BGPPeerGroup.objects.create(name='peer_group', description='peer_group_description')
        self.session = BGPSession.objects.create(
            name='session',
            description='session_descr',
            local_as=local_as,
            remote_as=remote_as,
            local_address=local_ip,
            remote_address=remote_ip,
            status='active',
            peer_group=self.peer_group
        )

    def test_list_session(self):
        url = reverse(f'{self.base_url_lookup}-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_get_session(self):
        url = reverse(f'{self.base_url_lookup}-detail', kwargs={'pk': self.session.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.session.name)
        self.assertEqual(response.data['description'], self.session.description)
        self.assertEqual(response.data['local_as']['asn'], self.session.local_as.asn)
        self.assertEqual(response.data['remote_as']['asn'], self.session.remote_as.asn)
        self.assertEqual(response.data['local_address']['address'], self.session.local_address.address)
        self.assertEqual(response.data['remote_address']['address'], self.session.remote_address.address)
        self.assertEqual(response.data['status']['value'], self.session.status)
        self.assertEqual(response.data['peer_group']['name'], self.session.peer_group.name)
        self.assertEqual(response.data['peer_group']['description'], self.session.peer_group.description)

    def test_create_session(self):
        url = reverse(f'{self.base_url_lookup}-list')
        data = {
            'name': 'test_session',
            'description': 'session_descr',
            'local_as': self.local_as.pk,
            'remote_as': self.remote_as.pk,
            'local_address': self.local_ip.pk,
            'remote_address': self.remote_ip.pk,
            'status': 'active',
            'device': self.device.pk,
            'peer_group': self.peer_group.pk

        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BGPSession.objects.get(pk=response.data['id']).name, 'test_session')
        self.assertEqual(BGPSession.objects.get(pk=response.data['id']).description, 'session_descr')

    def test_session_no_device(self):
        url = reverse(f'{self.base_url_lookup}-list')
        data = {
            'name': 'test_session',
            'description': 'session_descr',
            'local_as': self.local_as.pk,
            'remote_as': self.remote_as.pk,
            'local_address': self.local_ip.pk,
            'remote_address': self.remote_ip.pk,
            'status': 'active',
            'peer_group': self.peer_group.pk

        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BGPSession.objects.get(pk=response.data['id']).name, 'test_session')
        self.assertEqual(BGPSession.objects.get(pk=response.data['id']).description, 'session_descr')

    def test_graphql(self):
        url = reverse('graphql')
        query = 'query bgp_session($id: Int!){bgp_session(id: $id){name}}'
        response = self.gql_client.post(
            url,
            json.dumps({'query': query, 'variables': {'id': self.session.pk}}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content)['data']['bgp_session']['name'], self.session.name)

    def test_graphql_list(self):
        url = reverse('graphql')
        query = '{bgp_session_list{name}}'
        response = self.gql_client.post(
            url,
            json.dumps({'query': query}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)