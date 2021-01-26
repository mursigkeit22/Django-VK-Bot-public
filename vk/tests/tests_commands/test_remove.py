from typing import Optional

from django.test import TestCase

from vk import models
from vk.helpers import remove
from vk.tests.shared.pipelines_and_setups import PipelinesAndSetUps
from vk.tests.shared.shared_tests.common_group_tests import NOGROUPTestMixin, THEREISGROUPOffTestMixin, \
    THEREISGROUPOnTestMixin
from vk.tests.shared.shared_tests.user_specific_commands_test import UserSpecificCommandsMixinTest
import vk.tests.data_for_tests.group_links as links


class Shared:
    command = f"{remove}"
    setting_model = models.KickNonMembersSetting

    def check_db(self, mode: bool, grouplink: str, groupid: Optional[int]):
        self.setting_object.refresh_from_db()
        self.assertEqual(self.setting_object.kick_nonmembers_mode, mode)
        self.assertEqual(self.setting_object.kick_nonmembers_group_link, grouplink)
        self.assertEqual(self.setting_object.kick_nonmembers_group_id, groupid)


class UserSpecificKickNonMembersTest(TestCase, Shared, UserSpecificCommandsMixinTest):  # 6
    pass


class KickNonMembersNOGROUPTest(TestCase, Shared, NOGROUPTestMixin):  # 6 + 1
    field_dict = dict()

    @classmethod
    def setUpTestData(cls):
        super().setup()

    def test_remove_option(self):
        expected_answer = f"Чтобы включить команду {self.command}, воспользуйтесь командой {self.command} on."
        self.pipeline_chat_from_owner("", expected_answer)


class KickNonMembersTHEREISGROUPOffTest(TestCase, Shared, THEREISGROUPOffTestMixin):  # 3

    field_dict = {"kick_nonmembers_group_link": links.normal_group1,
                  "kick_nonmembers_group_id": links.normal_group1ID, "kick_nonmembers_mode": False}

    @classmethod
    def setUpTestData(cls):
        super().setup()


class KickNonMembersTHEREISGROUPOnTest(TestCase, Shared, THEREISGROUPOnTestMixin):  # 3 + 1

    field_dict = {"kick_nonmembers_group_link": links.normal_group1,
                  "kick_nonmembers_group_id": links.normal_group1ID, "kick_nonmembers_mode": True}

    @classmethod
    def setUpTestData(cls):
        super().setup()

    def test_remove(self):
        expected_answer = "Чтобы кого-нибудь удалить из беседы, нужно сначала кого-нибудь в неё добавить."
        self.pipeline_user("", expected_answer)
        self.pipeline_chat_from_owner("", expected_answer)



class KickNonMembersTurnOffDeleteChangeONTest(TestCase, Shared, PipelinesAndSetUps):  # 7
    field_dict = {"kick_nonmembers_group_link": links.normal_group1,
                  "kick_nonmembers_group_id": links.normal_group1ID, "kick_nonmembers_mode": True}

    def setUp(self):
        super().setup()

    def test_off_chat(self):
        expected_answer = f'Команда {remove} выключена.'
        self.pipeline_chat_from_owner("off", expected_answer)
        self.check_db(False, links.normal_group1, links.normal_group1ID)

    def test_off_user(self):
        expected_answer = f'Команда {remove} выключена.'
        self.pipeline_user("off", expected_answer)
        self.check_db(False, links.normal_group1, links.normal_group1ID)

    def test_delete_chat(self):
        expected_answer = f'Группа для команды {remove} удалена из настроек. Команда {remove} выключена.'
        self.pipeline_chat_from_owner("group delete", expected_answer)
        self.check_db(False, "", None)

    def test_delete_user(self):
        expected_answer = f'Группа для команды {remove} удалена из настроек. Команда {remove} выключена.'
        self.pipeline_user("group delete", expected_answer)
        self.check_db(False, "", None)

    def test_change_group_chat(self):
        expected_answer = f'Группа {links.normal_group2} сохранена в настройках. Команда {remove} включена.'
        self.pipeline_chat_from_owner(f"group {links.normal_group2}", expected_answer)
        self.check_db(True, links.normal_group2, links.normal_group2ID)

    def test_change_group_user(self):
        expected_answer = f'Группа {links.normal_group2} сохранена в настройках. Команда {remove} включена.'
        self.pipeline_user(f"group {links.normal_group2}", expected_answer)
        self.check_db(True, links.normal_group2, links.normal_group2ID)

    def test_chat_not_owner(self):
        expected_answer = 'Только владелец беседы может использовать эту команду.'
        self.pipeline_chat_not_owner("group delete", expected_answer)


