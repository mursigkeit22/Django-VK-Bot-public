from typing import Optional

from django.test import TestCase

from vk import models
from vk.helpers import newpost, option_group, option_delete, option_on
from vk.usertext import newpost_dict
from web_vk.constants import test_personal_expired_token, LOGIN_LINK
from vk.tests.shared.shared_tests.common_group_tests import NOGROUPTestMixin, THEREISGROUPOffTestMixin, \
    THEREISGROUPOnTestMixin, TurnOffDeleteChangeONMixin, TurnOnDeleteChangeOFFMixin, AddGroupMixin, \
    NoProfileModeOFFMixin, ExpiredTokenModeOFFMixin
from vk.tests.shared.shared_tests.user_specific_commands_test import UserSpecificCommandsMixinTest

import vk.tests.data_for_tests.group_links as links


class Shared:
    command = newpost
    setting_model = models.NewPostSetting
    command_code = "NEWPOST"
    text_dict = newpost_dict

    def check_db(self, mode: bool, grouplink: str, groupid: Optional[int]):
        self.setting_object.refresh_from_db()
        self.assertEqual(self.setting_object.newpost_mode, mode)
        self.assertEqual(self.setting_object.newpost_group_link, grouplink)
        self.assertEqual(self.setting_object.newpost_group_id, groupid)


class UserSpecificNewPostTest(TestCase, Shared, UserSpecificCommandsMixinTest):  # 6
    pass


class NewPostNOGROUPTest(TestCase, Shared, NOGROUPTestMixin):  # 6 + 1
    field_dict = dict()

    @classmethod
    def setUpTestData(cls):
        super().setup_with_user_profile()

    def test_without_option(self):
        bot_response = "Пожалуйста, уточните опцию."
        self.pipeline_chat_from_owner("", 'ABSENT_OPTION', bot_response=bot_response)


class NewPostTHEREISGROUPOffTest(TestCase, Shared, THEREISGROUPOffTestMixin):
    field_dict = {"newpost_group_link": links.normal_group1,
                  "newpost_group_id": links.normal_group1ID, "newpost_mode": False}

    @classmethod
    def setUpTestData(cls):
        super().setup_with_setting_object()


class NewPostTHEREISGROUPOnTest(TestCase, Shared, THEREISGROUPOnTestMixin):
    field_dict = {"newpost_group_link": links.normal_group1,
                  "newpost_group_id": links.normal_group1ID, "newpost_mode": True}

    @classmethod
    def setUpTestData(cls):
        super().setup_with_user_profile()


class NewPostTurnOffDeleteChangeONTest(TestCase, Shared, TurnOffDeleteChangeONMixin):  # 7
    field_dict = {"newpost_group_link": links.normal_group1,
                  "newpost_group_id": links.normal_group1ID, "newpost_mode": True}

    def setUp(self):
        super().setup_with_user_profile()


class NewPostTurnOnDeleteChangeOFFTest(TestCase, Shared, TurnOnDeleteChangeOFFMixin):  # 6
    field_dict = {"newpost_group_link": links.normal_group1,
                  "newpost_group_id": links.normal_group1ID, "newpost_mode": False}

    def setUp(self):
        super().setup_with_user_profile()


class NewPostAddGroup(TestCase, Shared, AddGroupMixin):
    field_dict = dict()

    def setUp(self):
        super().setup_with_user_profile()


class NewPostNoProfileModeOFFTest(TestCase, Shared, NoProfileModeOFFMixin):  # 3
    field_dict = {"newpost_group_link": links.normal_group1,
                  "newpost_group_id": links.normal_group1ID, "newpost_mode": False}

    def setUp(self):
        super().setup_with_setting_object()

    def test_on_not_chat_owner(self):
        bot_response = f'Только владелец беседы может использовать команду {self.command}.'
        self.pipeline_chat_not_owner(option_on, "NOT_OWNER", bot_response=bot_response)


class NewPostExpiredTokenModeOFFTest(TestCase, Shared, ExpiredTokenModeOFFMixin):  # 3
    field_dict = {"newpost_group_link": links.normal_group1,
                  "newpost_group_id": links.normal_group1ID, "newpost_mode": False}

    def setUp(self):
        super().setup_with_setting_object()
        super().set_user_profile(test_personal_expired_token)

    def test_on_not_chat_owner(self):
        bot_response = f'Только владелец беседы может использовать команду {self.command}.'
        self.pipeline_chat_not_owner(option_on, "NOT_OWNER", bot_response=bot_response)
