from django.test import TestCase

from vk import models
from vk.tests.data_for_tests.message_data import OwnerAndBotChatData


class ActionSmartTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True, )
