from typing import Optional

from django.test import TestCase

from vk import models
from vk.helpers import random_post, PersonalTokenException
from vk.tests.data_for_tests.message_data import OwnerAndBotChatData
from vk.tests.shared.pipelines_and_setups import PipelinesAndSetUps
from web_vk.constants import test_personal_expired_token, LOGIN_LINK
from vk.tests.shared.shared_tests.common_group_tests import NOGROUPTestMixin, THEREISGROUPOffTestMixin, \
    THEREISGROUPOnTestMixin
from vk.tests.shared.shared_tests.user_specific_commands_test import UserSpecificCommandsMixinTest
import vk.tests.data_for_tests.group_links as links


# TODO: сделать остальные миксины


class Shared:
    command = f"{random_post}"
    setting_model = models.RandomPostSetting

    def check_db(self, mode: bool, grouplink: str, groupid: Optional[int]):
        self.setting_object.refresh_from_db()
        self.assertEqual(self.setting_object.random_post_mode, mode)
        self.assertEqual(self.setting_object.random_post_group_link, grouplink)
        self.assertEqual(self.setting_object.random_post_group_id, groupid)


class UserSpecificRandomPostTest(TestCase, Shared, UserSpecificCommandsMixinTest):  # 6
    pass


class RandomPostNOGROUPTest(TestCase, Shared, NOGROUPTestMixin):  # 6 + 1
    field_dict = dict()

    @classmethod
    def setUpTestData(cls):
        super().setup_with_user_profile()

    def test_post_option(self):
        expected_answer = f"Чтобы включить команду {self.command}, воспользуйтесь командой {self.command} on."
        self.pipeline_chat_from_owner("", expected_answer)

    def test_chat_not_owner(self):
        expected_answer = f'Для вас доступна команда {self.command} без дополнительных опций.'
        self.pipeline_chat_not_owner("info", expected_answer)


class RandomPostTHEREISGROUPOffTest(TestCase, Shared, THEREISGROUPOffTestMixin):  # 3

    field_dict = {"random_post_group_link": links.normal_group1,
                  "random_post_group_id": links.normal_group1ID, "random_post_mode": False}

    @classmethod
    def setUpTestData(cls):
        super().setup_with_user_profile()

    def test_chat_not_owner(self):
        expected_answer = 'Для вас доступна команда /post без дополнительных опций.'
        self.pipeline_chat_not_owner("off", expected_answer)


class RandomPostTHEREISGROUPOnTest(TestCase, Shared, THEREISGROUPOnTestMixin):  # 3 + 1

    field_dict = {"random_post_group_link": links.normal_group1,
                  "random_post_group_id": links.normal_group1ID, "random_post_mode": True}

    @classmethod
    def setUpTestData(cls):
        super().setup_with_user_profile()

    def test_post(self):
        expected_answer = "random post is sent."
        self.pipeline_user("", expected_answer)
        self.pipeline_chat_from_owner("", expected_answer)

    def test_chat_not_owner(self):
        expected_answer = f'Для вас доступна команда {self.command} без дополнительных опций.'
        self.pipeline_chat_not_owner("on", expected_answer)


