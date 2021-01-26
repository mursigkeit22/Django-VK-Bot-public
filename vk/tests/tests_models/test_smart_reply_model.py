import datetime
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from vk import models
from vk.tests.data_for_tests.message_data import OwnerAndBotChatData


class SmartReplyModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True)

    def test_last_used_is_none(self):
        with self.assertRaises(IntegrityError):
            models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger="hello",
                                             reply="hello", last_used=None)

    def test_last_used_empty(self):
        timezone.now() - datetime.timedelta(minutes=5)
        reply_object = models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger="hello",
                                                        reply="hello")
        reply_object.refresh_from_db()
        expected_time = timezone.now() - datetime.timedelta(minutes=5)
        self.assertEqual(expected_time.replace(second=0, microsecond=0),
                         reply_object.last_used.replace(second=0, microsecond=0))

    def test_last_used_filled(self):
        reply_object = models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger="hello",
                                                        reply="hello", last_used=timezone.now())
        reply_object.refresh_from_db()
        self.assertEqual(timezone.now().replace(second=0, microsecond=0),
                         reply_object.last_used.replace(second=0, microsecond=0))

    def test_update_last_used_field(self):
        reply_object = models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger="hello",
                                                        reply="hello")
        reply_object.refresh_from_db()
        reply_object.last_used = timezone.now()
        reply_object.save()
        reply_object.refresh_from_db()
        self.assertEqual(timezone.now().replace(second=0, microsecond=0),
                         reply_object.last_used.replace(second=0, microsecond=0))

    def test_update_other_field(self):
        reply_object = models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger="hello",
                                                        reply="hello")
        reply_object.refresh_from_db()
        reply_object.reply = "updated hello"
        reply_object.save()
        reply_object.refresh_from_db()
        expected_time = timezone.now() - datetime.timedelta(minutes=5)
        self.assertEqual(expected_time.replace(second=0, microsecond=0),
                         reply_object.last_used.replace(second=0, microsecond=0))
