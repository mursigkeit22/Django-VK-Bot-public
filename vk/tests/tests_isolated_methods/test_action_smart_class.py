import datetime

from django.test import TestCase
from django.utils import timezone

from vk import models
from vk.actions.SmartAction import SmartAction
from vk.tests.data_for_tests.event_dicts import event_dict_simple_message
from vk.tests.data_for_tests.message_data import OwnerAndBotChatData
from vk.vkreceiver_message_handler import MessageHandler


class ProcessTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True,
            smart_mode=True)

    def pipeline(self, text, expected_answer):
        message_handler_object = MessageHandler(event_dict_simple_message)
        from_id = message_handler_object.from_id
        action_object = SmartAction(self.chat_db_object, text, from_id)
        returned_answer = action_object.process()
        self.assertEqual(returned_answer, expected_answer)

    def test_no_trigger(self):
        models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger="hello",
                                         reply="hello")
        expected_answer = "No such trigger. Nothing will be sent."
        self.pipeline("no hello", expected_answer)

    def test_reply(self):
        time = timezone.now() - datetime.timedelta(minutes=6)
        models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger="hello",
                                         reply="hello", last_used=time)
        expected_answer = "SmartReplyAction. Message was sent: 'hello'."
        self.pipeline("hello", expected_answer)

    def test_reply_then_cooldown(self):
        time = timezone.now() - datetime.timedelta(minutes=6)
        models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger="hello",
                                         reply="hello", last_used=time)
        expected_answer = "SmartReplyAction. Message was sent: 'hello'."
        self.pipeline("hello", expected_answer)
        expected_answer = "SmartReplyAction. 5 minutes break for trigger 'hello'."
        self.pipeline("hello", expected_answer)

    def test_3_smarts_one_ok(self):
        time_good = timezone.now() - datetime.timedelta(minutes=6)
        time_early1 = timezone.now() - datetime.timedelta(minutes=3)
        time_early2 = timezone.now() - datetime.timedelta(minutes=1)

        models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger="hello",
                                         reply="hello_early1", last_used=time_early1)
        models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger="hello",
                                         reply="hello_early2", last_used=time_early2)
        models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger="hello",
                                         reply="hello good", last_used=time_good)
        expected_answer = "SmartReplyAction. Message was sent: 'hello good'."
        self.pipeline("hello", expected_answer)

    def test_3_smarts_cooldown(self):
        time_good = timezone.now() - datetime.timedelta(minutes=4)
        time_early1 = timezone.now() - datetime.timedelta(minutes=3)
        time_early2 = timezone.now() - datetime.timedelta(minutes=1)

        models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger="hello",
                                         reply="hello_early1", last_used=time_early1)
        models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger="hello",
                                         reply="hello_early2", last_used=time_early2)
        models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger="hello",
                                         reply="hello good", last_used=time_good)
        expected_answer = "SmartReplyAction. 5 minutes break for trigger 'hello'."
        self.pipeline("Hello", expected_answer)