class KickNonMembersTurnOnDeleteChangeOFFTest(TestCase, Shared, PipelinesAndSetUps):  # 6 + 2
    field_dict = {"kick_nonmembers_group_link": links.normal_group1,
                  "kick_nonmembers_group_id": links.normal_group1ID, "kick_nonmembers_mode": False}

    def setUp(self):
        super().setup()

    def test_change_group_chat(self):
        expected_answer = f'Группа {links.normal_group2} сохранена в настройках.' \
                          f' Чтобы включить команду {remove} , воспользуйтесь командой {remove} on'
        self.pipeline_chat_from_owner(f"group {links.normal_group2}", expected_answer)
        self.check_db(False, links.normal_group2, links.normal_group2ID)

    def test_change_group_user(self):
        expected_answer = f'Группа {links.normal_group2} сохранена в настройках.' \
                          f' Чтобы включить команду {remove} , воспользуйтесь командой {remove} on'
        self.pipeline_user(f"group {links.normal_group2}", expected_answer)
        self.check_db(False, links.normal_group2, links.normal_group2ID)

    def test_on_group_chat(self):
        expected_answer = f'Команда {remove} включена. С её помощью вы можете удалять из чата участников, которые не состоят в группе {links.normal_group1}.'
        self.pipeline_chat_from_owner("on", expected_answer)
        self.check_db(True, links.normal_group1, links.normal_group1ID)

    def test_on_group_user(self):
        expected_answer = f'Команда {remove} включена. С её помощью вы можете удалять из чата участников, которые не состоят в группе {links.normal_group1}.'
        self.pipeline_user("on", expected_answer)
        self.check_db(True, links.normal_group1, links.normal_group1ID)

    def test_delete_chat(self):
        expected_answer = f'Группа для команды {remove} удалена из настроек. Команда {remove} выключена.'
        self.pipeline_chat_from_owner("group delete", expected_answer)
        self.check_db(False, "", None)

    def test_delete_user(self):
        expected_answer = f'Группа для команды {remove} удалена из настроек. Команда {remove} выключена.'
        self.pipeline_user("group delete", expected_answer)
        self.check_db(False, "", None)

    def test_remove(self):
        expected_answer = f"Чтобы включить команду {remove}, воспользуйтесь командой {remove} on."
        self.pipeline_user("", expected_answer)
        self.pipeline_chat_from_owner("", expected_answer)

    def test_remove_not_chat_owner(self):
        expected_answer = 'Только владелец беседы может использовать эту команду.'
        self.pipeline_chat_not_owner("", expected_answer)


class KickNonMembersAddGroup(TestCase, Shared, PipelinesAndSetUps):  # 4
    field_dict = dict()

    def setUp(self):
        super().setup()

    def test_add_group_chat(self):
        expected_answer = f'Группа {links.normal_group2} сохранена в настройках.' \
                          f' Чтобы включить команду {remove} , воспользуйтесь командой {remove} on'
        self.pipeline_chat_from_owner(f"group {links.normal_group2}", expected_answer)
        self.check_db(False, links.normal_group2, links.normal_group2ID)

    def test_add_group_user(self):
        expected_answer = f'Группа {links.normal_group2} сохранена в настройках.' \
                          f' Чтобы включить команду {remove} , воспользуйтесь командой {remove} on'
        self.pipeline_user(f"group {links.normal_group2}", expected_answer)
        self.check_db(False, links.normal_group2, links.normal_group2ID)

    def test_add_bad_group_chat(self):
        expected_answer = f'Группа {links.nonexisting_group} не может быть зарегистрирована для команды {remove}.' \
                          ' Убедитесь, что ссылка правильная, и группа не является закрытой'
        self.pipeline_chat_from_owner(f"group {links.nonexisting_group}", expected_answer)
        self.check_db(False, "", None)

    def test_add_bad_group_user(self):
        expected_answer = f'Группа {links.nonexisting_group} не может быть зарегистрирована для команды {remove}.' \
                          ' Убедитесь, что ссылка правильная, и группа не является закрытой'
        self.pipeline_user(f"group {links.nonexisting_group}", expected_answer)
        self.check_db(False, "", None)
