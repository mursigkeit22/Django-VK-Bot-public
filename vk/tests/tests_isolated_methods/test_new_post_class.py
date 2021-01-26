from typing import Optional

from django.test import TestCase

from vk import models
from vk.command_handlers.NewPostCommandHandler import NewPostCommandHandler
from vk.helpers import new_post
from vk.tests.data_for_tests.event_dicts import event_dict_simple_message
from vk.tests.data_for_tests.message_data import OwnerAndBotChatData
from vk.tests.shared.shared_tests.common_group_class_tests import CommandNOGROUPTestMixin, \
    CommandTHEREISGROUPOffTestMixin, \
    CommandTHEREISGROUPOnTestMixin
from vk.tests.shared.pipelines_and_setups import PipelinesAndSetUps
from vk.tests.shared.shared_tests.common_valid_option_test import ValidOptionMixinTest
from vk.text_parser import TextParser
from vk.vkreceiver_message_handler import MessageHandler
import vk.tests.data_for_tests.group_links as links


class ValidOptionTest(TestCase, ValidOptionMixinTest): # 9
    command = f"{new_post}"
    command_handler = NewPostCommandHandler

    @classmethod
    def setUpTestData(cls):
        super().setup()


class SharedMethods:
    command = f"{new_post}"
    command_handler = NewPostCommandHandler
    setting_model = models.NewPostSetting

    def check_db(self, mode: bool, grouplink: str, groupid: Optional[int]):
        self.setting_object.refresh_from_db()
        self.assertEqual(self.setting_object.newpost_mode, mode)
        self.assertEqual(self.setting_object.newpost_group_link, grouplink)
        self.assertEqual(self.setting_object.newpost_group_id, groupid)


class CommandNOGROUPTest(TestCase, SharedMethods, CommandNOGROUPTestMixin): # 4
    field_dict = dict()

    @classmethod
    def setUpTestData(cls):
        super().setup_class_with_user_profile()


class CommandTHEREISGROUPOffTest(TestCase, SharedMethods, CommandTHEREISGROUPOffTestMixin): #2
    field_dict = {"newpost_group_link": links.normal_group1,
                  "newpost_group_id": links.normal_group1ID, "newpost_mode": False}

    @classmethod
    def setUpTestData(cls):
        super().setup_class()


class CommandTHEREISGROUPOnTest(TestCase, SharedMethods, CommandTHEREISGROUPOnTestMixin): #2
    field_dict = {"newpost_group_link": links.normal_group1,
                  "newpost_group_id": links.normal_group1ID, "newpost_mode": True}

    @classmethod
    def setUpTestData(cls):
        super().setup_class_with_user_profile()


class CommandTurnOffDeleteChangeONTest(TestCase, SharedMethods, PipelinesAndSetUps): # 3
    field_dict = {"newpost_group_link": links.normal_group1,
                  "newpost_group_id": links.normal_group1ID, "newpost_mode": True}

    def setUp(self):
        self.setup_class()

    def test_off(self):
        expected_answer = f'Режим {new_post} выключен, свежие посты присылаться не будут.'
        self.pipeline_class("off", expected_answer)
        self.check_db(False, links.normal_group1, links.normal_group1ID)

    def test_delete(self):
        expected_answer = f'Группа для режима {new_post} удалена из настроек, свежие посты присылаться не будут.'
        self.pipeline_class("delete", expected_answer)
        self.check_db(False, "", None)

    def test_change_group(self):
        expected_answer = f'Группа {links.normal_group2} сохранена в настройках.' \
                          f' Посты этой группы будут приходить в ваш чат по мере их появления.'
        self.pipeline_class((links.normal_group2_screen_name, links.normal_group2ID), expected_answer)
        self.check_db(True, links.normal_group2, links.normal_group2ID)


class CommandTurnOnChangeOFFTest(TestCase, SharedMethods, PipelinesAndSetUps): # 3
    field_dict = {"newpost_group_link": links.normal_group1,
                  "newpost_group_id": links.normal_group1ID, "newpost_mode": False}

    def setUp(self):
        self.setup_class_with_user_profile()

    def test_change_group(self):
        expected_answer = f'Группа {links.normal_group2} сохранена в настройках.' \
                          f' Чтобы получать обновления из этой группы, воспользуйтесь командой {new_post} on'
        self.pipeline_class((links.normal_group2_screen_name, links.normal_group2ID), expected_answer)
        self.check_db(False, links.normal_group2, links.normal_group2ID)

    def test_on_group(self):
        expected_answer = f'Режим {new_post} включен. Посты группы {links.normal_group1} будут приходить в ваш чат по мере их появления.'
        self.pipeline_class("on", expected_answer)
        self.check_db(True, links.normal_group1, links.normal_group1ID)

    def test_delete(self):
        expected_answer = f'Группа для режима {new_post} удалена из настроек, свежие посты присылаться не будут.'
        self.pipeline_class("delete", expected_answer)
        self.check_db(False, "", None)


class CommandAddGroup(TestCase, SharedMethods, PipelinesAndSetUps):  # 1
    field_dict = dict()

    def setUp(self):
        self.setup_class()

    def test_add_group(self):
        expected_answer = f'Группа {links.normal_group2} сохранена в настройках.' \
                          f' Чтобы получать обновления из этой группы, воспользуйтесь командой {new_post} on'
        self.pipeline_class((links.normal_group2_screen_name, links.normal_group2ID), expected_answer)
        self.check_db(False, links.normal_group2, links.normal_group2ID)
