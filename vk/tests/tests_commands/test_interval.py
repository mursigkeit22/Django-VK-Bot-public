from typing import Optional

from django.test import TestCase

from vk import models
from vk.helpers import interval, interval_phrase, option_off, option_info, option_on
from vk.tests.shared.pipelines_and_setups import PipelinesAndSetUps
from vk.tests.shared.shared_tests.common_command_tests import CommonCommandMixin
from vk.tests.shared.shared_tests.user_specific_commands_test import UserSpecificCommandsMixinTest


class UserSpecificIntervalTest(TestCase, UserSpecificCommandsMixinTest, ):
    command = interval


class SharedMethods(TestCase, PipelinesAndSetUps):
    command = interval

    def check_db(self, mode: bool, interval: Optional[int], endpoint: Optional[int]):
        self.chat_db_object.refresh_from_db()
        self.assertEqual(self.chat_db_object.interval_mode, mode)
        self.assertEqual(self.chat_db_object.interval, interval)
        self.assertEqual(self.chat_db_object.messages_till_endpoint, endpoint)


class IntervalNoPhrasesNoIntervalTest(SharedMethods, CommonCommandMixin):  # 4+4
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_wrong_interval(self):
        bot_response = "Интервал должен быть больше 2 и меньше 1000."
        self.pipeline_user("4000", "LIMIT_ERROR", bot_response=bot_response)
        self.pipeline_chat_from_owner("4000", "LIMIT_ERROR", bot_response=bot_response)

    def test_on(self):
        bot_response = f"Сначала установите интервал командой {self.command}, например '{self.command} 10'."
        self.pipeline_user(option_on, "PREREQUISITES_ERROR", bot_response=bot_response)
        self.pipeline_chat_from_owner(option_on, "PREREQUISITES_ERROR", bot_response=bot_response)

    def test_off(self):
        bot_response = f'Режим {self.command} уже выключен.'
        self.pipeline_user(option_off, "ALREADY_DONE", bot_response=bot_response)
        self.pipeline_chat_from_owner(option_off, "ALREADY_DONE", bot_response=bot_response)

    def test_info(self):
        bot_response = f"Режим {self.command} выключен. Сохраненные настройки: интервал не установлен."
        self.pipeline_user(option_info, "INTERVAL_INFO", bot_response=bot_response)
        self.pipeline_chat_from_owner(option_info, "INTERVAL_INFO", bot_response=bot_response)


class IntervalNoPhrasesThereIsIntervalTest(SharedMethods):

    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()
        cls.chat_db_object.interval = 5
        cls.chat_db_object.save()

    def test_no_phrases_interval_on(self):
        bot_response = f"Сначала добавьте фразы командой {interval_phrase} add', после этого можно включить режим интервал."
        self.pipeline_user(option_on, "PREREQUISITES_ERROR", bot_response=bot_response)
        self.pipeline_chat_from_owner(option_on, "PREREQUISITES_ERROR", bot_response=bot_response)


class IntervalThereArePhrasesNoIntervalTest(SharedMethods):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()
        models.IntervalPhrase.objects.create(chat_id=cls.chat_db_object, phrase="phrase1")

    def test_on(self):
        bot_response = f"Сначала установите интервал командой {self.command}, например '{self.command} 10'."
        self.pipeline_user(option_on, "PREREQUISITES_ERROR", bot_response=bot_response)
        self.pipeline_chat_from_owner(option_on, "PREREQUISITES_ERROR", bot_response=bot_response)

    def test_off(self):
        bot_response = f'Режим {self.command} уже выключен.'
        self.pipeline_user(option_off, "ALREADY_DONE", bot_response=bot_response)
        self.pipeline_chat_from_owner(option_off, "ALREADY_DONE", bot_response=bot_response)

    def test_info(self):
        bot_response = f"Режим {self.command} выключен. Сохраненные настройки: интервал не установлен."
        self.pipeline_user(option_info, "INTERVAL_INFO", bot_response=bot_response)
        self.pipeline_chat_from_owner(option_info, "INTERVAL_INFO", bot_response=bot_response)


class IntervalThereArePhrasesThereIsIntervalTest(SharedMethods):

    @classmethod
    def setUpTestData(cls):
        cls.setup_chat(True, interval=4)
        cls.create_settings_tables()
        models.IntervalPhrase.objects.create(chat_id=cls.chat_db_object, phrase="phrase1")

    def test_info(self):
        bot_response = f"Режим {self.command} выключен. Сохраненные настройки: интервал между фразами бота - 4 сообщения."
        self.pipeline_user(option_info, "INTERVAL_INFO", bot_response=bot_response)
        self.pipeline_chat_from_owner(option_info, "INTERVAL_INFO", bot_response=bot_response)

    def test_off(self):
        bot_response = f'Режим {self.command} уже выключен.'
        self.pipeline_user(option_off, "ALREADY_DONE", bot_response=bot_response)
        self.pipeline_chat_from_owner(option_off, "ALREADY_DONE", bot_response=bot_response)


