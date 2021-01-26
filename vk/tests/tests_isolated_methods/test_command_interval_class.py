from typing import Optional


from django.test import TestCase

from vk import models
from vk.command_handlers.IntervalCommandHandler import IntervalCommandHandler
from vk.tests.data_for_tests.event_dicts import event_dict_simple_message
from vk.tests.data_for_tests.message_data import OwnerAndBotChatData
from vk.text_parser import TextParser
from vk.vkreceiver_message_handler import MessageHandler


class ValidOptionTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True)
        message_handler_object = MessageHandler(event_dict_simple_message)
        text_instance = TextParser(message_handler_object)
        cls.handler_object = IntervalCommandHandler(text_instance, chat_db_object)

    def pipeline(self, option: str, expected_answer: tuple):
        self.handler_object.wordlist = ["/interval", option]
        returned_value = self.handler_object.valid_option()
        self.assertEqual(returned_value, expected_answer)

    def test_option_info(self):
        self.pipeline("info", (True, "info"))

    def test_option_off(self):
        self.pipeline("off", (True, "off"))

    def test_option_on(self):
        self.pipeline("on", (True, "on"))

    def test_option_delete(self):
        expected_value = (
            False, "У команды /interval нет опции 'delete'")
        self.pipeline("delete", expected_value)

    def test_option_wrong(self):
        expected_value = (
            False, f"У команды /interval нет опции 'asdf'")
        self.pipeline("asdf", expected_value)

    def test_option_good_integer(self):
        expected_value = (True, 4)
        self.pipeline("4", expected_value)

    def test_option_too_small_integer(self):
        expected_value = (False, "Интервал должен быть больше 2 и меньше 1000.")
        self.pipeline("2", expected_value)

    def test_option_too_big_integer(self):
        expected_value = (False, "Интервал должен быть больше 2 и меньше 1000.")
        self.pipeline("1000", expected_value)

    def test_option_minus_integer(self):
        expected_value = (False, "У команды /interval нет опции '-4'")
        self.pipeline("-4", expected_value)


class SharedMethods(TestCase):

    def pipeline(self, option: str, expected_answer: str):
        self.handler_object.option = option
        returned_answer = self.handler_object.command()
        self.assertEqual(returned_answer, expected_answer)

    @classmethod
    def set_up(cls):
        message_handler_object = MessageHandler(event_dict_simple_message)
        text_instance = TextParser(message_handler_object)
        cls.handler_object = IntervalCommandHandler(text_instance, cls.chat_db_object)

    def set_up_db(self, mode: bool, interval: Optional[int], endpoint: Optional[int]):
        models.IntervalPhrase.objects.create(chat_id=self.chat_db_object, phrase="phrase1")
        self.chat_db_object.interval = interval
        self.chat_db_object.interval_mode = mode
        self.chat_db_object.messages_till_endpoint = endpoint
        self.chat_db_object.save()


class CommandNoPhrasesNoIntervalTest(SharedMethods):
    @classmethod
    def setUpTestData(cls):
        cls.chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True)
        cls.set_up()

    def test_on(self):
        expected_answer = "Сначала установите интервал командой /interval, например '/interval 10'."
        self.pipeline("on", expected_answer)

    def test_off(self):
        expected_answer = 'Режим /interval уже выключен.'
        self.pipeline("off", expected_answer)

    def test_info(self):
        expected_answer = f"Режим /interval выключен. Настройки: интервал не установлен."
        self.pipeline("info", expected_answer)



class CommandThereArePhrasesNoIntervalTest(SharedMethods):
    @classmethod
    def setUpTestData(cls):
        cls.chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True)
        models.IntervalPhrase.objects.create(chat_id=cls.chat_db_object, phrase="phrase1")
        cls.set_up()

    def test_on(self):
        expected_answer = "Сначала установите интервал командой /interval, например '/interval 10'."
        self.pipeline("on", expected_answer)

    def test_off(self):
        expected_answer = 'Режим /interval уже выключен.'
        self.pipeline("off", expected_answer)

    def test_info(self):
        expected_answer = f"Режим /interval выключен. Настройки: интервал не установлен."
        self.pipeline("info", expected_answer)


class CommandThereArePhrasesThereIsIntervalTest(SharedMethods):

    @classmethod
    def setUpTestData(cls):
        cls.chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True,
            interval=4)
        models.IntervalPhrase.objects.create(chat_id=cls.chat_db_object, phrase="phrase1")
        cls.set_up()

    def test_info(self):
        expected_answer = f"Режим /interval выключен. Настройки: фраза бота через каждые 4 сообщений."
        self.pipeline("info", expected_answer)

    def test_off(self):
        expected_answer = 'Режим /interval уже выключен.'
        self.pipeline("off", expected_answer)


class CommandTurnOnOffSetInterval(SharedMethods):

    def check_db(self, mode: bool, interval: Optional[int], endpoint: Optional[int]):
        self.chat_db_object.refresh_from_db()
        self.assertEqual(self.chat_db_object.interval_mode, mode)
        self.assertEqual(self.chat_db_object.interval, interval)
        self.assertEqual(self.chat_db_object.messages_till_endpoint, endpoint)

    def setUp(self):
        self.chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True)
        message_handler_object = MessageHandler(event_dict_simple_message)
        text_instance = TextParser(message_handler_object)
        self.handler_object = IntervalCommandHandler(text_instance, self.chat_db_object)



    def test_no_phrases_interval(self):
        expected_answer = "Интервал между фразами установлен. Режим /interval выключен."
        self.pipeline("4", expected_answer)
        self.check_db(False, 4, None)

    def test_there_are_phrases_interval(self):
        models.IntervalPhrase.objects.create(chat_id=self.chat_db_object, phrase="phrase1")
        expected_answer = "Интервал между фразами установлен. Режим /interval выключен."
        self.pipeline("4", expected_answer)
        self.check_db(False, 4, None)

    def test_change_interval_while_on(self):
        self.set_up_db(True, 4, 2)
        expected_answer = f"Режим /interval включен, интервал между фразами 3"
        self.pipeline("3", expected_answer)
        self.check_db(True, 3, 3)

    def test_turn_off(self):
        self.set_up_db(True, 4, 2)
        expected_answer = 'Режим /interval выключен.'
        self.pipeline("off", expected_answer)
        self.check_db(False, None, None)

    def test_turn_on(self):
        self.set_up_db(False, 4, None)
        expected_answer = f"Режим /interval включен."
        self.pipeline("on", expected_answer)
        self.check_db(True, 4, 4)


class CommandIntervalOnTest(SharedMethods):
    @classmethod
    def setUpTestData(cls):
        cls.chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True,
            interval=4, interval_mode=True, messages_till_endpoint=2)
        models.IntervalPhrase.objects.create(chat_id=cls.chat_db_object, phrase="phrase1")
        cls.set_up()

    def test_on(self):
        expected_answer = f"Режим /interval уже включен, интервал между фразами 4, " \
                          f"следующую фразу бот отправит через 2 сообщений."
        self.pipeline("on", expected_answer)

    def test_info(self):
        expected_answer = f"Режим /interval включен, интервал между фразами 4, " \
                          f"следующую фразу бот отправит через 2 сообщений."
        self.pipeline("info", expected_answer)
