from vk.tests.shared.pipelines_and_setups import PipelinesAndSetUps

import vk.tests.data_for_tests.group_links as links


# class CommandNOGROUPTestMixin(PipelinesAndSetUps): # всё есть в NOGROUPTestMixin
#
#     def test_info(self):
#         expected_answer = f"У вас нет сохраненной группы для команды {self.command}."
#         self.pipeline_class("info", expected_answer)
#
#     def test_delete(self):
#         expected_answer = f'У вас нет сохраненной группы для команды {self.command}.'
#         self.pipeline_class("delete", expected_answer)
#
#     def test_on(self):
#         expected_answer = f"Чтобы пользоваться командой '{self.command} on', сохраните в настройках ссылку на группу. " \
#                           f"Сделать это можно командой {self.command} group," \
#                           f" например: {self.command} group https://vk.com/link_to_the_group"
#         self.pipeline_class("on", expected_answer)
#
#     def test_off(self):
#         expected_answer = f'Команда {self.command} уже выключена.'
#         self.pipeline_class("off", expected_answer)


# class CommandTHEREISGROUPOffTestMixin(PipelinesAndSetUps): # duplicate THEREISGROUPOffTestMixin
#
#     def test_info(self):
#         expected_answer = f'Для команды {self.command} у вас зарегистрирована группа {links.normal_group1}. Команда {self.command} выключена.'
#         self.pipeline_class("info", expected_answer)
#
#     def test_off(self):
#         expected_answer = f'Команда {self.command} уже выключена.'
#         self.pipeline_class("off", expected_answer)


# class CommandTHEREISGROUPOnTestMixin(PipelinesAndSetUps): # duplicate THEREISGROUPOnTestMixin
#
#     def test_info(self):
#         expected_answer = f'Команда {self.command} включена. Группа в настройках: {links.normal_group1}.'
#         self.pipeline_class("info", expected_answer)
#
#     def test_on(self):
#         expected_answer = f'Команда {self.command} уже включена. Группа в настройках: {links.normal_group1}.'
#         self.pipeline_class("on", expected_answer)
