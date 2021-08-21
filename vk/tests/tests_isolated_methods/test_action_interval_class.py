from django.test import TestCase

from vk import models
from vk.actions.IntervalAction import IntervalAction
from vk.tests.data_for_tests.message_data import OwnerAndBotChatData
from vk.tests.shared.pipelines_and_setups import PipelinesAndSetUps


class CounterTest(TestCase, PipelinesAndSetUps):

    @classmethod
    def setUpTestData(cls):
        cls.setup_chat(True, interval=4, interval_mode=True, messages_till_endpoint=4)
        cls.create_settings_tables()
        models.IntervalPhrase.objects.create(chat_id=cls.chat_db_object, phrase="phrase1")

    def pipeline_endpoint(self, endpoint: int, new_endpoint: int):
        self.chat_db_object.messages_till_endpoint = endpoint
        self.chat_db_object.save()
        message_instance = self.create_input_message_instance('just text')
        action_object = IntervalAction(self.chat_db_object, message_instance)
        returned_answer = action_object.counter()
        self.assertEqual(returned_answer, new_endpoint)

    def test_endpoint_4(self):
        self.pipeline_endpoint(4, 3)

    def test_endpoint_1(self):
        self.pipeline_endpoint(1, 0)


class ProcessTest(CounterTest, TestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()


    def pipeline_(self, count: int, code: str, bot_response, endpoint: int):
        message_instance = self.create_input_message_instance('just text')
        action_object = IntervalAction(self.chat_db_object, message_instance)
        action_object.count = count
        returned_answer = action_object.process()
        self.assertEqual(returned_answer.event_code, code)
        self.assertEqual(returned_answer.bot_response, bot_response)
        self.chat_db_object.refresh_from_db()
        self.assertEqual(self.chat_db_object.messages_till_endpoint, endpoint)

    def test_count_0(self):
        self.pipeline_(0, "INTERVAL_MESSAGE_SENT", 'phrase1', 4)

    def test_count_1(self):
        self.pipeline_(1, "INTERVAL_COUNTER", None, 1)
