from typing import Optional

from django.test import TestCase

from vk import models
from vk.helpers import new_post
from vk.tests.shared.pipelines_and_setups import PipelinesAndSetUps
from web_vk.constants import test_personal_expired_token, LOGIN_LINK
from vk.tests.shared.shared_tests.common_group_tests import NOGROUPTestMixin, THEREISGROUPOffTestMixin, \
    THEREISGROUPOnTestMixin
from vk.tests.shared.shared_tests.user_specific_commands_test import UserSpecificCommandsMixinTest

from vk.tests.data_for_tests.message_data import OwnerAndBotChatData
import vk.tests.data_for_tests.group_links as links


class Shared:
    command = f"{new_post}"
    setting_model = models.NewPostSetting

    def check_db(self, mode: bool, grouplink: str, groupid: Optional[int]):
        self.setting_object.refresh_from_db()
        self.assertEqual(self.setting_object.newpost_mode, mode)
        self.assertEqual(self.setting_object.newpost_group_link, grouplink)
        self.assertEqual(self.setting_object.newpost_group_id, groupid)


class UserSpecificNewPostTest(TestCase, Shared, UserSpecificCommandsMixinTest):
    pass


class NewPostNOGROUPTest(TestCase, Shared, NOGROUPTestMixin):
    field_dict = dict()

    @classmethod
    def setUpTestData(cls):
        super().setup_with_user_profile()

    def test_without_option(self):
        expected_answer = "Пожалуйста, уточните опцию."
        self.pipeline_chat_from_owner("", expected_answer)


class NewPostTHEREISGROUPOffTest(TestCase, Shared, THEREISGROUPOffTestMixin):
    field_dict = {"newpost_group_link": links.normal_group1,
                  "newpost_group_id": links.normal_group1ID, "newpost_mode": False}

    @classmethod
    def setUpTestData(cls):
        super().setup()


class NewPostTHEREISGROUPOnTest(TestCase, Shared, THEREISGROUPOnTestMixin):
    field_dict = {"newpost_group_link": links.normal_group1,
                  "newpost_group_id": links.normal_group1ID, "newpost_mode": True}

    @classmethod
    def setUpTestData(cls):
        super().setup_with_user_profile()


class NewPostTurnOffDeleteChangeONTest(TestCase, Shared, PipelinesAndSetUps):  # 7
    field_dict = {"newpost_group_link": links.normal_group1,
                  "newpost_group_id": links.normal_group1ID, "newpost_mode": True}

    def setUp(self):
        super().setup_with_user_profile()

    def test_off_chat(self):
        expected_answer = f'Режим {new_post} выключен, свежие посты присылаться не будут.'
        self.pipeline_chat_from_owner("off", expected_answer)
        self.check_db(False, links.normal_group1, links.normal_group1ID)

    def test_off_user(self):
        expected_answer = f'Режим {new_post} выключен, свежие посты присылаться не будут.'
        self.pipeline_user("off", expected_answer)
        self.check_db(False, links.normal_group1, links.normal_group1ID)

    def test_delete_chat(self):
        expected_answer = f'Группа для режима {new_post} удалена из настроек, свежие посты присылаться не будут.'
        self.pipeline_chat_from_owner("group delete", expected_answer)
        self.check_db(False, "", None)

    def test_delete_user(self):
        expected_answer = f'Группа для режима {new_post} удалена из настроек, свежие посты присылаться не будут.'
        self.pipeline_user("group delete", expected_answer)
        self.check_db(False, "", None)

    def test_change_group_chat(self):
        expected_answer = f'Группа {links.normal_group2} сохранена в настройках.' \
                          f' Посты этой группы будут приходить в ваш чат по мере их появления.'
        self.pipeline_chat_from_owner(f"group {links.normal_group2}", expected_answer)
        self.check_db(True, links.normal_group2, links.normal_group2ID)

    def test_change_group_user(self):
        expected_answer = f'Группа {links.normal_group2} сохранена в настройках.' \
                          f' Посты этой группы будут приходить в ваш чат по мере их появления.'
        self.pipeline_user(f"group {links.normal_group2}", expected_answer)
        self.check_db(True, links.normal_group2, links.normal_group2ID)

    def test_chat_not_owner(self):
        expected_answer = 'Только владелец беседы может использовать эту команду.'
        self.pipeline_chat_not_owner("group delete", expected_answer)


