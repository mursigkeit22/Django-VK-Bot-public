from typing import Optional

from web_vk.constants import BOT_GROUPID, VK_SECRET, BOT_NAME1

my_personal_ID = 21070693


class OwnerAndBotChatData:
    if 'варя' in BOT_NAME1:
        peer_id = 2000000005
    elif 'кирил' in BOT_NAME1:
        peer_id = 2000000002
    owner_id = my_personal_ID
    not_owner_id = 12345678
    first_name = 'Валерия'
    last_name = 'Иванова'
    screen_name = 'id21070693'


class FakeChatData:
    peer_id = 2000000010
    owner_id = 12345678


class NoAdminThereIsAccessToMessagesThereIsDBEntryChatData:
    pass


class NotAdminChatData:
    if 'варя' in BOT_NAME1:
        peer_id = 2000000006
    elif 'кирил' in BOT_NAME1:
        peer_id = 2000000003
    owner_id = my_personal_ID


class NotAdminNoAccessToMessagesThereIsDBEntryChatData:
    if 'варя' in BOT_NAME1:
        peer_id = 2000000002

    elif 'кирил' in BOT_NAME1:
        peer_id = 2000000004
    owner_id = my_personal_ID
    not_owner_id = 12345678


class NotRegisteredChatData:
    if 'варя' in BOT_NAME1:
        peer_id = 2000000001
    elif 'кирил' in BOT_NAME1:
        peer_id = 2000000008
    owner_id = my_personal_ID


class KickActionChatData:
    if 'варя' in BOT_NAME1:
        peer_id = 2000000003
        local_id = 3
    elif 'кирил' in BOT_NAME1:
        peer_id = 2000000001
        local_id = 1
    owner_id = my_personal_ID


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
