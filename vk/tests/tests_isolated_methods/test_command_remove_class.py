from typing import Optional


from django.test import TestCase

from vk import models
from vk.command_handlers.RemoveCommandHandler import RemoveCommandHandler
from vk.helpers import remove
from vk.tests.shared.shared_tests.common_group_class_tests import CommandNOGROUPTestMixin, \
    CommandTHEREISGROUPOffTestMixin, \
    CommandTHEREISGROUPOnTestMixin
from vk.tests.shared.pipelines_and_setups import PipelinesAndSetUps
from vk.tests.shared.shared_tests.common_valid_option_test import ValidOptionMixinTest
import vk.tests.data_for_tests.group_links as links


class ValidOptionTest(TestCase, ValidOptionMixinTest):  # 9 + 1
    command = f"{remove}"
    command_handler = RemoveCommandHandler

    @classmethod
    def setUpTestData(cls):
        super().setup()

    def test_option_remove(self):
        self.pipeline("", (True, "remove"))


class Shared:
    command = f"{remove}"
    command_handler = RemoveCommandHandler
    setting_model = models.KickNonMembersSetting

    def check_db(self, mode: bool, grouplink: str, groupid: Optional[int]):
        self.setting_object.refresh_from_db()
        self.assertEqual(self.setting_object.kick_nonmembers_mode, mode)
        self.assertEqual(self.setting_object.kick_nonmembers_group_link, grouplink)
        self.assertEqual(self.setting_object.kick_nonmembers_group_id, groupid)


class CommandNOGROUPTest(TestCase, Shared, CommandNOGROUPTestMixin, ):  # 4
    field_dict = dict()

    @classmethod
    def setUpTestData(cls):
        super().setup_class()


class CommandTHEREISGROUPOffTest(TestCase, Shared, CommandTHEREISGROUPOffTestMixin, ):  # 2
    field_dict = {"kick_nonmembers_group_link": links.normal_group1,
                  "kick_nonmembers_group_id": links.normal_group1ID, "kick_nonmembers_mode": False}

    @classmethod
    def setUpTestData(cls):
        super().setup_class()



class CommandTHEREISGROUPOnTest(TestCase, Shared, CommandTHEREISGROUPOnTestMixin, ):  # 2 + 1
    field_dict = {"kick_nonmembers_group_link": links.normal_group1,
                  "kick_nonmembers_group_id": links.normal_group1ID, "kick_nonmembers_mode": True}

    @classmethod
    def setUpTestData(cls):
        super().setup_class()

    def test_remove(self):
        expected_answer = "Чтобы кого-нибудь удалить из беседы, нужно сначала кого-нибудь в неё добавить."
        self.pipeline_class("remove", expected_answer)


class CommandTurnOffDeleteChangeONTest(TestCase, Shared, PipelinesAndSetUps):  # 3
    field_dict = {"kick_nonmembers_group_link": links.normal_group1,
                  "kick_nonmembers_group_id": links.normal_group1ID, "kick_nonmembers_mode": True}

    def setUp(self):
        self.setup_class()

    def test_off(self):
        expected_answer = f'Команда {remove} выключена.'
        self.pipeline_class("off", expected_answer)
        self.check_db(False, links.normal_group1, links.normal_group1ID)

    def test_delete(self):
        expected_answer = f'Группа для команды {remove} удалена из настроек. Команда {remove} выключена.'
        self.pipeline_class("delete", expected_answer)
        self.check_db(False, "", None)

    def test_change_group(self):
        expected_answer = f'Группа {links.normal_group2} сохранена в настройках. Команда {remove} включена.'
        self.pipeline_class((links.normal_group2_screen_name, links.normal_group2ID), expected_answer)
        self.check_db(True, links.normal_group2, links.normal_group2ID)


class CommandTurnOnChangeOFFTest(TestCase, Shared, PipelinesAndSetUps):  # 3
    field_dict = {"kick_nonmembers_group_link": links.normal_group1,
                  "kick_nonmembers_group_id": links.normal_group1ID, "kick_nonmembers_mode": False}

    def setUp(self):
        self.setup_class()

    def test_change_group(self):
        expected_answer = f'Группа {links.normal_group2} сохранена в настройках.' \
                          f' Чтобы включить команду {remove} , воспользуйтесь командой {remove} on'
        self.pipeline_class((links.normal_group2_screen_name, links.normal_group2ID), expected_answer)
        self.check_db(False, links.normal_group2, links.normal_group2ID)

    def test_on_group(self):
        expected_answer = f'Команда {remove} включена. С её помощью вы можете удалять из чата участников, которые не состоят в группе {links.normal_group1}.'
        self.pipeline_class("on", expected_answer)
        self.check_db(True, links.normal_group1, links.normal_group1ID)

    def test_delete(self):
        expected_answer = f'Группа для команды {remove} удалена из настроек. Команда {remove} выключена.'
        self.pipeline_class("delete", expected_answer)
        self.check_db(False, "", None)


class CommandAddGroup(TestCase, Shared, PipelinesAndSetUps):  # 2
    field_dict = dict()

    def setUp(self):
        self.setup_class()

    def test_add_group(self):
        expected_answer = f'Группа {links.normal_group2} сохранена в настройках.' \
                          f' Чтобы включить команду {remove} , воспользуйтесь командой {remove} on'
        self.pipeline_class((links.normal_group2_screen_name, links.normal_group2ID), expected_answer)
        self.check_db(False, links.normal_group2, links.normal_group2ID)

    def test_remove(self):
        expected_answer = f"Чтобы включить команду {remove}, воспользуйтесь командой {remove} on."
        self.pipeline_class(f"remove", expected_answer)
