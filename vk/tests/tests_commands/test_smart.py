import datetime

from django.test import TestCase, TransactionTestCase

from django.test import TestCase, TransactionTestCase
from django.utils import timezone

from vk import models, helpers
from vk.helpers import smart, option_info, option_add, option_off, option_on
from web_vk.constants import SMARTREPLY_MAX_COUNT
from vk.tests.data_for_tests.big_texts_for_tests import text_122_letters
from vk.tests.data_for_tests.message_data import OwnerAndBotChatData
from vk.tests.shared.pipelines_and_setups import PipelinesAndSetUps
from vk.tests.shared.shared_tests.common_command_tests import CommonCommandMixin
from vk.tests.shared.shared_tests.common_phrase_tests import RemoveNothingMixin, RemoveWhileOn, RemoveWhileOff
from vk.tests.shared.shared_tests.common_smart_test import InfoSmartReplyMixin
from vk.tests.shared.shared_tests.user_specific_commands_test import UserSpecificCommandsMixinTest
from vk.usertext import smart_dict


class SharedMethods(PipelinesAndSetUps):
    command = smart
    text_dict = smart_dict
    command_code = "SMART"

    def check_entries_id_left(self, ids_left: set):
        entries_from_db = models.SmartReply.objects.filter(chat_id=self.chat_db_object)
        ids_from_db = {entry.id for entry in entries_from_db}
        self.assertEqual(ids_from_db, ids_left)

    def check_no_entries_left(self):
        entries_from_db = models.SmartReply.objects.filter(chat_id=self.chat_db_object)
        self.assertEqual(len(entries_from_db), 0)

    def check_on_off(self, mode: bool):
        self.chat_db_object.refresh_from_db()
        self.assertEqual(self.chat_db_object.smart_mode, mode)


class UserSpecificSmartReplyTest(TestCase, SharedMethods, UserSpecificCommandsMixinTest):  # 6
    pass


class SmartReplyEmptyDBTest(TestCase, SharedMethods, CommonCommandMixin, RemoveNothingMixin):  # 4+2

    def setUp(self):
        self.basic_setup()


class InfoOFFSmartReplyTest(TransactionTestCase, SharedMethods, InfoSmartReplyMixin):  # 3+1
    reset_sequences = True
    state = "off"

    def setUp(self):
        self.basic_setup()

    def test_info_0_phrases(self):
        bot_response = self.text_dict["off"] + self.text_dict["saved_entries"].substitute(number=0)
        self.pipeline_chat_from_owner(option_info, f"{self.command_code}_INFO", bot_response=bot_response)
        self.pipeline_user(option_info, f"{self.command_code}_INFO", bot_response=bot_response)


class InfoONSmartReplyTest(TransactionTestCase, SharedMethods, InfoSmartReplyMixin):  # 3
    reset_sequences = True
    state = "on"

    def setUp(self):
        self.setup_chat(is_registered=True, smart_mode=True, )
        self.create_settings_tables()


class RemoveSmartOnTest(TransactionTestCase, SharedMethods, RemoveWhileOn):  # 10
    reset_sequences = True

    def setUp(self):
        self.setup_chat(is_registered=True, smart_mode=True, )
        self.create_settings_tables()
        models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger="hello", reply="hello1")
        models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger="hello", reply="hello2")
        models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger="hello", reply="hello3")


class RemoveSmartOffTest(TransactionTestCase, SharedMethods, RemoveWhileOff):  # 10
    reset_sequences = True

    def setUp(self):
        self.basic_setup()
        models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger="hello", reply="hello1")
        models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger="hello", reply="hello2")
        models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger="hello", reply="hello3")