class IntervalIntervalOnTest(SharedMethods):

    @classmethod
    def setUpTestData(cls):
        cls.setup_chat(True, interval=4, interval_mode=True, messages_till_endpoint=2)
        cls.create_settings_tables()
        models.IntervalPhrase.objects.create(chat_id=cls.chat_db_object, phrase="phrase1")

    def test_on(self):
        bot_response = f"Режим {self.command} уже включен, интервал между фразами 4, " \
                       f"следующую фразу бот отправит через 2 сообщения."
        self.pipeline_user(option_on, "ALREADY_DONE", bot_response=bot_response)
        self.pipeline_chat_from_owner(option_on, "ALREADY_DONE", bot_response=bot_response)

    def test_info(self):
        bot_response = f"Режим {self.command} включен, интервал между фразами 4, " \
                       f"следующую фразу бот отправит через 2 сообщения."
        self.pipeline_user(option_info, "INTERVAL_INFO", bot_response=bot_response)
        self.pipeline_chat_from_owner(option_info, "INTERVAL_INFO", bot_response=bot_response)


class IntervalSetIntervalTest(SharedMethods):
    def setUp(self):
        self.basic_setup()

    def test_no_phrases_interval_user(self):
        bot_response = f"Интервал между фразами установлен. Режим {self.command} выключен."
        self.pipeline_user("4", "INTERVAL_SET", bot_response=bot_response)
        self.check_db(False, 4, None)

    def test_no_phrases_interval_chat(self):
        bot_response = f"Интервал между фразами установлен. Режим {self.command} выключен."
        self.pipeline_chat_from_owner("4", "INTERVAL_SET", bot_response=bot_response)
        self.check_db(False, 4, None)

    def test_there_are_phrases_interval_user(self):
        models.IntervalPhrase.objects.create(chat_id=self.chat_db_object, phrase="phrase1")
        bot_response = f"Интервал между фразами установлен. Режим {self.command} выключен."
        self.pipeline_user("4", "INTERVAL_SET", bot_response=bot_response)
        self.check_db(False, 4, None)

    def test_there_are_phrases_interval_chat(self):
        models.IntervalPhrase.objects.create(chat_id=self.chat_db_object, phrase="phrase1")
        bot_response = f"Интервал между фразами установлен. Режим {self.command} выключен."
        self.pipeline_chat_from_owner("4", "INTERVAL_SET", bot_response=bot_response)
        self.check_db(False, 4, None)


class IntervalTurnOnOffTest(SharedMethods):

    def setUp(self):
        self.basic_setup()

    def set_up_interval(self, mode: bool, interval: Optional[int], endpoint: Optional[int]):
        models.IntervalPhrase.objects.create(chat_id=self.chat_db_object, phrase="phrase1")
        self.chat_db_object.interval = interval
        self.chat_db_object.interval_mode = mode
        self.chat_db_object.messages_till_endpoint = endpoint
        self.chat_db_object.save()

    def test_change_interval_while_on_user(self):
        self.set_up_interval(True, 4, 2)
        bot_response = f"Режим {self.command} включен, интервал между фразами 3."
        self.pipeline_user("3", "INTERVAL_SET", bot_response=bot_response)
        self.check_db(True, 3, 3)

    def test_change_interval_while_on_chat(self):
        self.set_up_interval(True, 4, 2)
        bot_response = f"Режим {self.command} включен, интервал между фразами 3."
        self.pipeline_chat_from_owner("3", "INTERVAL_SET", bot_response=bot_response)
        self.check_db(True, 3, 3)

    def test_turn_off_user(self):
        self.set_up_interval(True, 4, 2)
        bot_response = f'Режим {self.command} выключен.'
        self.pipeline_user(option_off, "INTERVAL_OFF", bot_response=bot_response)
        self.check_db(False, None, None)

    def test_turn_off_chat(self):
        self.set_up_interval(True, 4, 2)
        bot_response = f'Режим {self.command} выключен.'
        self.pipeline_chat_from_owner(option_off, "INTERVAL_OFF", bot_response=bot_response)
        self.check_db(False, None, None)

    def test_turn_on_user(self):
        self.set_up_interval(False, 4, None)
        bot_response = f"Режим {self.command} включен."
        self.pipeline_user(option_on, "INTERVAL_ON", bot_response=bot_response)
        self.check_db(True, 4, 4)

    def test_turn_on_chat(self):
        self.set_up_interval(False, 4, None)
        bot_response = f"Режим {self.command} включен."
        self.pipeline_chat_from_owner(option_on, "INTERVAL_ON", bot_response=bot_response)
        self.check_db(True, 4, 4)
