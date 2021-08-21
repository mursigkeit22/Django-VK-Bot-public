from typing import Optional

from django.test import TestCase

import vk.tests.data_for_tests.group_links as links
from vk import models
from vk.helpers import random_post, option_on, option_info, option_group, option_delete
from vk.tests.data_for_tests.message_data import OwnerAndBotChatData
from vk.tests.shared.pipelines_and_setups import PipelinesAndSetUps
from vk.tests.shared.shared_tests.common_group_tests import NOGROUPTestMixin, THEREISGROUPOffTestMixin, \
    THEREISGROUPOnTestMixin, TurnOffDeleteChangeONMixin, TurnOnDeleteChangeOFFMixin, AddGroupMixin, \
    NoProfileModeOFFMixin, ExpiredTokenModeOFFMixin
from vk.tests.shared.shared_tests.user_specific_commands_test import UserSpecificCommandsMixinTest
from vk.usertext import random_post_dict, common_dict
from web_vk.constants import test_personal_expired_token


class Shared:
    command = random_post
    setting_model = models.RandomPostSetting
    command_code = "RANDOM_POST"
    text_dict = random_post_dict

    def check_db(self, mode: bool, grouplink: str, groupid: Optional[int]):
        self.setting_object.refresh_from_db()
        self.assertEqual(self.setting_object.random_post_mode, mode)
        self.assertEqual(self.setting_object.random_post_group_link, grouplink)
        self.assertEqual(self.setting_object.random_post_group_id, groupid)


class UserSpecificRandomPostTest(TestCase, Shared, UserSpecificCommandsMixinTest):  # 6
    pass


class RandomPostNOGROUPTest(TestCase, Shared, NOGROUPTestMixin):  # 5 + 2
    field_dict = dict()

    @classmethod
    def setUpTestData(cls):
        super().setup_with_user_profile()

    def test_post_option(self):
        bot_response = f"Чтобы включить команду {self.command}, воспользуйтесь командой {self.command} {option_on}."
        self.pipeline_chat_from_owner("", "PREREQUISITES_ERROR", bot_response=bot_response)

    def test_chat_not_owner(self):
        self.pipeline_chat_not_owner(option_info, 'NOT_OWNER',
                                     event_description="random_post_mode is false. Nothing will be sent.")


class RandomPostTHEREISGROUPOffTest(TestCase, Shared, THEREISGROUPOffTestMixin):  # 2+1

    field_dict = {"random_post_group_link": links.normal_group1,
                  "random_post_group_id": links.normal_group1ID, "random_post_mode": False}

    @classmethod
    def setUpTestData(cls):
        super().setup_with_user_profile()

    def test_chat_not_owner(self):
        self.pipeline_chat_not_owner(option_info, 'NOT_OWNER',
                                     event_description="random_post_mode is false. Nothing will be sent.")


class RandomPostTHEREISGROUPOnTest(TestCase, Shared, THEREISGROUPOnTestMixin):  # 3 + 1

    field_dict = {"random_post_group_link": links.normal_group1,
                  "random_post_group_id": links.normal_group1ID, "random_post_mode": True}

    @classmethod
    def setUpTestData(cls):
        super().setup_with_user_profile()

    def test_post(self):
        self.pipeline_part_dict(OwnerAndBotChatData.owner_id, OwnerAndBotChatData.owner_id,
                                f"{self.command} {OwnerAndBotChatData.peer_id}",
                                "RANDOM_POST_SENT", {"peer_id": OwnerAndBotChatData.peer_id})
        self.pipeline_part_dict(OwnerAndBotChatData.peer_id, OwnerAndBotChatData.owner_id, self.command,
                                "RANDOM_POST_SENT", {"peer_id": OwnerAndBotChatData.peer_id},
                                )

    def test_chat_not_owner(self):
        bot_response = f'Для вас доступна команда {self.command} без дополнительных опций.'
        self.pipeline_chat_not_owner(option_info, 'NOT_OWNER', bot_response=bot_response)