class RandomPostTurnOffDeleteChangeONTest(TestCase, Shared, PipelinesAndSetUps):  # 7
    field_dict = {"random_post_group_link": links.normal_group1,
                  "random_post_group_id": links.normal_group1ID, "random_post_mode": True}

    def setUp(self):
        super().setup_with_user_profile()

    def test_off_chat(self):
        expected_answer = f'Команда {self.command} выключена.'
        self.pipeline_chat_from_owner("off", expected_answer)
        self.check_db(False, links.normal_group1, links.normal_group1ID)

    def test_off_user(self):
        expected_answer = f'Команда {self.command} выключена.'
        self.pipeline_user("off", expected_answer)
        self.check_db(False, links.normal_group1, links.normal_group1ID)

    def test_delete_chat(self):
        expected_answer = f'Группа для команды {self.command} удалена из настроек. Команда {self.command} выключена.'
        self.pipeline_chat_from_owner("group delete", expected_answer)
        self.check_db(False, "", None)

    def test_delete_user(self):
        expected_answer = f'Группа для команды {self.command} удалена из настроек. Команда {self.command} выключена.'
        self.pipeline_user("group delete", expected_answer)
        self.check_db(False, "", None)

    def test_change_group_chat(self):
        expected_answer = f'Группа {links.normal_group2} сохранена в настройках. Команда {self.command} включена.'
        self.pipeline_chat_from_owner(f"group {links.normal_group2}", expected_answer)
        self.check_db(True, links.normal_group2, links.normal_group2ID)

    def test_change_group_user(self):
        expected_answer = f'Группа {links.normal_group2} сохранена в настройках. Команда {self.command} включена.'
        self.pipeline_user(f"group {links.normal_group2}", expected_answer)
        self.check_db(True, links.normal_group2, links.normal_group2ID)

    def test_chat_not_owner(self):
        expected_answer = f'Для вас доступна команда {self.command} без дополнительных опций.'
        self.pipeline_chat_not_owner("group delete", expected_answer)


class RandomPostTurnOnDeleteChangeOFFTest(TestCase, Shared, PipelinesAndSetUps):  # 6 + 2
    field_dict = {"random_post_group_link": links.normal_group1,
                  "random_post_group_id": links.normal_group1ID, "random_post_mode": False}

    def setUp(self):
        super().setup_with_user_profile()

    def test_change_group_chat(self):
        expected_answer = f'Группа {links.normal_group2} сохранена в настройках.' \
                          f' Чтобы включить команду {self.command} , воспользуйтесь командой {self.command} on'
        self.pipeline_chat_from_owner(f"group {links.normal_group2}", expected_answer)
        self.check_db(False, links.normal_group2, links.normal_group2ID)

    def test_change_group_user(self):
        expected_answer = f'Группа {links.normal_group2} сохранена в настройках.' \
                          f' Чтобы включить команду {self.command} , воспользуйтесь командой {self.command} on'
        self.pipeline_user(f"group {links.normal_group2}", expected_answer)
        self.check_db(False, links.normal_group2, links.normal_group2ID)

    def test_on_group_chat(self):
        expected_answer = f'Команда {self.command} включена. По этой команде в чат будет приходить случайно выбранный пост из группы {links.normal_group1}.'
        self.pipeline_chat_from_owner("on", expected_answer)
        self.check_db(True, links.normal_group1, links.normal_group1ID)

    def test_on_group_user(self):
        expected_answer = f'Команда {self.command} включена. По этой команде в чат будет приходить случайно выбранный пост из группы {links.normal_group1}.'
        self.pipeline_user("on", expected_answer)
        self.check_db(True, links.normal_group1, links.normal_group1ID)

    def test_delete_chat(self):
        expected_answer = f'Группа для команды {self.command} удалена из настроек. Команда {self.command} выключена.'
        self.pipeline_chat_from_owner("group delete", expected_answer)
        self.check_db(False, "", None)

    def test_delete_user(self):
        expected_answer = f'Группа для команды {self.command} удалена из настроек. Команда {self.command} выключена.'
        self.pipeline_user("group delete", expected_answer)
        self.check_db(False, "", None)

    def test_post(self):
        expected_answer = f"Чтобы включить команду {self.command}, воспользуйтесь командой {self.command} on."
        self.pipeline_user("", expected_answer)
        self.pipeline_chat_from_owner("", expected_answer)

    def test_post_not_chat_owner(self):
        expected_answer = "nothing will be sent"
        self.pipeline_chat_not_owner("", expected_answer)


