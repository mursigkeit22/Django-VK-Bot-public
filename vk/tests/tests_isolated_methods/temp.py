# from typing import Optional
#
# from django.test import TestCase
#
# from vk import models
# from vk.command_handlers.RandomPostCommandHandler import RandomPostCommandHandler
# from vk.tests.data_for_tests.event_dicts import event_dict_simple_message
# from vk.tests.data_for_tests.message_data import OwnerAndBotChatData
# from vk.text_parser import TextParser
# from vk.vkreceiver_message_handler import MessageHandler
# import vk.tests.data_for_tests.group_links as links
#
#
# class SharedMethods(TestCase):
#
#     def pipeline(self, option: str, mode: bool, expected_answer: str):
#         setting_db_object = models.RandomPostSetting.objects.get(chat_id=self.chat_db_object)
#         setting_db_object.random_post_mode = mode
#         setting_db_object.save()
#         self.handler_object.option = option
#         returned_answer = self.handler_object.command()
#         self.assertEqual(returned_answer, expected_answer)
#
#     def db_check(self, mode: bool, groupID: int):
#         setting_db_object = models.RandomPostSetting.objects.get(chat_id=self.chat_db_object)
#         self.assertEqual(setting_db_object.random_post_mode, mode)
#         self.assertEqual(setting_db_object.random_post_group_id, groupID)
#
#
# class ValidOptionTest(TestCase):
#
#     @classmethod
#     def setUpTestData(cls):
#         """
#         The class-level atomic block allows the creation of initial data at the class level, once for the whole TestCase.
#         This technique allows for faster tests as compared to using setUp()
#         Modifications to in-memory objects from setup work done at the class level will persist between test methods.
#         """
#         chat_db_object = models.Chat.objects.create(
#             chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True)
#         models.RandomPostSetting.objects.create(chat_id=chat_db_object)
#         message_object = MessageHandler(event_dict_simple_message)
#         text_instance = TextParser(message_object)
#         cls.handler_object = RandomPostCommandHandler(text_instance, chat_db_object)
#
#     def test_option_info(self):
#         self.handler_object.wordlist = ["/post", "info"]
#         returned_value = self.handler_object.valid_option()
#         self.assertEqual(returned_value, (True, "info"))
#
#     def test_option_off(self):
#         self.handler_object.wordlist = ["/post", "off"]
#         returned_value = self.handler_object.valid_option()
#         self.assertEqual(returned_value, (True, 'off'))
#
#     def test_option_group_on(self):
#         self.handler_object.wordlist = ["/post", "on"]
#         returned_value = self.handler_object.valid_option()
#         self.assertEqual(returned_value, (True, "on"))
#
#     def test_option_group_error(self):
#         self.handler_object.wordlist = ["/post", "sdfghjk"]
#         returned_value = self.handler_object.valid_option()
#         expected_value = (
#             False, f"У команды /post нет опции {self.handler_object.wordlist[1]}")
#         self.assertEqual(returned_value, expected_value)
#
#     def test_option_extra_words(self):
#         self.handler_object.wordlist = ["/post", "info", "shfjg"]
#         returned_value = self.handler_object.valid_option()
#         self.assertEqual(returned_value, (True, "info"))
#
#
# class CommandPostTest(TestCase):
#
#     @classmethod
#     def setUpTestData(cls):
#         cls.chat_db_object = models.Chat.objects.create(
#             chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True)
#         message_object = MessageHandler(event_dict_simple_message)
#         text_instance = TextParser(message_object)
#         cls.handler_object = RandomPostCommandHandler(text_instance, cls.chat_db_object)
#         cls.handler_object.option = "post"
#
#     def pipeline(self, mode: bool, expected_answer: str, groupID: Optional[int] = None,
#                  grouplink: str = "", ):
#         models.RandomPostSetting.objects.create(chat_id=self.chat_db_object, random_post_group_id=groupID,
#                                                 random_post_group_link=grouplink, random_post_mode=mode)
#         returned_answer = self.handler_object.command()
#         self.assertEqual(returned_answer, expected_answer)
#
#     def test_post_is_off(self):
#         expected_answer = "Чтобы включить команду /post, воспользуйтесь командой /post on"
#         self.pipeline(mode=False, expected_answer=expected_answer)
#
#     def test_wall_is_empty(self):
#         expected_answer = "Стена пуста."
#         self.pipeline(mode=True, expected_answer=expected_answer, groupID=links.public_name_with_empty_wallID)
#
#     def test_group_turned_out_closed(self):
#         expected_answer = f"Что-то пошло не так. Убедитесь, что группа {links.closed_group} не заблокирована и не является закрытой."
#         self.pipeline(mode=True, expected_answer=expected_answer, groupID=links.closed_groupID,
#                       grouplink=links.closed_group)
#
#     def test_group_turned_out_deactivated(self):
#         expected_answer = f"Что-то пошло не так. Убедитесь, что группа {links.deactivated_group} не заблокирована и не является закрытой."
#         self.pipeline(mode=True, expected_answer=expected_answer, groupID=links.deactivated_groupID,
#                       grouplink=links.deactivated_group)
#
#     def test_group_turned_out_private(self):
#         expected_answer = f"Что-то пошло не так. Убедитесь, что группа {links.private_group1} не заблокирована и не является закрытой."
#         self.pipeline(mode=True, expected_answer=expected_answer, groupID=links.private_group1ID,
#                       grouplink=links.private_group1)
#
#     def test_normal_post(self):
#         expected_answer = "random post is sent"
#         self.pipeline(mode=True, expected_answer=expected_answer, groupID=links.normal_group1ID,
#                       grouplink=links.normal_group1)
#
#     def test_only_one_post_on_the_wall(self):
#         expected_answer = "random post is sent"
#         self.pipeline(mode=True, expected_answer=expected_answer, groupID=links.group_with_one_postID,
#                       grouplink=links.group_with_one_post)
#
#
# class CommandInfoOnOffNOGROUPPOSTTest(SharedMethods):
#     @classmethod
#     def setUpTestData(cls):
#         cls.chat_db_object = models.Chat.objects.create(
#             chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True)
#         models.RandomPostSetting.objects.create(chat_id=cls.chat_db_object)
#         message_object = MessageHandler(event_dict_simple_message)
#         text_instance = TextParser(message_object)
#         cls.handler_object = RandomPostCommandHandler(text_instance, cls.chat_db_object)
#
#     def test_INFO(self):
#         expected_answer = "У вас нет зарегистрированной группы для команды /post"
#         self.pipeline("info", False, expected_answer)
#
#     def test_ON(self):
#         expected_answer = "Чтобы включить команду /post, сначала нужно установить группу, " \
#                           "со стены которой будут отправляться рандомные посты. " \
#                           "Сделать это можно следующей командой: /grouppost https://vk.com/link_to_the_group"
#         self.pipeline("on", False, expected_answer)
#
#     def test_OFF(self):
#         expected_answer = 'Команда /post выключена.'
#         self.pipeline("off", False, expected_answer)
#
#
# class CommandInfoOnOffTHEREISGROUPPOSTTest(SharedMethods):
#     @classmethod
#     def setUpTestData(cls):
#         cls.chat_db_object = models.Chat.objects.create(
#             chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True)
#         models.RandomPostSetting.objects.create(chat_id=cls.chat_db_object, random_post_group_link=links.normal_group1,
#                                                 random_post_group_id=links.normal_group1ID)
#         message_object = MessageHandler(event_dict_simple_message)
#         text_instance = TextParser(message_object)
#         cls.handler_object = RandomPostCommandHandler(text_instance, cls.chat_db_object)
#
#     def test_post_off_INFO(self):
#         expected_answer = f'Для команды /post у вас зарегистрирована группа {links.normal_group1}. Команда /post выключена.'
#         self.pipeline("info", False, expected_answer)
#
#     def test_post_on_INFO(self):
#         expected_answer = f'Для команды /post у вас зарегистрирована группа {links.normal_group1}. Команда /post включена.'
#         self.pipeline("info", True, expected_answer)
#
#     def test_post_off_OFF(self):
#         expected_answer = 'Команда /post выключена.'
#         self.pipeline("off", False, expected_answer)
#         self.db_check(False, links.normal_group1ID)
#
#     def test_post_on_OFF(self):
#         expected_answer = 'Команда /post выключена.'
#         self.pipeline("off", True, expected_answer)
#         self.db_check(False, links.normal_group1ID)
#
#     def test_post_on_ON(self):
#         expected_answer = f'Для команды /post у вас зарегистрирована группа {links.normal_group1}. Команда /post включена.'
#         self.pipeline("on", True, expected_answer)
#
#     def test_post_off_ON(self):
#         expected_answer = f'Для команды /post у вас зарегистрирована группа {links.normal_group1}. Команда /post включена.'
#         self.pipeline("on", False, expected_answer)
#         self.db_check(True, links.normal_group1ID)
