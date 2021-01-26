import os

from django.test import SimpleTestCase
from vk.vkreceiver_event_handler import EventHandler
from vk.tests.data_for_tests.message_data import input_data, OwnerAndBotChatData


VK_SECRET = os.environ['VK_SECRET']


class EventTests(SimpleTestCase):

    def test_vk_secret_wrong(self):
        data = input_data(OwnerAndBotChatData.peer_id, 'just text', OwnerAndBotChatData.owner_id, vk_secret="12345678910")
        event_object = EventHandler(data)
        self.assertNotEqual(VK_SECRET, event_object.vk_secret_key)

    def test_vk_secret_none(self):
        data = input_data(OwnerAndBotChatData.peer_id, 'just text', OwnerAndBotChatData.owner_id, vk_secret=None)
        event_object = EventHandler(data)
        self.assertNotEqual(VK_SECRET, event_object.vk_secret_key)

    def test_vk_secret_right(self):
        data = input_data(OwnerAndBotChatData.peer_id, 'just text', OwnerAndBotChatData.owner_id, vk_secret=VK_SECRET)
        event_object = EventHandler(data)
        self.assertEqual(VK_SECRET, event_object.vk_secret_key)
