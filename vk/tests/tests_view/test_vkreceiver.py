from django.conf import settings
from django.test import TestCase, SimpleTestCase

from vk.tests.data_for_tests.message_data import input_data, OwnerAndBotChatData
from web_vk.constants import BOT_GROUPID, CONFIRMATION_RESPONSE, VK_SECRET


class ViewVKReceiverTests(SimpleTestCase):
    url = '/vkreceiver/'
    peer_id = OwnerAndBotChatData.peer_id
    owner_id = OwnerAndBotChatData.owner_id

    def test_vk_secret_wrong(self):
        data = input_data(self.peer_id, '/reg on', self.owner_id, "12345678910")
        response = self.client.post(self.url, data, content_type="application/json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.content, b'AUTHENTICATION ERROR')

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'it was get')

    def test_confirmation_response(self):
        data = {"type": "confirmation", "group_id": BOT_GROUPID}
        response = self.client.post(self.url, data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, str.encode(CONFIRMATION_RESPONSE))


# TODO:create separate tests for celery
class ViewVKReceiverFullTests(TestCase):  # doesn't work locally 'cause of celery and rabbit
    url = '/vkreceiver/'
    peer_id = OwnerAndBotChatData.peer_id
    owner_id = OwnerAndBotChatData.owner_id

    def test_vk_secret_right(self):
        try:
            celery_check = settings.CELERY_BROKER_URL
            data = input_data(self.peer_id, 'some text', self.owner_id, VK_SECRET)
            response = self.client.post(self.url, data, content_type="application/json")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content, b'ok')
        except AttributeError:
            pass
