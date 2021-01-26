from vk import models
from vk.tests.data_for_tests.message_data import OwnerAndBotChatData
from vk.tests.shared.pipelines_and_setups import PipelinesAndSetUps
import vk.tests.data_for_tests.group_links as links


class NOGROUPTestMixin(PipelinesAndSetUps):

    def test_info(self):
        expected_answer = f"У вас нет сохраненной группы для команды {self.command}."
        self.pipeline_chat_from_owner("info", expected_answer)
        self.pipeline_user("info", expected_answer)

    def test_delete_chat(self):
        expected_answer = f"У вас нет сохраненной группы для команды {self.command}."
        self.pipeline_chat_from_owner("group delete", expected_answer)
        self.pipeline_user("group delete", expected_answer)

    def test_on_chat(self):
        expected_answer = f"Чтобы пользоваться командой '{self.command} on', сохраните в настройках ссылку на группу. " \
                          f"Сделать это можно командой {self.command} group," \
                          f" например: {self.command} group https://vk.com/link_to_the_group"
        self.pipeline_chat_from_owner("on", expected_answer)
        self.pipeline_user("on", expected_answer)

    def test_off_chat(self):
        expected_answer = f'Команда {self.command} уже выключена.'
        self.pipeline_chat_from_owner("off", expected_answer)
        self.pipeline_user("off", expected_answer)

    def test_not_valid_option_chat(self):
        expected_answer = f"У команды {self.command} нет опции 'asdf'."
        self.pipeline_chat_from_owner("asdf", expected_answer)
        self.pipeline_user("asdf", expected_answer)

    def test_chat_not_owner(self):
        expected_answer = 'Только владелец беседы может использовать эту команду.'
        self.pipeline_chat_not_owner("info", expected_answer)


class THEREISGROUPOffTestMixin(PipelinesAndSetUps):

    def test_info(self):
        expected_answer = f'Для команды {self.command} у вас зарегистрирована группа {links.normal_group1}. Команда {self.command} выключена.'
        self.pipeline_chat_from_owner("info", expected_answer)
        self.pipeline_user("info", expected_answer)

    def test_off(self):
        expected_answer = f'Команда {self.command} уже выключена.'
        self.pipeline_chat_from_owner("off", expected_answer)
        self.pipeline_user("off", expected_answer)

    def test_chat_not_owner(self):
        expected_answer = 'Только владелец беседы может использовать эту команду.'
        self.pipeline_chat_not_owner("off", expected_answer)


class THEREISGROUPOnTestMixin(PipelinesAndSetUps):

    def test_info(self):
        expected_answer = f'Команда {self.command} включена. Группа в настройках: {links.normal_group1}.'
        self.pipeline_chat_from_owner("info", expected_answer)
        self.pipeline_user("info", expected_answer)

    def test_on(self):
        expected_answer = f'Команда {self.command} уже включена. Группа в настройках: {links.normal_group1}.'
        self.pipeline_chat_from_owner("on", expected_answer)
        self.pipeline_user("on", expected_answer)

    def test_chat_not_owner(self):
        expected_answer = 'Только владелец беседы может использовать эту команду.'
        self.pipeline_chat_not_owner("on", expected_answer)



# class TurnOffDeleteChangeONMixin(PipelinesAndSetUps): #TODO: maybe later
#
#     def test_off_chat(self):
#         expected_answer = f'Команда {self.command} выключена.'
#         self.pipeline_chat_from_owner("off", expected_answer)
#         self.check_db(False, links.normal_group1, links.normal_group1ID) #that works.
