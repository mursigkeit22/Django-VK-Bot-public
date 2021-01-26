import datetime

from django.test import TestCase
from django.utils import timezone

from vk import models
from vk.helpers import smart, smart_reply, five_minutes_ago
from vk.tests.data_for_tests.message_data import OwnerAndBotChatData
from vk.tests.shared.pipelines_and_setups import PipelinesAndSetUps
from vk.tests.shared.shared_tests.user_specific_commands_test import UserSpecificCommandsMixinTest


class UserSpecificIntervalTest(TestCase, UserSpecificCommandsMixinTest):
    command = "/smart"


class SharedMethods(TestCase, PipelinesAndSetUps):
    command = "/smart"

    def check_db(self, mode):
        self.chat_db_object.refresh_from_db()
        self.assertEqual(self.chat_db_object.smart_mode, mode)


class SmartModeOFFNoRepliesTest(SharedMethods):

    @classmethod
    def setUpTestData(cls):
        cls.chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True)

    def test_on(self):
        expected_answer = f"Сначала добавьте smart-сообщения командой {smart_reply} add, после этого можно включить режим {smart[1:]}."
        self.pipeline_user("on", expected_answer)
        self.pipeline_chat_from_owner("on", expected_answer)

    def test_off(self):
        expected_answer = f'Режим {smart} уже выключен.'
        self.pipeline_user("off", expected_answer)
        self.pipeline_chat_from_owner("off", expected_answer)

    def test_info(self):
        expected_answer = f'Режим {smart} выключен.'
        self.pipeline_user("info", expected_answer)
        self.pipeline_chat_from_owner("info", expected_answer)


class SmartModeONTest(SharedMethods):

    @classmethod
    def setUpTestData(cls):
        cls.chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True, smart_mode=True)
        models.SmartReply.objects.create(chat_id=cls.chat_db_object, trigger="trigger-message",
                                         reply="smart_reply")

    def test_on(self):
        expected_answer = f'Режим {smart} уже включен.'
        self.pipeline_user("on", expected_answer)
        self.pipeline_chat_from_owner("on", expected_answer)

    def test_info(self):
        expected_answer = f'Режим {smart} включен.'
        self.pipeline_user("info", expected_answer)
        self.pipeline_chat_from_owner("info", expected_answer)


class SmartChange(SharedMethods):

    def setUp(self):
        self.chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True)
        self.reply_object = models.SmartReply.objects.create(chat_id=self.chat_db_object,
                                                             trigger="trigger-message", reply="smart_reply")

    def test_on_user(self):
        expected_answer = f"Режим {smart} включен."
        self.pipeline_user("on", expected_answer)
        self.check_db(True)

    def test_on_chat(self):
        expected_answer = f"Режим {smart} включен."
        self.pipeline_chat_from_owner("on", expected_answer)
        self.check_db(True)

    def test_off_user(self):
        self.chat_db_object.smart_mode = True
        self.chat_db_object.save()
        expected_answer = f'Режим {smart} выключен.'
        self.pipeline_user("off", expected_answer)
        self.check_db(False)

    def test_off_chat(self):
        self.chat_db_object.smart_mode = True
        self.chat_db_object.save()
        expected_answer = f'Режим {smart} выключен.'
        self.pipeline_chat_from_owner("off", expected_answer)
        self.check_db(False)

    def test_updated_last_used_field(self):
        reply_object1 = models.SmartReply.objects.create(chat_id=self.chat_db_object,
                                         trigger="trigger-message1", reply="smart_reply1")
        reply_object2 = models.SmartReply.objects.create(chat_id=self.chat_db_object,
                                         trigger="trigger-message2", reply="smart_reply2")
        self.chat_db_object.smart_mode = True
        self.chat_db_object.save()
        expected_answer = f'Режим {smart} выключен.'
        self.pipeline_chat_from_owner("off", expected_answer)
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

