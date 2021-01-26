

from django.test import TestCase

from vk import models
from vk.tests.data_for_tests.message_data import OwnerAndBotChatData, input_data
from vk.vkreceiver_event_handler import EventHandler


class IntervalActionTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True,
            interval=4, interval_mode=True, messages_till_endpoint=4)
        models.IntervalPhrase.objects.create(chat_id=cls.chat_db_object, phrase="phrase1")
        models.IntervalPhrase.objects.create(chat_id=cls.chat_db_object, phrase="phrase2")
        models.IntervalPhrase.objects.create(chat_id=cls.chat_db_object, phrase="phrase3")

    def pipeline_send(self):
        text = "message"
        data = input_data(OwnerAndBotChatData.peer_id, text, OwnerAndBotChatData.owner_id)
        return EventHandler(data).process()

    def test_one_time(self):
        for i in range(3):
            returned_answer = self.pipeline_send()
            self.assertEqual(returned_answer, " IntervalAction. Nothing will be sent.")
        returned_answer = self.pipeline_send()
        self.assertEqual(returned_answer[:34], " IntervalAction. message was sent:")

    def test_chain(self):
        for j in range(3):
            self.test_one_time()
