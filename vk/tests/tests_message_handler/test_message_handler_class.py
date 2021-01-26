from django.test import SimpleTestCase, TestCase

from vk import helpers, models
from vk.tests.data_for_tests.event_dicts import event_dict_simple_message, event_dict_chat_title_update_message
from vk.tests.data_for_tests.message_data import OwnerAndBotChatData
from vk.tests.data_for_tests.vk_api_dicts import *
from vk.vkreceiver_message_handler import MessageHandler


class MessageHandlerTest(SimpleTestCase):


    def test_is_service_message_false(self):
        message_handler_object = MessageHandler(event_dict_simple_message)
        self.assertIsNotNone(message_handler_object.peer_id)

        self.assertFalse(message_handler_object.service_message)

    def test_is_service_message_true(self):
        message_handler_object = MessageHandler(event_dict_chat_title_update_message)
        self.assertIsNotNone(message_handler_object.action_type)
        self.assertTrue(message_handler_object.service_message)

    def test_is_allowed_to_write_to_chat_true(self):
        message_handler_object = MessageHandler(event_dict_simple_message)
        message_handler_object.conversation_dict = helpers.parse_vk_object(getConversationsById_chat_good_response)
        message_handler_object.conversation_type = message_handler_object.conversation_dict.get(
            'response__items__peer__type', None)
        self.assertTrue(message_handler_object.is_admin_or_userchat())

    def test_is_allowed_to_write_to_chat_false(self):
        message_handler_object = MessageHandler(event_dict_simple_message)
        message_handler_object.conversation_dict = helpers.parse_vk_object(getConversationsById_chat_bot_not_admin)
        message_handler_object.conversation_type = message_handler_object.conversation_dict.get(
            'response__items__peer__type', None)
        self.assertFalse(message_handler_object.is_admin_or_userchat())

    def test_is_allowed_to_write_to_user_true(self):
        message_handler_object = MessageHandler(event_dict_simple_message)
        message_handler_object.conversation_dict = helpers.parse_vk_object(getConversationsById_user_good_response)
        message_handler_object.conversation_type = message_handler_object.conversation_dict.get(
            'response__items__peer__type', None)
        self.assertTrue(message_handler_object.is_admin_or_userchat())




