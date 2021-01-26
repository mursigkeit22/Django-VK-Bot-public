import os

from django.test import TestCase

from vk.tests.data_for_tests.message_data import input_data

VK_SECRET = os.environ['VK_SECRET']
CONFIRMATION_RESPONSE = os.environ['CONFIRMATION_RESPONSE']

class ViewVKReceiverTests(TestCase): #TODO: simple test case?
    url = '/vkreceiver/'
    peer_id = 2000000005

    def test_vk_secret_wrong(self):

        data = input_data(self.peer_id, '/reg on', 21070693, "12345678910")
        response = self.client.post(self.url, data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'wrong VK secret key')

    def test_vk_secret_right(self):
        data = input_data(self.peer_id, 'some text', 21070693, VK_SECRET)
        response = self.client.post(self.url, data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'ok')

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'it was get')

    def test_confirmation_response(self):
        data = {"type": "confirmation", "group_id": 188881180}
        response = self.client.post(self.url, data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, str.encode(CONFIRMATION_RESPONSE))
