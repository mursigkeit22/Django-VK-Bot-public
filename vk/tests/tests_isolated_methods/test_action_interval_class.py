from django.test import TestCase

from vk import models
from vk.actions.IntervalAction import IntervalAction
from vk.tests.data_for_tests.message_data import OwnerAndBotChatData


class CounterTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True,
            interval=4, interval_mode=True, messages_till_endpoint=4)

    def pipeline(self, endpoint: int, new_endpoint: int):
        self.chat_db_object.messages_till_endpoint = endpoint
        self.chat_db_object.save()
        action_object = IntervalAction(self.chat_db_object)
        returned_answer = action_object.counter()
        self.assertEqual(returned_answer, new_endpoint)

    def test_endpoint_4(self):
        self.pipeline(4, 3)

    def test_endpoint_1(self):
        self.pipeline(1, 0)


class ProcessTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True,
            interval=4, interval_mode=True, messages_till_endpoint=4)
        models.IntervalPhrase.objects.create(chat_id=cls.chat_db_object, phrase="phrase1")

    def pipeline(self, count: int, expected_answer: str, endpoint: int):
        action_object = IntervalAction(self.chat_db_object)
        action_object.count = count
        returned_answer = action_object.process()
        self.assertEqual(returned_answer, expected_answer)
        self.chat_db_object.refresh_from_db()
        self.assertEqual(self.chat_db_object.messages_till_endpoint, endpoint)

    def test_count_0(self):
        self.pipeline(0, "IntervalAction. message was sent: phrase1", 4)

    def test_count_1(self):
        self.pipeline(1, "IntervalAction. Nothing will be sent.", 1)
