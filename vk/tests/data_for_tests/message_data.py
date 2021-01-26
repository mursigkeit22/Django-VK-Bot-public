from typing import Optional

from web_vk.constants import BOT_GROUPID, VK_SECRET

my_personal_ID = 21070693


class OwnerAndBotChatDataVarya:
    peer_id = 2000000005
    owner_id = 21070693
    not_owner_id = 12345678


class OwnerAndBotChatDataKiril:
    peer_id = 2000000002
    owner_id = 21070693
    not_owner_id = 12345678


# TODO: change for kiril/varya
class OwnerAndBotChatData:
    peer_id = OwnerAndBotChatDataVarya.peer_id
    owner_id = OwnerAndBotChatDataVarya.owner_id
    not_owner_id = 12345678
    first_name = 'Валерия'
    last_name = 'Иванова'
    screen_name = 'id21070693'


# for Varya-bot and for Kiril-bot
class FakeChatData:
    peer_id = 2000000010
    owner_id = 12345678


class NotAdminChatDataVarya:
    peer_id = 2000000006
    owner_id = 21070693


class NotAdminChatDataKiril:
    peer_id = 2000000004
    owner_id = 21070693


# TODO: change for kiril/varya
class NotAdminChatData:
    peer_id = NotAdminChatDataVarya.peer_id
    owner_id = NotAdminChatDataVarya.owner_id


class NotRegisteredButAdminKirill:
    peer_id = 2000000008
    owner_id = 21070693


class NotRegisteredButAdminVarya:
    peer_id = 2000000001
    owner_id = 21070693


# TODO: change for kiril/varya
class NotRegisteredChatData:
    peer_id = NotRegisteredButAdminVarya.peer_id
    owner_id = NotRegisteredButAdminVarya.owner_id


class RemoveActionChatDataVarya:
    peer_id = 2000000003
    owner_id = 21070693
    local_id = 3


class RemoveActionChatDataKiril:
    peer_id = 2000000001
    owner_id = 21070693
    local_id = 1


# TODO: change for kiril/varya
class RemoveActionChatData:
    peer_id = RemoveActionChatDataVarya.peer_id
    owner_id = RemoveActionChatDataVarya.owner_id
    local_id = RemoveActionChatDataVarya.local_id


def input_data(peer_id: int, text: str, from_id: int, vk_secret: Optional[str] = VK_SECRET):
    data = \
        {'type': 'message_new', 'object':
            {'date': 1579158373,
             'from_id': from_id,
             'id': 0, 'out': 0, 'peer_id': peer_id,
             'text': text,
             'conversation_message_id': 21,
             'fwd_messages': [], 'important': False,
             'random_id': 0, 'attachments': [], 'is_hidden': False},
         'group_id': BOT_GROUPID,
         'event_id': '0d68190a19c440062461b2a94c3f7a3f02a3b648',
         'secret': vk_secret}
    return data