class AddExtraSpacesSmartReply(TransactionTestCase, SharedMethods):  # 6
    """  all extra spaces and linebreaks are deleted before processing/saving to db"""
    reset_sequences = True

    def setUp(self):
        self.basic_setup()

    def test_extra_spaces_chat(self):
        text = f"{option_add} hello  murlo  purlo || hello"
        bot_response = self.text_dict["off"] + self.text_dict["saved_entries"].substitute(
            number=1) + 'ID: 1. Сообщение-триггер: hello murlo purlo . Smart-ответ: hello\n'
        self.pipeline_chat_from_owner(text, f"{self.command_code}_ADD_INFO", bot_response=bot_response)

    def test_extra_spaces_user(self):
        text = f"{option_add} hello  murlo  purlo || hello"
        bot_response = self.text_dict["off"] + self.text_dict["saved_entries"].substitute(
            number=1) + 'ID: 1. Сообщение-триггер: hello murlo purlo . Smart-ответ: hello\n'
        self.pipeline_user(text, f"{self.command_code}_ADD_INFO", bot_response=bot_response)

    def test_extra_spaces_line_break_chat(self):
        bot_response = self.text_dict["off"] + self.text_dict["saved_entries"].substitute(
            number=1) + 'ID: 1. Сообщение-триггер: hello murlo purlo . Smart-ответ: hello\n'
        text = f"{option_add} hello\nmurlo  purlo || hello"
        self.pipeline_chat_from_owner(text, f"{self.command_code}_ADD_INFO", bot_response=bot_response)

    def test_extra_spaces_line_break_user(self):
        bot_response = self.text_dict["off"] + self.text_dict["saved_entries"].substitute(
            number=1) + 'ID: 1. Сообщение-триггер: hello murlo purlo . Smart-ответ: hello\n'
        text = f"{option_add} hello\nmurlo  purlo || hello"
        self.pipeline_user(text, f"{self.command_code}_ADD_INFO", bot_response=bot_response)

    def test_extra_spaces_line_break2_chat(self):
        bot_response = self.text_dict["off"] + self.text_dict["saved_entries"].substitute(
            number=1) + 'ID: 1. Сообщение-триггер: hello murlo purlo . Smart-ответ: hello\n'
        text = f"{option_add} hello  \n  murlo  purlo\n || hello"
        self.pipeline_chat_from_owner(text, f"{self.command_code}_ADD_INFO", bot_response=bot_response)

    def test_extra_spaces_line_break2_user(self):
        bot_response = self.text_dict["off"] + self.text_dict["saved_entries"].substitute(
            number=1) + 'ID: 1. Сообщение-триггер: hello murlo purlo . Smart-ответ: hello\n'
        text = f"{option_add} hello  \n  murlo  purlo\n || hello"
        self.pipeline_user(text, f"{self.command_code}_ADD_INFO", bot_response=bot_response)


class AddGoodSmartReply(TransactionTestCase, SharedMethods):
    reset_sequences = True

    def setUp(self):
        self.basic_setup()

    def test_add_normal_first_chat(self):
        bot_response = self.text_dict["off"] + self.text_dict["saved_entries"].substitute(
            number=1) + 'ID: 1. Сообщение-триггер: hello . Smart-ответ: hello\n'
        text = f"{option_add} hello || hello"
        self.pipeline_chat_from_owner(text, f"{self.command_code}_ADD_INFO", bot_response=bot_response)

    def test_add_normal_first_chat_REGEX(self):
        bot_response = self.text_dict["off"] + self.text_dict["saved_entries"].substitute(
            number=1) + 'ID: 1. REGEX ' + r'Сообщение-триггер: \bкирил[ауе]?\b .' + ' Smart-ответ: hello\n'
        text = fr"{option_add} regex \bкирил[ауе]?\b || hello"
        self.pipeline_chat_from_owner(text, f"{self.command_code}_ADD_INFO", bot_response=bot_response)

    def test_add_normal_first_user(self):
        bot_response = self.text_dict["off"] + self.text_dict["saved_entries"].substitute(
            number=1) + 'ID: 1. Сообщение-триггер: hello . Smart-ответ: hello\n'
        text = f"{option_add} hello || hello"
        self.pipeline_user(text, f"{self.command_code}_ADD_INFO", bot_response=bot_response)

    def test_add_normal_first_user_REGEX(self):
        bot_response = self.text_dict["off"] + self.text_dict["saved_entries"].substitute(
            number=1) + 'ID: 1. REGEX ' + r'Сообщение-триггер: \bкирил[ауе]*? .' + ' Smart-ответ: hello\n'
        text = fr"{option_add} regex \bкирил[ауе]*? || hello"
        self.pipeline_user(text, f"{self.command_code}_ADD_INFO", bot_response=bot_response)

    def test_add_normal_second_chat(self):
        models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger="hello",
                                         reply="hello")

        bot_response = self.text_dict["off"] + self.text_dict["saved_entries"].substitute(
            number=2) + 'ID: 1. Сообщение-триггер: hello . Smart-ответ: hello\nID: 2. Сообщение-триггер: second message . Smart-ответ: second hello\n'

        text = f"{option_add} second message || second hello"
        self.pipeline_chat_from_owner(text, f"{self.command_code}_ADD_INFO", bot_response=bot_response)

    def test_add_normal_second_chat_REGEX(self):
        models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger="hello",
                                         reply="hello")

        bot_response = self.text_dict["off"] + self.text_dict["saved_entries"].substitute(
            number=2) + \
                       'ID: 1. Сообщение-триггер: hello . Smart-ответ: hello\n' \
                       f'ID: 2. REGEX ' + r'Сообщение-триггер: \bслов[оауе]? . ' + 'Smart-ответ: second hello\n'
        text = fr"{option_add} regex \bслов[оауе]? || second hello"
        self.pipeline_chat_from_owner(text, f"{self.command_code}_ADD_INFO", bot_response=bot_response)

    def test_add_normal_second_user(self):
        models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger="hello",
                                         reply="hello")

        bot_response = self.text_dict["off"] + self.text_dict["saved_entries"].substitute(
            number=2) + \
                       'ID: 1. Сообщение-триггер: hello . Smart-ответ: hello\n' \
                       'ID: 2. Сообщение-триггер: second message . Smart-ответ: second hello\n'
        text = f"{option_add} second message || second hello"
        self.pipeline_user(text, f"{self.command_code}_ADD_INFO", bot_response=bot_response)

    def test_add_normal_second_user_REGEX(self):
        models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger="hello",
                                         reply="hello")
        bot_response = self.text_dict["off"] + self.text_dict["saved_entries"].substitute(
            number=2) + \
                       'ID: 1. Сообщение-триггер: hello . Smart-ответ: hello\n' \
                       f'ID: 2. REGEX ' + r'Сообщение-триггер: \bслов[оауе]? . ' + 'Smart-ответ: second hello\n'
        text = fr"{option_add} regex \bслов[оауе]? || second hello"
        self.pipeline_user(text, f"{self.command_code}_ADD_INFO", bot_response=bot_response)

    def test_151_chat(self):
        phrase_model_list = [models.SmartReply(chat_id=self.chat_db_object, trigger="hello",
                                               reply="hello")] * SMARTREPLY_MAX_COUNT
        models.SmartReply.objects.bulk_create(phrase_model_list)
        bot_response = self.text_dict["too_many_entries"]
        text = f"{option_add} 151 message || 151 hello"
        self.pipeline_chat_from_owner(text, "LIMIT_ERROR", bot_response=bot_response)






