from unittest import mock
from django.test import TestCase

import vk.models as models
from vk.tests.data_for_tests.message_data import OwnerAndBotChatData, input_data
from vk.vkreceiver_event_handler import EventHandler


def side_effect(plain_text):
    return plain_text


class RegistrationCommandTest(TestCase):

    def setUp(self):
        models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True)

    @mock.patch('vk.command_handler.CommandHandler.send_message')
    def test_info(self, mock_send_message, side_effect=side_effect):
        mock_send_message.side_effect = side_effect
        data = input_data(OwnerAndBotChatData.peer_id, '/reg info', OwnerAndBotChatData.owner_id)
        answer = EventHandler(data).process()
        expected_answer = f'ID вашей беседы {OwnerAndBotChatData.peer_id}'
        self.assertEqual(answer, expected_answer)
