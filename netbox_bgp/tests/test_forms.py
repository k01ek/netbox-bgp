from http import HTTPStatus

from django.test import TestCase

from netbox_bgp.forms import CommunityForm


class TestCommunityFormCase(TestCase):
    def test_asn_invalid_letters(self):
        form = CommunityForm(
            data={
                'value': 'dsad',
                'status': 'active'
            }
        )
        self.assertEqual(
            form.errors['value'], ['Enter a valid value.']
        )

    def test_community_valid(self):
        form = CommunityForm(
            data={
                'value': '1234:5678',
                'status': 'active'
            }
        )
        self.assertEqual(
            form.errors.get('value'), None
        )
