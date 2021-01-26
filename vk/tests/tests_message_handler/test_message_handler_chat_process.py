import datetime

from django.test import TestCase
from django.utils import timezone

from vk import models, helpers
from vk.tests.data_for_tests.big_texts_for_tests import text_122_letters
from vk.tests.data_for_tests.event_dicts import event_dict_simple_message
from vk.tests.data_for_tests.message_data import OwnerAndBotChatData, input_data
from vk.vkreceiver_message_handler import MessageHandler


class IntervalAndSmartTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id,
            conversation_is_registered=True)
        models.IntervalPhrase.objects.create(chat_id=cls.chat_db_object, phrase="phrase1")
        cls.smart_reply = models.SmartReply.objects.create(chat_id=cls.chat_db_object, trigger="hello", reply="hello1")

    def pipiline(self, text, expected_answer):
        data = input_data(OwnerAndBotChatData.peer_id, text, OwnerAndBotChatData.owner_id)
        event_dict = helpers.parse_vk_object(data)
        returned_answer = MessageHandler(event_dict).process()
        self.assertEqual(expected_answer, returned_answer)

    def interval_db_settings(self, interval_mode=False, interval=4, messages_till_endpoint=3):
        self.chat_db_object.interval_mode = interval_mode
        self.chat_db_object.interval = interval
        self.chat_db_object.messages_till_endpoint = messages_till_endpoint
        self.chat_db_object.save()

    def smart_db_settings(self, mode=False, minutes=1):
        self.chat_db_object.smart_mode = mode
        self.chat_db_object.save()
        self.smart_reply.last_used = timezone.now() - datetime.timedelta(minutes=minutes)
        self.smart_reply.save()

    def test_only_interval_send(self):
        self.smart_db_settings()
        self.interval_db_settings(interval_mode=True, messages_till_endpoint=1)
        self.pipiline("just a message", " IntervalAction. message was sent: phrase1")

    def test_only_interval_not_send(self):
        self.smart_db_settings()
        self.interval_db_settings(interval_mode=True, messages_till_endpoint=2)
        self.pipiline("just a message", " IntervalAction. Nothing will be sent.")

    def test_only_smart_send(self):
        self.interval_db_settings()
        self.smart_db_settings(True, 6)
        self.pipiline("hello", "SmartReplyAction. Message was sent: 'hello1'. ")

    def test_only_smart_not_send(self):
        self.interval_db_settings()
        self.smart_db_settings(True, 1)
        self.pipiline("hello", "SmartReplyAction. 5 minutes break for trigger 'hello'. ")

    def test_both_off(self):
        self.interval_db_settings()
        self.smart_db_settings()
        self.pipiline("hello", "It was normal message. Nothing will be sent.")

    def test_both_not_send(self):
        self.interval_db_settings(True)
        self.smart_db_settings(True)
        self.pipiline("hello",
                      f"SmartReplyAction. 5 minutes break for trigger 'hello'. IntervalAction. Nothing will be sent.")

    def test_both_send(self):
        self.interval_db_settings(interval_mode=True, messages_till_endpoint=1)
        self.smart_db_settings(True, 6)
        self.pipiline("hello",
                      "SmartReplyAction. Message was sent: 'hello1'. IntervalAction. message was sent: phrase1")

    def test_interval_send_smart_not_send(self):
        self.interval_db_settings(interval_mode=True, messages_till_endpoint=1)
        self.smart_db_settings(True)
        self.pipiline("hello",
                      "SmartReplyAction. 5 minutes break for trigger 'hello'. IntervalAction. message was sent: phrase1")

    def test_smart_send_interval_not_send(self):
        self.interval_db_settings(interval_mode=True)
        self.smart_db_settings(True, 6)
        self.pipiline("hello", "SmartReplyAction. Message was sent: 'hello1'. IntervalAction. Nothing will be sent.")

    def test_too_long_not_interval(self):
        self.interval_db_settings()
        self.smart_db_settings(True)
        self.pipiline(f"{text_122_letters}", "Not a valid message length for SmartAction. Nothing will be sent. ")

    def test_too_long_interval_send(self):
        self.interval_db_settings(interval_mode=True, messages_till_endpoint=1)
        self.smart_db_settings(True)
        self.pipiline(f"{text_122_letters}",
                      "Not a valid message length for SmartAction. Nothing will be sent. IntervalAction. message was sent: phrase1")

    def test_too_long_interval_not_send(self):
        self.interval_db_settings(interval_mode=True, messages_till_endpoint=2)
        self.smart_db_settings(True)
        self.pipiline(f"{text_122_letters}",
                      "Not a valid message length for SmartAction. Nothing will be sent. IntervalAction. Nothing will be sent.")

    def test_empty_not_interval(self):
        self.interval_db_settings()
        self.smart_db_settings(True)
        self.pipiline("", "Not a valid message length for SmartAction. Nothing will be sent. ")

    def test_empty_interval_send(self):
        self.interval_db_settings(interval_mode=True, messages_till_endpoint=1)
        self.smart_db_settings(True)
        self.pipiline("",
                      "Not a valid message length for SmartAction. Nothing will be sent. IntervalAction. message was sent: phrase1")

    def test_empty_interval_not_send(self):
        self.interval_db_settings(interval_mode=True, messages_till_endpoint=2)
        self.smart_db_settings(True)
        self.pipiline("",
                      "Not a valid message length for SmartAction. Nothing will be sent. IntervalAction. Nothing will be sent.")


class MessageHandlerChatProcessTest(TestCase):

    def test_normal_message_no_reg(self):
        message_handler_object = MessageHandler(event_dict_simple_message)
        bot_answer = message_handler_object.chat_process()
        expected_answer = "Conversation isn't registered. Nothing will be sent."
        self.assertEqual(bot_answer, expected_answer)
