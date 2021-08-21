from typing import Union, Tuple, Optional

from django.contrib.auth.models import User

from botsite.models import UserProfile
from vk import models
from vk.bot_answer import BotAnswer
from vk.input_message import InputMessage
from vk.tests.data_for_tests.event_dicts import event_dict_simple_message
from vk.tests.data_for_tests.message_data import OwnerAndBotChatData, input_data
from vk.text_parser import TextParser
from vk.vkreceiver_event_handler import EventHandler
from vk.vkreceiver_message_handler import MessageHandler
from web_vk.constants import test_personal_token


class PipelinesAndSetUps:

    @classmethod
    def basic_setup(cls, is_registered=True):
        cls.setup_chat(is_registered)
        cls.create_settings_tables()

    @classmethod
    def create_settings_tables(cls):
        cls.setup_newpost()
        cls.setup_kick()
        cls.setup_randompost()

    @classmethod
    def setup_chat(cls, is_registered,
                   interval_mode=False, interval=None,
                   messages_till_endpoint=None, smart_mode=False,
                   ):
        cls.chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id,
            conversation_is_registered=is_registered,
            interval_mode=interval_mode, interval=interval,
            messages_till_endpoint=messages_till_endpoint, smart_mode=smart_mode,
        )

    @classmethod
    def setup_newpost(cls,
                      mode: bool = False, group_link: str = '', group_id: Optional[int] = None, ):
        cls.newpost_setting_object = models.NewPostSetting.objects.create(chat_id=cls.chat_db_object,
                                                                          newpost_mode=mode,
                                                                          newpost_group_link=group_link,
                                                                          newpost_group_id=group_id)

    @classmethod
    def setup_kick(cls,
                   mode: bool = False, group_link: str = '', group_id: Optional[int] = None, ):
        cls.kick_setting_object = models.KickNonMembersSetting.objects.create(chat_id=cls.chat_db_object,
                                                                              kick_nonmembers_mode=mode,
                                                                              kick_nonmembers_group_link=group_link,
                                                                              kick_nonmembers_group_id=group_id)

    @classmethod
    def setup_randompost(cls,
                         mode: bool = False, group_link: str = '', group_id: Optional[int] = None, ):
        cls.randompost_setting_object = models.RandomPostSetting.objects.create(chat_id=cls.chat_db_object,
                                                                                random_post_mode=mode,
                                                                                random_post_group_link=group_link,
                                                                                random_post_group_id=group_id)

    def core_pipeline(self, peer_id, from_id, input_text, event_code, event_description=None, bot_response=None, ):
        """ We create expected_answer before actual processing, 'cause initializing InputMessage object
        we call 'getConversationsById' method to get conversation_dict, and there are such fields as
        response__items__last_message_id
        and
        response__items__in_read
        in that dict
        which will be different after event_object.process(), 'cause bot sends a message in that process."""

        input_message_object = self.create_input_message_instance(input_text, peer_id=peer_id, from_id=from_id)
        expected_answer = BotAnswer(event_code, input_message_object, event_description=event_description,
                                    bot_response=bot_response)
        # print("EXPECTED_ANSWER", expected_answer)

        returned_answer = self.event_object.process()
        # print("RETURNED_ANSWER", returned_answer)
        self.assertEqual(expected_answer, returned_answer)

    def pipeline_part_dict(self, peer_id, from_id, input_text, event_code,
                           expected_bot_response_dict, event_description=None,):
        """ Here we compare only part of bot_response dictionary.
         First we create expected_answer without bot_response,
         then we compare only those bot_response dictionary values which we passed in expected_bot_response_dict."""
        input_message_object = self.create_input_message_instance(input_text, peer_id=peer_id, from_id=from_id)

        expected_answer = BotAnswer(event_code, input_message_object, event_description=event_description)
        returned_answer = self.event_object.process()
        returned_bot_response_dict = returned_answer.bot_response
        for key, item in expected_bot_response_dict.items():
            self.assertEqual(item, returned_bot_response_dict.get(key))
        self.assertEqual(expected_answer.event_code, returned_answer.event_code)
        self.assertEqual(expected_answer.input_message, returned_answer.input_message)
        self.assertEqual(expected_answer.event_description, returned_answer.event_description)

    def pipeline_chat_from_owner(self, option: str, event_code, event_description=None, bot_response=None, ):
        text = f"{self.command} {option}"
        self.core_pipeline(OwnerAndBotChatData.peer_id, OwnerAndBotChatData.owner_id, text, event_code,
                           event_description,
                           bot_response, )

    def pipeline_user(self, option: str, event_code, event_description=None, bot_response=None, ):
        text = f"{self.command} {OwnerAndBotChatData.peer_id} {option}"
        self.core_pipeline(OwnerAndBotChatData.owner_id, OwnerAndBotChatData.owner_id, text, event_code,
                           event_description,
                           bot_response, )

    def pipeline_chat_not_owner(self, option: str, event_code, event_description=None, bot_response=None, ):
        text = f"{self.command} {option}"
        self.core_pipeline(OwnerAndBotChatData.peer_id, OwnerAndBotChatData.not_owner_id, text, event_code,
                           event_description,
                           bot_response, )

    @classmethod
    def setup_with_user_profile(cls):
        cls.setup_with_setting_object()
        cls.set_user_profile(test_personal_token)

    @classmethod
    def setup_with_setting_object(cls):
        cls.basic_setup()
        cls.setting_object = cls.setting_model.objects.get(chat_id=cls.chat_db_object)

        for key, item in cls.field_dict.items():
            setattr(cls.setting_object, key, item)
        cls.setting_object.save()

    @classmethod
    def setup_command_handler_object(cls):
        cls.setup_with_setting_object()
        cls.input_message_object = cls().create_input_message_instance("just_a_message", )
        cls.handler_object = cls.command_handler(["just_a_message"], cls.input_message_object, cls.chat_db_object)

    def create_input_message_instance(self, input_text, peer_id=OwnerAndBotChatData.peer_id,
                                      from_id=OwnerAndBotChatData.owner_id):
        data = input_data(peer_id, input_text, from_id)
        self.event_object = EventHandler(data)
        input_message_object = InputMessage(self.event_object.event_dict)
        return input_message_object

    @staticmethod
    def set_user_profile(token):
        user = User.objects.create_user(OwnerAndBotChatData.screen_name, first_name=OwnerAndBotChatData.first_name,
                                        last_name=OwnerAndBotChatData.last_name)
        profile = UserProfile(user=user, vk_id=OwnerAndBotChatData.owner_id, vk_token=token)
        profile.save()
