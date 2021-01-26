import vk.tests.data_for_tests.group_links as links
from vk import models
from vk.tests.data_for_tests.event_dicts import event_dict_simple_message
from vk.tests.data_for_tests.message_data import OwnerAndBotChatData
from vk.text_parser import TextParser
from vk.vkreceiver_message_handler import MessageHandler


class ValidOptionMixinTest:

    def __init__(self, command, command_handler):
        self.command = command
        self.command_handler = command_handler

    @classmethod
    def setup(cls):
        chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True)
        message_handler_object = MessageHandler(event_dict_simple_message)
        text_instance = TextParser(message_handler_object)
        cls.handler_object = cls.command_handler(text_instance, chat_db_object)

    def pipeline(self, option: str, expected_answer: tuple):
        self.handler_object.wordlist = [f"{self.command}"] + option.split()
        returned_value = self.handler_object.valid_option()
        self.assertEqual(returned_value, expected_answer)

    def test_option_info(self):
        self.pipeline("info", (True, "info"))

    def test_option_off(self):
        self.pipeline("off", (True, "off"))

    def test_option_group_ok(self):
        self.pipeline(f"group {links.normal_group2}", (True, (links.normal_group2_screen_name, links.normal_group2ID)))

    def test_option_group_error(self):
        expected_value = (
            False, f'Группа {links.nonexisting_group} не может быть зарегистрирована для команды {self.command}.' \
                   ' Убедитесь, что ссылка правильная, и группа не является закрытой')
        self.pipeline(f"group {links.nonexisting_group}", expected_value)

    def test_option_on(self):
        self.pipeline("on", (True, "on"))

    def test_option_delete(self):
        self.pipeline("group delete", (True, "delete"))

    def test_option_wrong(self):
        expected_value = (
            False, f"У команды {self.command} нет опции 'asdf'.")
        self.pipeline("asdf", expected_value)

    def test_option_wrong_delete(self):
        expected_value = (
            False, f"Возможно, вы имели в виду команду '{self.command} group delete'?")
        self.pipeline("delete", expected_value)

    def test_option_extra_word(self):
        self.pipeline("info asdft", (True, "info"))