class RandomPostTurnOffDeleteChangeONTest(TestCase, Shared, TurnOffDeleteChangeONMixin):  # 7
    field_dict = {"random_post_group_link": links.normal_group1,
                  "random_post_group_id": links.normal_group1ID, "random_post_mode": True}

    def setUp(self):
        super().setup_with_user_profile()

    def test_chat_not_owner(self):
        bot_response = f'Для вас доступна команда {self.command} без дополнительных опций.'
        self.pipeline_chat_not_owner(f"{option_group} {option_delete}", 'NOT_OWNER', bot_response=bot_response)


class RandomPostTurnOnDeleteChangeOFFTest(TestCase, Shared, TurnOnDeleteChangeOFFMixin):  # 6 + 2
    field_dict = {"random_post_group_link": links.normal_group1,
                  "random_post_group_id": links.normal_group1ID, "random_post_mode": False}

    def setUp(self):
        super().setup_with_user_profile()

    def test_post(self):
        bot_response = f"Чтобы включить команду {self.command}, воспользуйтесь командой {self.command} on."
        self.pipeline_user("", "PREREQUISITES_ERROR", bot_response=bot_response)
        self.pipeline_chat_from_owner("", "PREREQUISITES_ERROR", bot_response=bot_response)

    def test_post_not_chat_owner(self):
        self.pipeline_chat_not_owner("", 'NOT_OWNER',
                                     event_description="random_post_mode is false. Nothing will be sent.")


class RandomPostAddGroup(TestCase, Shared, AddGroupMixin):  # 4
    field_dict = dict()

    def setUp(self):
        super().setup_with_user_profile()


class RandomPostNoProfileModeOFFTest(TestCase, Shared, NoProfileModeOFFMixin):  # 3
    field_dict = {"random_post_group_link": links.normal_group1,
                  "random_post_group_id": links.normal_group1ID, "random_post_mode": False}

    @classmethod
    def setUpTestData(cls):
        super().setup_with_setting_object()

    def test_on_not_chat_owner(self):
        self.pipeline_chat_not_owner(option_on, 'NOT_OWNER',
                                     event_description="random_post_mode is false. Nothing will be sent.")


class RandomPostExpiredTokenModeOFFTest(TestCase, Shared, ExpiredTokenModeOFFMixin):  # 3
    field_dict = {"random_post_group_link": links.normal_group1,
                  "random_post_group_id": links.normal_group1ID, "random_post_mode": False}

    @classmethod
    def setUpTestData(cls):
        super().setup_with_setting_object()
        super().set_user_profile(test_personal_expired_token)

    def test_on_not_chat_owner(self):
        self.pipeline_chat_not_owner(option_on, 'NOT_OWNER',
                                     event_description="random_post_mode is false. Nothing will be sent.")


class RandomPostExpiredTokenModeONTest(TestCase, Shared, PipelinesAndSetUps):  # 3
    field_dict = {"random_post_group_link": links.normal_group1,
                  "random_post_group_id": links.normal_group1ID, "random_post_mode": True}
    bot_response = {
        "message": common_dict["refresh_token"].substitute(command=Shared.command),
        "peer_id": OwnerAndBotChatData.owner_id}
    event_description = "An error message is sent to chat owner."

    @classmethod
    def setUpTestData(cls):
        super().setup_with_setting_object()
        super().set_user_profile(test_personal_expired_token)

    def test_on_group_user(self):
        self.pipeline_user("", "USER_PROFILE_ERROR", bot_response=self.bot_response,
                           event_description=self.event_description)

    def test_on_group_chat(self):  # message is sent to chat owner (not to the chat)
        self.pipeline_chat_from_owner("", "USER_PROFILE_ERROR", bot_response=self.bot_response,
                                      event_description=self.event_description)

    def test_on_not_chat_owner(self):  # message is sent to chat owner (not to the user who called '/post' command)
        self.pipeline_chat_not_owner("", "USER_PROFILE_ERROR",
                                     bot_response=self.bot_response, event_description=self.event_description)
