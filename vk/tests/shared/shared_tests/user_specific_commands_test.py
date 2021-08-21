from vk import models
from vk.helpers import registration

from vk.tests.data_for_tests.message_data import FakeChatData, NotAdminChatData, \
    NotRegisteredChatData, OwnerAndBotChatData
from vk.tests.shared.pipelines_and_setups import PipelinesAndSetUps


class UserSpecificCommandsMixinTest(PipelinesAndSetUps):

    def test_not_owner(self):
        models.Chat.objects.create(
            chat_id=FakeChatData.peer_id, owner_id=FakeChatData.owner_id)
        bot_response = f"У вас нет беседы с ID {FakeChatData.peer_id}."
        input_text = f"{self.command} {FakeChatData.peer_id}"
        self.core_pipeline(OwnerAndBotChatData.owner_id, OwnerAndBotChatData.owner_id,
                           input_text, "WRONG_CHAT", bot_response=bot_response)

    def test_non_existing_chat(self):
        bot_response = f"У вас нет беседы с ID '888888'."
        input_text = f"{self.command} 888888"
        self.core_pipeline(OwnerAndBotChatData.owner_id, OwnerAndBotChatData.owner_id,
                           input_text, "NON_EXISTING_CHAT", bot_response=bot_response)

    def test_not_integer_chat_id(self):
        bot_response = f"У вас нет беседы с ID 'asdfg'."
        input_text = f"{self.command} asdfg"
        self.core_pipeline(OwnerAndBotChatData.owner_id, OwnerAndBotChatData.owner_id,
                           input_text, "NON_EXISTING_CHAT", bot_response=bot_response)

    def test_chat_id_not_specified(self):
        bot_response = "Пожалуйста, укажите ID беседы."
        input_text = f"{self.command}"
        self.core_pipeline(OwnerAndBotChatData.owner_id, OwnerAndBotChatData.owner_id,
                           input_text, "ABSENT_CHAT_ID", bot_response=bot_response)

    def test_bot_not_admin(self):
        models.Chat.objects.create(
            chat_id=NotAdminChatData.peer_id, owner_id=NotAdminChatData.owner_id)
        input_text = f"{self.command} {NotAdminChatData.peer_id}"
        bot_response = f"Бот не является админом в чате {NotAdminChatData.peer_id} и не может выполнять команды."
        self.core_pipeline(OwnerAndBotChatData.owner_id, OwnerAndBotChatData.owner_id,
                           input_text, "NOT_ADMIN", bot_response=bot_response)

    def test_chat_not_registered(self):
        models.Chat.objects.create(
            chat_id=NotRegisteredChatData.peer_id, owner_id=NotRegisteredChatData.owner_id)
        input_text = f"{self.command} {NotRegisteredChatData.peer_id}"
        bot_response = f"Беседа {NotRegisteredChatData.peer_id} не зарегистрирована. Зарегистрировать беседу можно командой {registration} on."
        self.core_pipeline(OwnerAndBotChatData.owner_id, OwnerAndBotChatData.owner_id,
                           input_text, "NOT_REGISTERED", bot_response=bot_response)
