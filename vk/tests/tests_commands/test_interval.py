from typing import Optional

from django.test import TestCase

from vk import models
from vk.tests.shared.pipelines_and_setups import PipelinesAndSetUps
from vk.tests.shared.shared_tests.user_specific_commands_test import UserSpecificCommandsMixinTest

from vk.tests.data_for_tests.message_data import OwnerAndBotChatData


class UserSpecificIntervalTest(TestCase, UserSpecificCommandsMixinTest):
    command = "/interval"


class SharedMethods(TestCase, PipelinesAndSetUps):
    command = "/interval"

    def check_db(self, mode: bool, interval: Optional[int], endpoint: Optional[int]):
        self.chat_db_object.refresh_from_db()
        self.assertEqual(self.chat_db_object.interval_mode, mode)
        self.assertEqual(self.chat_db_object.interval, interval)
        self.assertEqual(self.chat_db_object.messages_till_endpoint, endpoint)


class IntervalNoPhrasesNoIntervalTest(SharedMethods):
    @classmethod
    def setUpTestData(cls):
        cls.chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True)

    def test_on(self):
        expected_answer = "Сначала установите интервал командой /interval, например '/interval 10'."
        self.pipeline_user("on", expected_answer)
        self.pipeline_chat_from_owner("on", expected_answer)

    def test_off(self):
        expected_answer = 'Режим /interval уже выключен.'
        self.pipeline_user("off", expected_answer)
        self.pipeline_chat_from_owner("off", expected_answer)

    def test_info(self):
        expected_answer = f"Режим /interval выключен. Настройки: интервал не установлен."
        self.pipeline_user("info", expected_answer)
        self.pipeline_chat_from_owner("info", expected_answer)

    def test_not_owner(self):
        expected_answer = 'Только владелец беседы может использовать эту команду.'
        self.pipeline_chat_not_owner("info", expected_answer)

    def test_wrong_option(self):
        expected_answer = "У команды /interval нет опции 'asdfg'"
        self.pipeline_chat_from_owner("asdfg", expected_answer)

    def test_without_option(self):
        expected_answer = "Пожалуйста, уточните опцию."
        self.pipeline_chat_from_owner("", expected_answer)


class IntervalThereArePhrasesNoIntervalTest(SharedMethods):
    @classmethod
    def setUpTestData(cls):
        cls.chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True)
        models.IntervalPhrase.objects.create(chat_id=cls.chat_db_object, phrase="phrase1")

    def test_on(self):
        expected_answer = "Сначала установите интервал командой /interval, например '/interval 10'."
        self.pipeline_user("on", expected_answer)
        self.pipeline_chat_from_owner("on", expected_answer)

    def test_off(self):
        expected_answer = 'Режим /interval уже выключен.'
        self.pipeline_user("off", expected_answer)
        self.pipeline_chat_from_owner("off", expected_answer)

    def test_info(self):
        expected_answer = f"Режим /interval выключен. Настройки: интервал не установлен."
        self.pipeline_user("info", expected_answer)
        self.pipeline_chat_from_owner("info", expected_answer)


class IntervalThereArePhrasesThereIsIntervalTest(SharedMethods):

    @classmethod
    def setUpTestData(cls):
        cls.chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True,
            interval=4)
        models.IntervalPhrase.objects.create(chat_id=cls.chat_db_object, phrase="phrase1")

    def test_info(self):
        expected_answer = f"Режим /interval выключен. Настройки: фраза бота через каждые 4 сообщений."
        self.pipeline_user("info", expected_answer)
        self.pipeline_chat_from_owner("info", expected_answer)

    def test_off(self):
        expected_answer = 'Режим /interval уже выключен.'
        self.pipeline_user("off", expected_answer)
        self.pipeline_chat_from_owner("off", expected_answer)


class IntervalIntervalOnTest(SharedMethods):

    @classmethod
    def setUpTestData(cls):
        cls.chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True,
            interval=4, interval_mode=True, messages_till_endpoint=2)
        models.IntervalPhrase.objects.create(chat_id=cls.chat_db_object, phrase="phrase1")

    def test_on(self):
        expected_answer = f"Режим /interval уже включен, интервал между фразами 4, " \
                          f"следующую фразу бот отправит через 2 сообщений."
        self.pipeline_user("on", expected_answer)
        self.pipeline_chat_from_owner("on", expected_answer)

    def test_info(self):
        expected_answer = f"Режим /interval включен, интервал между фразами 4, " \
                          f"следующую фразу бот отправит через 2 сообщений."
        self.pipeline_user("info", expected_answer)
        self.pipeline_chat_from_owner("info", expected_answer)


class CommandTurnOnOffSetInterval(SharedMethods):

    def setUp(self):
        self.chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True)

    def set_up(self, mode: bool, interval: Optional[int], endpoint: Optional[int]):
        models.IntervalPhrase.objects.create(chat_id=self.chat_db_object, phrase="phrase1")
        self.chat_db_object.interval = interval
        self.chat_db_object.interval_mode = mode
        self.chat_db_object.messages_till_endpoint = endpoint
        self.chat_db_object.save()

    def test_no_phrases_interval_user(self):
        expected_answer = "Интервал между фразами установлен. Режим /interval выключен."
        self.pipeline_user("4", expected_answer)
        self.check_db(False, 4, None)

    def test_no_phrases_interval_chat(self):
        expected_answer = "Интервал между фразами установлен. Режим /interval выключен."
        self.pipeline_chat_from_owner("4", expected_answer)
        self.check_db(False, 4, None)

    def test_there_are_phrases_interval_user(self):
        models.IntervalPhrase.objects.create(chat_id=self.chat_db_object, phrase="phrase1")
        expected_answer = "Интервал между фразами установлен. Режим /interval выключен."
        self.pipeline_user("4", expected_answer)
        self.check_db(False, 4, None)

    def test_there_are_phrases_interval_chat(self):
        models.IntervalPhrase.objects.create(chat_id=self.chat_db_object, phrase="phrase1")
        expected_answer = "Интервал между фразами установлен. Режим /interval выключен."
        self.pipeline_chat_from_owner("4", expected_answer)
        self.check_db(False, 4, None)

    def test_change_interval_while_on_user(self):
        self.set_up(True, 4, 2)
        expected_answer = f"Режим /interval включен, интервал между фразами 3"
        self.pipeline_user("3", expected_answer)
        self.check_db(True, 3, 3)

    def test_change_interval_while_on_chat(self):
        self.set_up(True, 4, 2)
        expected_answer = f"Режим /interval включен, интервал между фразами 3"
        self.pipeline_chat_from_owner("3", expected_answer)
        self.check_db(True, 3, 3)

    def test_turn_off_user(self):
        self.set_up(True, 4, 2)
        expected_answer = 'Режим /interval выключен.'
        self.pipeline_user("off", expected_answer)
        self.check_db(False, None, None)

    def test_turn_off_chat(self):
        self.set_up(True, 4, 2)
        expected_answer = 'Режим /interval выключен.'
        self.pipeline_chat_from_owner("off", expected_answer)
        self.check_db(False, None, None)

    def test_turn_on_user(self):
        self.set_up(False, 4, None)
        expected_answer = f"Режим /interval включен."
        self.pipeline_user("on", expected_answer)
        self.check_db(True, 4, 4)

    def test_turn_on_chat(self):
        self.set_up(False, 4, None)
        expected_answer = f"Режим /interval включен."
        self.pipeline_chat_from_owner("on", expected_answer)
        self.check_db(True, 4, 4)
