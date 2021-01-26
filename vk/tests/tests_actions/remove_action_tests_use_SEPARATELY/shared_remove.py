from vk import models
from vk.helpers import remove
from vk.tests.data_for_tests.message_data import RemoveActionChatData, input_data
from vk.vkreceiver_event_handler import EventHandler


class SharedRemove:
    def __init__(self, kick_nonmembers_group_link, kick_nonmembers_group_id):
        self.kick_nonmembers_group_link = kick_nonmembers_group_link
        self.kick_nonmembers_group_id = kick_nonmembers_group_id

    def setup(self):
        chat_db_object = models.Chat.objects.create(
            chat_id=RemoveActionChatData.peer_id, owner_id=RemoveActionChatData.owner_id,
            local_id=RemoveActionChatData.local_id,
            conversation_is_registered = True)
        models.KickNonMembersSetting.objects.create(chat_id=chat_db_object,
                                                    kick_nonmembers_group_link=self.kick_nonmembers_group_link,
                                                    kick_nonmembers_group_id=self.kick_nonmembers_group_id,
                                                    kick_nonmembers_mode=True)

    def pipeline_chat(self, expected_answer):
        text = f"{remove}"
        data = input_data(RemoveActionChatData.peer_id, text, RemoveActionChatData.owner_id)
        returned_answer = EventHandler(data).process()
        self.assertEqual(returned_answer, expected_answer)

    def pipeline_user(self, expected_answer):
        text = f"{remove} {RemoveActionChatData.peer_id}"
        data = input_data(RemoveActionChatData.owner_id, text, RemoveActionChatData.owner_id)
        returned_answer = EventHandler(data).process()
        self.assertEqual(returned_answer, expected_answer)
