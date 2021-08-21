import datetime
from time import sleep

from django.test import TestCase
from django.utils import timezone

from vk import models
from vk.actions.SmartAction import SmartAction
from vk.tests.shared.pipelines_and_setups import PipelinesAndSetUps
from vk.usertext import actions_dict


class SharedMethods(TestCase, PipelinesAndSetUps):
    @classmethod
    def setUpTestData(cls):
        cls.setup_chat(True, smart_mode=True)
        cls.create_settings_tables()
        cls.prepare_smart_replies()

    def prepare_smart_action(self, text):
        message_instance = self.create_input_message_instance(text)
        action_object = SmartAction(self.chat_db_object, message_instance)
        return action_object

    def pipeline_process(self, text, expected_code, expected_reply):
        action_object = self.prepare_smart_action(text)
        returned_answer = action_object.process()
        self.assertEqual(expected_code, returned_answer.event_code)
        self.assertEqual(expected_reply, returned_answer.bot_response)

    @classmethod
    def prepare_smart_replies(cls):
        time_4 = timezone.now() - datetime.timedelta(minutes=4)
        time_3 = timezone.now() - datetime.timedelta(minutes=3)
        time_1 = timezone.now() - datetime.timedelta(minutes=1)
        models.SmartReply.objects.create(chat_id=cls.chat_db_object, trigger=r'\bкирил[ауе]?\b',
                                         reply="кирил без звездочки 4 минуты назад", last_used=time_4, regex=True)
        models.SmartReply.objects.create(chat_id=cls.chat_db_object, trigger=r'\bкирил[ауе]*?',
                                         reply="кирил со звездочкой 3 минуты назад", last_used=time_3, regex=True)
        models.SmartReply.objects.create(chat_id=cls.chat_db_object, trigger=r'\bкирил',
                                         reply="кирил начало строки минуту назад", last_used=time_1, regex=True)
        models.SmartReply.objects.create(chat_id=cls.chat_db_object, trigger="hello",
                                         reply="hello 4 минуты назад regex", last_used=time_4, regex=True)
        models.SmartReply.objects.create(chat_id=cls.chat_db_object, trigger="hello",
                                         reply="hello 3 минуты назад regex", last_used=time_3, regex=True)
        models.SmartReply.objects.create(chat_id=cls.chat_db_object, trigger="hello",
                                         reply="hello 4 минуты назад fullmatch", last_used=time_4, )
        models.SmartReply.objects.create(chat_id=cls.chat_db_object, trigger="hello",
                                         reply="hello 3 минуты назад fullmatch", last_used=time_3, )
        models.SmartReply.objects.create(chat_id=cls.chat_db_object, trigger="hello",
                                         reply="hello 1 минута назад fullmatch", last_used=time_1)
        models.SmartReply.objects.create(chat_id=cls.chat_db_object, trigger="hello",
                                         reply="hello 5 минут назад fullmatch", )


class ProcessTest(SharedMethods):

    def test_no_trigger(self):
        self.pipeline_process("good bye", "SMART_NOT_TRIGGER", None)

    def test_reply(self):
        self.pipeline_process("hello", "SMART_REPLY_SENT", "hello 5 минут назад fullmatch")

    def test_3_smarts_just_created(self):
        models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger="hello",
                                         reply="hello created first", )
        sleep(0.1)
        models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger="hello",
                                         reply="hello created second", )
        sleep(0.1)
        models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger="hello",
                                         reply="hello created third", )

        self.pipeline_process("hello", "SMART_REPLY_SENT", "hello 5 минут назад fullmatch")

        self.pipeline_process("hello", "SMART_REPLY_SENT", "hello created first")

        self.pipeline_process("hello", "SMART_REPLY_SENT", "hello created second")

        self.pipeline_process("hello", "SMART_REPLY_SENT", "hello created third")

    def test_3_smarts_different_time(self):
        self.pipeline_process("hello", "SMART_REPLY_SENT", "hello 5 минут назад fullmatch")
        self.pipeline_process("hello", "SMART_REPLY_SENT", "hello 4 минуты назад fullmatch")
        self.pipeline_process("hello", "SMART_REPLY_SENT", "hello 3 минуты назад fullmatch")


class ChooseReplyTest(SharedMethods):

    def test_full_match_choose_oldest(self):
        action_object = self.prepare_smart_action('hello')
        returned_answer = action_object.choose_reply()
        self.assertEqual(returned_answer.reply, 'hello 5 минут назад fullmatch')

    def test_regex_match_choose_oldest(self):
        action_object = self.prepare_smart_action('кирил')
        returned_answer = action_object.choose_reply()
        self.assertEqual(returned_answer.reply, 'кирил без звездочки 4 минуты назад')


class ChooseReplyRegexText(SharedMethods):
    """ понял не понял"""

    # r'\bкирил[ауе]*?'

    def test_1(self):
        models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger=r"\bслов[оауе]",
                                         reply="got it1", regex=True, )
        reply_text = "got it1"
        self.pipeline_process("слово", "SMART_REPLY_SENT", reply_text)
        self.pipeline_process("словоохотливый", "SMART_REPLY_SENT", reply_text)
        self.pipeline_process("словам", "SMART_REPLY_SENT", reply_text)
        self.pipeline_process("слов", "SMART_NOT_TRIGGER", None)
        self.pipeline_process("словлю", "SMART_NOT_TRIGGER", None)
        self.pipeline_process("пустослов", "SMART_NOT_TRIGGER", None)

    def test_2(self):
        models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger=r"\bслов[оауе]\b",
                                         reply="got it2", regex=True, )
        reply_text = "got it2"
        self.pipeline_process("слово", "SMART_REPLY_SENT", reply_text)

        self.pipeline_process("словоохотливый", "SMART_NOT_TRIGGER", None)
        self.pipeline_process("слов", "SMART_NOT_TRIGGER", None)
        self.pipeline_process("словам", "SMART_NOT_TRIGGER", None)
        self.pipeline_process("словлю", "SMART_NOT_TRIGGER", None)
        self.pipeline_process("пустослов", "SMART_NOT_TRIGGER", None)

    def test_3(self):
        models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger=r"\bслов[оауе]*\b",
                                         reply="got it3", regex=True, )
        reply_text = "got it3"

        self.pipeline_process("слово", "SMART_REPLY_SENT", reply_text)
        self.pipeline_process("словооо", "SMART_REPLY_SENT", reply_text)
        self.pipeline_process("словоае", "SMART_REPLY_SENT", reply_text)
        self.pipeline_process("слов", "SMART_REPLY_SENT", reply_text)

        self.pipeline_process("словоохотливый", "SMART_NOT_TRIGGER", None)
        self.pipeline_process("словлю", "SMART_NOT_TRIGGER", None)
        self.pipeline_process("пустослов", "SMART_NOT_TRIGGER", None)
        self.pipeline_process("словам", "SMART_NOT_TRIGGER", None)

    def test_4(self):
        models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger="кирил",
                                         reply="got it4", regex=True, )
        reply_text = "got it4"
        self.pipeline_process("кирил", "SMART_REPLY_SENT", reply_text)