class NewPostTurnOnDeleteChangeOFFTest(TestCase, Shared, PipelinesAndSetUps):  # 6
    field_dict = {"newpost_group_link": links.normal_group1,
                  "newpost_group_id": links.normal_group1ID, "newpost_mode": False}

    def setUp(self):
        super().setup_with_user_profile()

    def test_change_group_chat(self):
        expected_answer = f'Группа {links.normal_group2} сохранена в настройках.' \
                          f' Чтобы получать обновления из этой группы, воспользуйтесь командой {new_post} on'
        self.pipeline_chat_from_owner(f"group {links.normal_group2}", expected_answer)
        self.check_db(False, links.normal_group2, links.normal_group2ID)

    def test_change_group_user(self):
        expected_answer = f'Группа {links.normal_group2} сохранена в настройках.' \
                          f' Чтобы получать обновления из этой группы, воспользуйтесь командой {new_post} on'
        self.pipeline_user(f"group {links.normal_group2}", expected_answer)
        self.check_db(False, links.normal_group2, links.normal_group2ID)

    def test_on_group_chat(self):
        expected_answer = f'Режим {new_post} включен. Посты группы {links.normal_group1} будут приходить в ваш чат по мере их появления.'
        self.pipeline_chat_from_owner("on", expected_answer)
        self.check_db(True, links.normal_group1, links.normal_group1ID)

    def test_on_group_user(self):
        expected_answer = f'Режим {new_post} включен. Посты группы {links.normal_group1} будут приходить в ваш чат по мере их появления.'
        self.pipeline_user("on", expected_answer)
        self.check_db(True, links.normal_group1, links.normal_group1ID)

    def test_delete_chat(self):
        expected_answer = f'Группа для режима {new_post} удалена из настроек, свежие посты присылаться не будут.'
        self.pipeline_chat_from_owner("group delete", expected_answer)
        self.check_db(False, "", None)

    def test_delete_user(self):
        expected_answer = f'Группа для режима {new_post} удалена из настроек, свежие посты присылаться не будут.'
        self.pipeline_user("group delete", expected_answer)
        self.check_db(False, "", None)


class NewPostAddGroup(TestCase, Shared, PipelinesAndSetUps):
    field_dict = dict()

    def setUp(self):
        super().setup_with_user_profile()

    def test_add_group_chat(self):
        expected_answer = f'Группа {links.normal_group2} сохранена в настройках.' \
                          f' Чтобы получать обновления из этой группы, воспользуйтесь командой {new_post} on'
        self.pipeline_chat_from_owner(f"group {links.normal_group2}", expected_answer)
        self.check_db(False, links.normal_group2, links.normal_group2ID)

    def test_add_group_user(self):
        expected_answer = f'Группа {links.normal_group2} сохранена в настройках.' \
                          f' Чтобы получать обновления из этой группы, воспользуйтесь командой {new_post} on'
        self.pipeline_user(f"group {links.normal_group2}", expected_answer)
        self.check_db(False, links.normal_group2, links.normal_group2ID)

    def test_add_bad_group_chat(self):
        expected_answer = f'Группа {links.nonexisting_group} не может быть зарегистрирована для команды {new_post}.' \
                          ' Убедитесь, что ссылка правильная, и группа не является закрытой'
        self.pipeline_chat_from_owner(f"group {links.nonexisting_group}", expected_answer)
        self.check_db(False, "", None)

    def test_add_bad_group_user(self):
        expected_answer = f'Группа {links.nonexisting_group} не может быть зарегистрирована для команды {new_post}.' \
                          ' Убедитесь, что ссылка правильная, и группа не является закрытой'
        self.pipeline_user(f"group {links.nonexisting_group}", expected_answer)
        self.check_db(False, "", None)


class NewPostNoProfileModeOFFTest(TestCase, Shared, PipelinesAndSetUps):  # 3
    field_dict = {"newpost_group_link": links.normal_group1,
                  "newpost_group_id": links.normal_group1ID, "newpost_mode": False}
    expected_answer = f"Чтобы пользоваться командой '{new_post} on', пройдите по ссылке {LOGIN_LINK}"

    def setUp(self):
        super().setup()

    def test_on_group_user(self):
        self.pipeline_user("on", self.expected_answer)

    def test_on_group_chat(self):
        self.pipeline_chat_from_owner("on", self.expected_answer)

    def test_on_not_chat_owner(self):
        expected_answer = 'Только владелец беседы может использовать эту команду.'
        self.pipeline_chat_not_owner("on", expected_answer)


class NewPostExpiredTokenModeOFFTest(TestCase, Shared, PipelinesAndSetUps):  # 3
    field_dict = {"newpost_group_link": links.normal_group1,
                  "newpost_group_id": links.normal_group1ID, "newpost_mode": False}
    expected_answer = f'Обновите токен по ссылке {LOGIN_LINK}'

    def setUp(self):
        super().setup()
        super().set_user_profile(test_personal_expired_token)

    def test_on_group_user(self):
        self.pipeline_user("on", self.expected_answer)

    def test_on_group_chat(self):
        self.pipeline_chat_from_owner("on", self.expected_answer)

    def test_on_not_chat_owner(self):
        expected_answer = 'Только владелец беседы может использовать эту команду.'
        self.pipeline_chat_not_owner("on", expected_answer)
