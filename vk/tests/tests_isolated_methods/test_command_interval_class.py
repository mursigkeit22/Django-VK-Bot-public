from django.test import TestCase

from vk.command_handlers.IntervalCommandHandler import IntervalCommandHandler
from vk.helpers import interval, option_info, option_off, option_on, option_delete
from vk.input_message import InputMessage
from vk.tests.data_for_tests.event_dicts import event_dict_simple_message
from vk.tests.shared.pipelines_and_setups import PipelinesAndSetUps
from vk.vkbot_exceptions import WrongOptionError, LimitError


class ValidOptionTest(TestCase, PipelinesAndSetUps):
    command = interval

    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()
        cls.input_message_object = InputMessage(event_dict_simple_message)

    def pipeline(self, option: str, ):
        wordlist = [{self.command}, option]
        self.handler_object = IntervalCommandHandler(wordlist, self.input_message_object, self.chat_db_object)
        self.handler_object.get_option()

    def test_option_info(self):
        self.pipeline(option_info)
        self.assertEqual(self.handler_object.option, option_info)

    def test_option_off(self):
        self.pipeline(option_off)
        self.assertEqual(self.handler_object.option, option_off)

    def test_option_on(self):
        self.pipeline(option_on)
        self.assertEqual(self.handler_object.option, option_on)

    def test_option_delete(self):
        with self.assertRaises(WrongOptionError) as context:
            self.pipeline(option_delete)
        self.assertEqual('WRONG_OPTION', context.exception.error_code)
        self.assertEqual(f"У команды {self.command} нет опции '{option_delete}'.", context.exception.bot_response)

    def test_option_wrong(self):
        with self.assertRaises(WrongOptionError) as context:
            self.pipeline("asdf")
        self.assertEqual('WRONG_OPTION', context.exception.error_code)
        self.assertEqual(f"У команды {self.command} нет опции 'asdf'.", context.exception.bot_response)

    def test_option_good_integer(self):
        self.pipeline("4")
        self.assertEqual(self.handler_object.option, 4)

    def test_option_too_small_integer(self):
        with self.assertRaises(LimitError) as context:
            self.pipeline("2")
        self.assertEqual('LIMIT_ERROR', context.exception.error_code)
        self.assertEqual("Интервал должен быть больше 2 и меньше 1000.", context.exception.bot_response)

    def test_option_too_big_integer(self):
        with self.assertRaises(LimitError) as context:
            self.pipeline("1000")
        self.assertEqual('LIMIT_ERROR', context.exception.error_code)
        self.assertEqual("Интервал должен быть больше 2 и меньше 1000.", context.exception.bot_response)

    def test_option_minus_integer(self):
        with self.assertRaises(WrongOptionError) as context:
            self.pipeline("-4")
        self.assertEqual('WRONG_OPTION', context.exception.error_code)
        self.assertEqual(f"У команды {self.command} нет опции '-4'.", context.exception.bot_response)
