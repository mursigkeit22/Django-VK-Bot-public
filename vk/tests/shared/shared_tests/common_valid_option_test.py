import vk.tests.data_for_tests.group_links as links
from vk import models
from vk.helpers import option_info, option_off, option_on, option_group, option_delete
from vk.input_message import InputMessage
from vk.tests.data_for_tests.event_dicts import event_dict_simple_message
from vk.tests.data_for_tests.message_data import OwnerAndBotChatData
from vk.tests.shared.pipelines_and_setups import PipelinesAndSetUps
from vk.text_parser import TextParser
from vk.vkbot_exceptions import GroupValidationError, WrongOptionError
from vk.vkreceiver_message_handler import MessageHandler


class ValidOptionMixinTest(PipelinesAndSetUps):

    @classmethod
    def setup_with_setting_object(cls):
        cls.basic_setup()
        cls.input_message_object = InputMessage(event_dict_simple_message)

    def pipeline(self, wordlist: list):
        wordlist = [self.command] + wordlist
        self.handler_object = self.command_handler(wordlist, self.input_message_object, self.chat_db_object)
        self.handler_object.get_option()

    def test_option_info(self):
        self.pipeline([option_info])
        self.assertEqual(self.handler_object.option, option_info)

    def test_option_off(self):
        self.pipeline([option_off])
        self.assertEqual(self.handler_object.option, option_off)

    def test_option_group_ok(self):
        self.pipeline([option_group, links.normal_group2])
        self.assertEqual(self.handler_object.option, (links.normal_group2_screen_name, links.normal_group2ID))

    def test_option_group_error(self):
        bot_response = f'Группа {links.nonexisting_group} не может быть зарегистрирована для команды {self.command}.' \
                       ' Убедитесь, что ссылка правильная, и группа не является закрытой'
        with self.assertRaises(GroupValidationError) as context:
            self.pipeline([option_group, links.nonexisting_group])
            self.assertEqual('WRONG_GROUP', context.exception.error_code)
            self.assertEqual(bot_response, context.exception.bot_response)

    def test_option_on(self):
        self.pipeline([option_on])
        self.assertEqual(self.handler_object.option, option_on)

    def test_option_delete(self):
        self.pipeline([option_group, option_delete])
        self.assertEqual(self.handler_object.option, option_delete)

    def test_option_wrong(self):
        bot_response = f"У команды {self.command} нет опции 'asdf'."
        with self.assertRaises(WrongOptionError) as context:
            self.pipeline(["asdf"], )
        self.assertEqual('WRONG_OPTION', context.exception.error_code)
        self.assertEqual(bot_response, context.exception.bot_response)

    def test_option_wrong_delete(self):
        bot_response = f"Возможно, вы имели в виду команду '{self.command} {option_group} {option_delete}'?"
        with self.assertRaises(WrongOptionError) as context:
            self.pipeline([option_delete])
        self.assertEqual('WRONG_OPTION', context.exception.error_code)
        self.assertEqual(bot_response, context.exception.bot_response)

    def test_option_extra_word(self):
        self.pipeline([option_info, "asdft", ])
        self.assertEqual(self.handler_object.option, option_info)
