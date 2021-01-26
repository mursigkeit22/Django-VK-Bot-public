from typing import Union, Tuple

from django.contrib.auth.models import User

from botsite.models import UserProfile
from vk import models
from vk.tests.data_for_tests.event_dicts import event_dict_simple_message
from vk.tests.data_for_tests.message_data import OwnerAndBotChatData, input_data
from vk.text_parser import TextParser
from vk.vkreceiver_event_handler import EventHandler
from vk.vkreceiver_message_handler import MessageHandler
from web_vk.constants import test_personal_token


class PipelinesAndSetUps:

    @classmethod
    def setup_with_user_profile(cls):
        cls.setup()
        cls.set_user_profile(test_personal_token)

    @classmethod
    def setup_class_with_user_profile(cls):
        cls.setup()
        cls.set_user_profile(test_personal_token)
        message_object = MessageHandler(event_dict_simple_message)
        text_instance = TextParser(message_object)
        cls.handler_object = cls.command_handler(text_instance, cls.chat_db_object)




    @classmethod
    def setup(cls):
        cls.chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True)
        cls.setting_object = cls.setting_model.objects.create(chat_id=cls.chat_db_object)
        for key, item in cls.field_dict.items():
            setattr(cls.setting_object, key, item)
        cls.setting_object.save()

    @classmethod
    def setup_class(cls):
        cls.setup()
        message_object = MessageHandler(event_dict_simple_message)
        text_instance = TextParser(message_object)
        cls.handler_object = cls.command_handler(text_instance, cls.chat_db_object)

    def pipeline_class(self, option: Union[str, Tuple[str, int]], expected_answer: str):
        self.handler_object.option = option
        returned_answer = self.handler_object.command()
        self.assertEqual(returned_answer, expected_answer)

    def pipeline_chat_from_owner(self, option: str, expected_answer: str):
        text = f"{self.command} {option}"
        data = input_data(OwnerAndBotChatData.peer_id, text, OwnerAndBotChatData.owner_id)
        returned_answer = EventHandler(data).process()
        self.assertEqual(returned_answer, expected_answer)

    def pipeline_user(self, option: str, expected_answer: str):
        text = f"{self.command} {OwnerAndBotChatData.peer_id} {option}"
        data = input_data(OwnerAndBotChatData.owner_id, text, OwnerAndBotChatData.owner_id)
        returned_answer = EventHandler(data).process()
        self.assertEqual(returned_answer, expected_answer)

    def pipeline_chat_not_owner(self, option: str, expected_answer: str):
        text = f"{self.command} {option}"
        data = input_data(OwnerAndBotChatData.peer_id, text, OwnerAndBotChatData.not_owner_id)
        returned_answer = EventHandler(data).process()
        self.assertEqual(returned_answer, expected_answer)

    @staticmethod
    def set_user_profile(token):
        user = User.objects.create_user(OwnerAndBotChatData.screen_name, first_name=OwnerAndBotChatData.first_name,
                                        last_name=OwnerAndBotChatData.last_name)
        profile = UserProfile(user=user, vk_id=OwnerAndBotChatData.owner_id, vk_token=token)
        profile.save()