class AddWrongSmartReplyText(TestCase, SharedMethods):

    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_add_extra_delimiter1(self):
        bot_response = self.text_dict["absent_or_wrong_add"]
        text = "add ||hello || hello"
        self.pipeline_chat_from_owner(text, "WRONG_OPTION", bot_response=bot_response)
        self.pipeline_user(text, "WRONG_OPTION", bot_response=bot_response)

    def test_add_extra_delimiter2(self):
        bot_response = self.text_dict["absent_or_wrong_add"]
        text = "add hello || hello ||"
        self.pipeline_chat_from_owner(text, "WRONG_OPTION", bot_response=bot_response)
        self.pipeline_user(text, "WRONG_OPTION", bot_response=bot_response)

    def test_add_extra_delimiter3(self):
        bot_response = self.text_dict["absent_or_wrong_add"]
        text = "add || hello || hello ||"
        self.pipeline_chat_from_owner(text, "WRONG_OPTION", bot_response=bot_response)
        self.pipeline_user(text, "WRONG_OPTION", bot_response=bot_response)

    def test_add_lack_delimetor(self):
        bot_response = self.text_dict["absent_or_wrong_add"]
        text = "add hello"
        self.pipeline_chat_from_owner(text, "WRONG_OPTION", bot_response=bot_response)
        self.pipeline_user(text, "WRONG_OPTION", bot_response=bot_response)

    def test_add_empty_trigger(self):
        bot_response = self.text_dict["empty_entry"]
        text = "add ||hello"
        self.pipeline_chat_from_owner(text, "LIMIT_ERROR", bot_response=bot_response)
        self.pipeline_user(text, "LIMIT_ERROR", bot_response=bot_response)

    def test_add_empty_reply(self):
        bot_response = self.text_dict["empty_entry"]
        text = "add incoming||"
        self.pipeline_chat_from_owner(text, "LIMIT_ERROR", bot_response=bot_response)
        self.pipeline_user(text, "LIMIT_ERROR", bot_response=bot_response)

    def test_separated_delimiter(self):
        bot_response = self.text_dict["absent_or_wrong_add"]
        text = "add incoming | | reply reply reply"
        self.pipeline_chat_from_owner(text, "WRONG_OPTION", bot_response=bot_response)
        self.pipeline_user(text, "WRONG_OPTION", bot_response=bot_response)

    def test_too_long_reply(self):
        bot_response = self.text_dict["too_long_entry"]
        text = f"add hello || {text_122_letters}"
        self.pipeline_chat_from_owner(text, "LIMIT_ERROR", bot_response=bot_response)
        self.pipeline_user(text, "LIMIT_ERROR", bot_response=bot_response)

    def test_too_long_trigger(self):
        bot_response = self.text_dict["too_long_entry"]
        text = f"add {text_122_letters} || hello"
        self.pipeline_chat_from_owner(text, "LIMIT_ERROR", bot_response=bot_response)
        self.pipeline_user(text, "LIMIT_ERROR", bot_response=bot_response)


