from unittest import mock

from django.test import TestCase

from vk.helpers import registration
from vk.tests.data_for_tests.message_data import OwnerAndBotChatData
from vk.tests.shared.pipelines_and_setups import PipelinesAndSetUps
from vk.tests.tests_mockAPIcalls import mock_shared


class RegistrationCommandTest(TestCase, PipelinesAndSetUps):
    command = registration

    def setUp(self):
        self.basic_setup()

    @mock.patch('vk.helpers.make_request_vk')
    def test_info(self, mock_make_request_vk, side_effect=mock_shared.side_effect_make_request):
        mock_make_request_vk.side_effect = side_effect
        self.pipeline_chat_from_owner("info", "REGISTRATION_INFO",
                                      bot_response=f'ID вашей беседы {OwnerAndBotChatData.peer_id}')