class RandomPostAddGroup(TestCase, Shared, PipelinesAndSetUps):  # 4
    field_dict = dict()

    def setUp(self):
        super().setup_with_user_profile()

    def test_add_group_chat(self):
        expected_answer = f'Группа {links.normal_group2} сохранена в настройках.' \
                          f' Чтобы включить команду {self.command} , воспользуйтесь командой {self.command} on'
        self.pipeline_chat_from_owner(f"group {links.normal_group2}", expected_answer)
        self.check_db(False, links.normal_group2, links.normal_group2ID)

    def test_add_group_user(self):
        expected_answer = f'Группа {links.normal_group2} сохранена в настройках.' \
                          f' Чтобы включить команду {self.command} , воспользуйтесь командой {self.command} on'
        self.pipeline_user(f"group {links.normal_group2}", expected_answer)
        self.check_db(False, links.normal_group2, links.normal_group2ID)

    def test_add_bad_group_chat(self):
        expected_answer = f'Группа {links.nonexisting_group} не может быть зарегистрирована для команды {self.command}.' \
                          ' Убедитесь, что ссылка правильная, и группа не является закрытой'
        self.pipeline_chat_from_owner(f"group {links.nonexisting_group}", expected_answer)
        self.check_db(False, "", None)

    def test_add_bad_group_user(self):
        expected_answer = f'Группа {links.nonexisting_group} не может быть зарегистрирована для команды {self.command}.' \
                          ' Убедитесь, что ссылка правильная, и группа не является закрытой'
        self.pipeline_user(f"group {links.nonexisting_group}", expected_answer)
        self.check_db(False, "", None)


class RandomPostNoProfileModeOFFTest(TestCase, Shared, PipelinesAndSetUps):  # 3
    field_dict = {"random_post_group_link": links.normal_group1,
                  "random_post_group_id": links.normal_group1ID, "random_post_mode": False}
    expected_answer = f"Чтобы пользоваться командой '{random_post} on', пройдите по ссылке {LOGIN_LINK}"

    def setUp(self):
        super().setup()

    def test_on_group_user(self):
        self.pipeline_user("on", self.expected_answer)

    def test_on_group_chat(self):
        self.pipeline_chat_from_owner("on", self.expected_answer)

    def test_on_not_chat_owner(self):
        expected_answer = f'Для вас доступна команда {self.command} без дополнительных опций.'
        self.pipeline_chat_not_owner("on", expected_answer)


class RandomPostExpiredTokenModeOFFTest(TestCase, Shared, PipelinesAndSetUps):  # 3
    field_dict = {"random_post_group_link": links.normal_group1,
                  "random_post_group_id": links.normal_group1ID, "random_post_mode": False}
    expected_answer = f'Обновите токен по ссылке {LOGIN_LINK}'

    def setUp(self):
        super().setup()
        super().set_user_profile(test_personal_expired_token)

    def test_on_group_user(self):
        self.pipeline_user("on", self.expected_answer)

    def test_on_group_chat(self):
        self.pipeline_chat_from_owner("on", self.expected_answer)

    def test_on_not_chat_owner(self):
        expected_answer = f'Для вас доступна команда {self.command} без дополнительных опций.'
        self.pipeline_chat_not_owner("on", expected_answer)


class RandomPostExpiredTokenModeONTest(TestCase, Shared, PipelinesAndSetUps):  # 3
    field_dict = {"random_post_group_link": links.normal_group1,
                  "random_post_group_id": links.normal_group1ID, "random_post_mode": True}
    expected_answer = f"Для корректной работы бота пройдите по ссылке {LOGIN_LINK}."

    def setUp(self):
        super().setup()
        super().set_user_profile(test_personal_expired_token)

    def test_on_group_user(self):
        self.pipeline_user("", self.expected_answer)

    def test_on_group_chat(self):
        self.pipeline_chat_from_owner("", self.expected_answer)

    def test_on_not_chat_owner(self):  # message is sent to chat owner (not to the user who called '/post' command)
        self.pipeline_chat_not_owner("", self.expected_answer)