class SmartOFFTest(TestCase, SharedMethods):
    def setUp(self):
        self.basic_setup()
        self.reply_object = models.SmartReply.objects.create(chat_id=self.chat_db_object,
                                                             trigger="trigger-message", reply="smart_reply")

    def test_no_entries_user(self):
        self.reply_object.delete()
        bot_response = self.text_dict["zero_entries"]
        self.pipeline_user(option_on, "PREREQUISITES_ERROR", bot_response=bot_response)
        self.check_on_off(False)

    def test_no_entries_chat(self):
        self.reply_object.delete()
        bot_response = self.text_dict["zero_entries"]
        self.pipeline_chat_from_owner(option_on, "PREREQUISITES_ERROR", bot_response=bot_response)
        self.check_on_off(False)

    def test_on_user(self):
        bot_response = self.text_dict["on"]
        self.pipeline_user(option_on, "SMART_ON", bot_response=bot_response)
        self.check_on_off(True)

    def test_already_off_user(self):
        bot_response = self.text_dict["already_off"]
        self.pipeline_user(option_off, "ALREADY_DONE", bot_response=bot_response)
        self.check_on_off(False)

    def test_on_chat(self):
        bot_response = self.text_dict["on"]
        self.pipeline_chat_from_owner(option_on, "SMART_ON", bot_response=bot_response)
        self.check_on_off(True)

    def test_already_off_chat(self):
        bot_response = self.text_dict["already_off"]
        self.pipeline_chat_from_owner(option_off, "ALREADY_DONE", bot_response=bot_response)
        self.check_on_off(False)


class SmartONTest(TestCase, SharedMethods):
    def setUp(self):
        self.setup_chat(is_registered=True, smart_mode=True, )
        self.create_settings_tables()
        self.reply_object = models.SmartReply.objects.create(chat_id=self.chat_db_object,
                                                             trigger="trigger-message", reply="smart_reply")

    def test_updated_last_used_field(self):
        reply_object1 = models.SmartReply.objects.create(chat_id=self.chat_db_object,
                                                         trigger="trigger-message1", reply="smart_reply1")
        reply_object2 = models.SmartReply.objects.create(chat_id=self.chat_db_object,
                                                         trigger="trigger-message2", reply="smart_reply2")

        bot_response = self.text_dict["off"]
        self.pipeline_chat_from_owner(option_off, "SMART_OFF", bot_response=bot_response)
        self.reply_object.refresh_from_db()
        reply_object1.refresh_from_db()
        reply_object2.refresh_from_db()
        expected_time = timezone.now() - datetime.timedelta(minutes=5)
        self.assertEqual(expected_time.replace(second=0, microsecond=0),
                         self.reply_object.last_used.replace(second=0, microsecond=0))
        self.assertEqual(expected_time.replace(second=0, microsecond=0),
                         reply_object1.last_used.replace(second=0, microsecond=0))
        self.assertEqual(expected_time.replace(second=0, microsecond=0),
                         reply_object2.last_used.replace(second=0, microsecond=0))

    def test_off_chat(self):
        bot_response = self.text_dict["off"]
        self.pipeline_chat_from_owner(option_off, "SMART_OFF", bot_response=bot_response)
        self.check_on_off(False)

    def test_off_user(self):
        bot_response = self.text_dict["off"]
        self.pipeline_user(option_off, "SMART_OFF", bot_response=bot_response)
        self.check_on_off(False)

    def test_already_on_user(self):
        bot_response = self.text_dict["already_on"]
        self.pipeline_user(option_on, "ALREADY_DONE", bot_response=bot_response)
        self.check_on_off(True)

    def test_already_on_chat(self):
        bot_response = self.text_dict["already_on"]
        self.pipeline_chat_from_owner(option_on, "ALREADY_DONE", bot_response=bot_response)
        self.check_on_off(True)
