from typing import Optional

from django.test import TestCase

from vk import models
from vk.command_handlers.RandomPostCommandHandler import RandomPostCommandHandler
from vk.helpers import random_post
from vk.tests.shared.shared_tests.common_group_class_tests import CommandNOGROUPTestMixin, \
    CommandTHEREISGROUPOffTestMixin, \
    CommandTHEREISGROUPOnTestMixin
from vk.tests.shared.pipelines_and_setups import PipelinesAndSetUps
from vk.tests.shared.shared_tests.common_valid_option_test import ValidOptionMixinTest
import vk.tests.data_for_tests.group_links as links


class ValidOptionTest(TestCase, ValidOptionMixinTest):  # 8 + 1
    command = f"{random_post}"
    command_handler = RandomPostCommandHandler

    @classmethod
    def setUpTestData(cls):
        super().setup()


class Shared:
    command = f"{random_post}"
    command_handler = RandomPostCommandHandler
    setting_model = models.RandomPostSetting

    def check_db(self, mode: bool, grouplink: str, groupid: Optional[int]):
        self.setting_object.refresh_from_db()
        self.assertEqual(self.setting_object.random_post_mode, mode)
        self.assertEqual(self.setting_object.random_post_group_link, grouplink)
        self.assertEqual(self.setting_object.random_post_group_id, groupid)


class CommandNOGROUPTest(TestCase, Shared, CommandNOGROUPTestMixin, ):  # 4
    field_dict = dict()

    @classmethod
    def setUpTestData(cls):
        super().setup_class_with_user_profile()


class CommandTHEREISGROUPOffTest(TestCase, Shared, CommandTHEREISGROUPOffTestMixin, ):  # 2
    field_dict = {"random_post_group_link": links.normal_group1,
                  "random_post_group_id": links.normal_group1ID, "random_post_mode": False}

    @classmethod
    def setUpTestData(cls):
        super().setup_class_with_user_profile()


class CommandTHEREISGROUPOnTest(TestCase, Shared, CommandTHEREISGROUPOnTestMixin, ):  # 2
    field_dict = {"random_post_group_link": links.normal_group1,
                  "random_post_group_id": links.normal_group1ID, "random_post_mode": True}

    @classmethod
    def setUpTestData(cls):
        super().setup_class_with_user_profile()


class CommandTurnOffDeleteChangeONTest(TestCase, Shared, PipelinesAndSetUps):  # 3
    field_dict = {"random_post_group_link": links.normal_group1,
                  "random_post_group_id": links.normal_group1ID, "random_post_mode": True}

    def setUp(self):
        self.setup_class()

    def test_off(self):
        expected_answer = f'Команда {self.command} выключена.'
        self.pipeline_class("off", expected_answer)
        self.check_db(False, links.normal_group1, links.normal_group1ID)

    def test_delete(self):
        expected_answer = f'Группа для команды {self.command} удалена из настроек. Команда {self.command} выключена.'
        self.pipeline_class("delete", expected_answer)
        self.check_db(False, "", None)

    def test_change_group(self):
        expected_answer = f'Группа {links.normal_group2} сохранена в настройках. Команда {self.command} включена.'
        self.pipeline_class((links.normal_group2_screen_name, links.normal_group2ID), expected_answer)
        self.check_db(True, links.normal_group2, links.normal_group2ID)


class CommandTurnOnChangeOFFTest(TestCase, Shared, PipelinesAndSetUps):  # 5
    field_dict = {"random_post_group_link": links.normal_group1,
                  "random_post_group_id": links.normal_group1ID, "random_post_mode": False}

    def setUp(self):
        self.setup_class_with_user_profile()

    def test_change_group(self):
        expected_answer = f'Группа {links.normal_group2} сохранена в настройках.' \
                          f' Чтобы включить команду {self.command} , воспользуйтесь командой {self.command} on'
        self.pipeline_class((links.normal_group2_screen_name, links.normal_group2ID), expected_answer)
        self.check_db(False, links.normal_group2, links.normal_group2ID)

    def test_on_group(self):
        expected_answer = f'Команда {self.command} включена. По этой команде в чат будет приходить случайно выбранный пост из группы {links.normal_group1}.'
        self.pipeline_class("on", expected_answer)
        self.check_db(True, links.normal_group1, links.normal_group1ID)

    def test_delete(self):
        expected_answer = f'Группа для команды {self.command} удалена из настроек. Команда {self.command} выключена.'
        self.pipeline_class("delete", expected_answer)
        self.check_db(False, "", None)

    def test_post_owner(self):
        self.pipeline_class("post", f"Чтобы включить команду {self.command}, воспользуйтесь командой {self.command} on.")

    def test_post_not_owner(self):
        self.handler_object.from_id = 12345678
        self.pipeline_class("post", "nothing will be sent")


class CommandAddGroup(TestCase, Shared, PipelinesAndSetUps):  # 2
    field_dict = dict()

    def setUp(self):
        self.setup_class()

    def test_add_group(self):
        expected_answer = f'Группа {links.normal_group2} сохранена в настройках.' \
                          f' Чтобы включить команду {self.command} , воспользуйтесь командой {self.command} on'
        self.pipeline_class((links.normal_group2_screen_name, links.normal_group2ID), expected_answer)
        self.check_db(False, links.normal_group2, links.normal_group2ID)
