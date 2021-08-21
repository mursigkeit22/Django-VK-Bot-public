from django.test import TestCase

from vk import models
from vk.bot_answer import BotAnswer
from vk.input_message import InputMessage
from vk.tests.data_for_tests.message_data import OwnerAndBotChatData, input_data
from vk.tests.shared.pipelines_and_setups import PipelinesAndSetUps
from vk.vkreceiver_event_handler import EventHandler


class IntervalActionTest(TestCase, PipelinesAndSetUps):

    @classmethod
    def setUpTestData(cls):
        cls.setup_chat(True, interval=4, interval_mode=True, messages_till_endpoint=4)
        cls.create_settings_tables()

        models.IntervalPhrase.objects.create(chat_id=cls.chat_db_object, phrase="phrase1")
        models.IntervalPhrase.objects.create(chat_id=cls.chat_db_object, phrase="phrase2")
        models.IntervalPhrase.objects.create(chat_id=cls.chat_db_object, phrase="phrase3")

    def pipeline_process(self, from_id):
        text = "message"
        data = input_data(OwnerAndBotChatData.peer_id, text, from_id)
        event_object = EventHandler(data)
        self.input_message_object = InputMessage(event_object.event_dict)
        return EventHandler(data).process()

    def pipeline_check(self, from_id):
        returned_answer = self.pipeline_process(from_id)
        expected_answer = BotAnswer("INTERVAL_COUNTER", self.input_message_object)
        self.assertEqual(expected_answer, returned_answer)

    def test_one_time_owner(self):
        for i in range(3):
            self.pipeline_check(OwnerAndBotChatData.owner_id)

        returned_answer = self.pipeline_process(OwnerAndBotChatData.owner_id)
        self.assertEqual("INTERVAL_MESSAGE_SENT", returned_answer.event_code, )
        self.assertIsNotNone(returned_answer.bot_response)

    def test_one_time_different_people(self):
        self.pipeline_check(12345678)
        self.pipeline_check(77778888)
        self.pipeline_check(OwnerAndBotChatData.owner_id)

        returned_answer = self.pipeline_process(2222222)
        self.assertEqual("INTERVAL_MESSAGE_SENT", returned_answer.event_code, )
        self.assertIsNotNone(returned_answer.bot_response)

    def test_chain_owner(self):
        for j in range(3):
            self.test_one_time_owner()

    def test_chain_diff(self):
        for j in range(3):
            self.test_one_time_different_people()


class IntervalOnePhraseTest(IntervalActionTest):
    @classmethod
    def setUpTestData(cls):
        cls.setup_chat(True, interval=4, interval_mode=True, messages_till_endpoint=4)
        cls.create_settings_tables()

        models.IntervalPhrase.objects.create(chat_id=cls.chat_db_object, phrase="phrase1")

    def test_one_time_not_owner(self):
        for i in range(3):
            returned_answer = self.pipeline_process(12345678)
            expected_answer = BotAnswer("INTERVAL_COUNTER", self.input_message_object)
            self.assertEqual(expected_answer, returned_answer)

        returned_answer = self.pipeline_process(12345678)
        self.assertEqual("INTERVAL_MESSAGE_SENT", returned_answer.event_code, )
        self.assertEqual('phrase1', returned_answer.bot_response)

    def test_chain(self):
        for j in range(3):
            self.test_one_time_not_owner()
