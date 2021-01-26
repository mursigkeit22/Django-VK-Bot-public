
from vk import models

from vk.tests.data_for_tests.message_data import FakeChatData, NotAdminChatData, \
    NotRegisteredChatData, input_data, my_personal_ID
from vk.vkreceiver_event_handler import EventHandler


class UserSpecificCommandsMixinTest:
    def __init__(self, command):
        self.command = command

    def pipeline(self, expected_answer: str, peer_id: str):
        text = f"{self.command} {peer_id}"
        data = input_data(my_personal_ID, text, my_personal_ID)  # peer_id = from_id means that message is from user
        returned_answer = EventHandler(data).process()

        self.assertEqual(returned_answer, expected_answer)

    def test_not_owner(self):
        chat_db_object = models.Chat.objects.create(
            chat_id=FakeChatData.peer_id, owner_id=FakeChatData.owner_id)
        models.RandomPostSetting.objects.create(chat_id=chat_db_object)
        expected_answer = f"У вас нет беседы с ID {FakeChatData.peer_id}."
        self.pipeline(expected_answer, peer_id=FakeChatData.peer_id)

    def test_non_existing_chat(self):
        expected_answer = f"У вас нет беседы с ID '888888'."
        self.pipeline(expected_answer, peer_id="888888")

    def test_not_integer_chat_id(self):
        expected_answer = f"У вас нет беседы с ID 'asdfg'."
        self.pipeline(expected_answer, peer_id="asdfg")

    def test_chat_id_not_specified(self):
        expected_answer = "Пожалуйста, укажите ID беседы."
        self.pipeline(expected_answer, peer_id="")

    def test_bot_not_admin(self):
        chat_db_object = models.Chat.objects.create(
            chat_id=NotAdminChatData.peer_id, owner_id=NotAdminChatData.owner_id)
        models.RandomPostSetting.objects.create(chat_id=chat_db_object)
        expected_answer = f"Бот не является админом в чате {NotAdminChatData.peer_id} и не может выполнять команды."
        self.pipeline(expected_answer, peer_id=NotAdminChatData.peer_id)

    def test_chat_not_registered(self):
        chat_db_object = models.Chat.objects.create(
            chat_id=NotRegisteredChatData.peer_id, owner_id=NotRegisteredChatData.owner_id)
        models.RandomPostSetting.objects.create(chat_id=chat_db_object)
        expected_answer = f"Беседа {NotRegisteredChatData.peer_id} не зарегистрирована. Зарегистрировать беседу можно командой /reg on."
        self.pipeline(expected_answer, peer_id=NotRegisteredChatData.peer_id)
