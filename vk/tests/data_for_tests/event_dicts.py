import os

from vk.tests.data_for_tests.message_data import OwnerAndBotChatData

VK_SECRET = os.environ['VK_SECRET']
BOT_GROUPID = int(os.environ['BOT_GROUPID'])


event_dict_simple_message = {'type': 'message_new', 'object__date': 1600330657, 'object__from_id': OwnerAndBotChatData.owner_id, 'object__id': 0,
                     'object__out': 0, 'object__peer_id': OwnerAndBotChatData.peer_id,
                     'object__text': 'hop', 'object__conversation_message_id': 1223, 'object__fwd_messages': [],
                     'object__important': False, 'object__random_id': 0, 'object__attachments': [],
                     'object__is_hidden': False, 'group_id': BOT_GROUPID,
                     'event_id': '2bec39b2d68d6941316221b3f998502b4f9e8b73', 'secret': VK_SECRET}

event_dict_simple_message_not_me = {'type': 'message_new', 'object__date': 1600330657, 'object__from_id': 12345678, 'object__id': 0,
                     'object__out': 0, 'object__peer_id': OwnerAndBotChatData.peer_id,
                     'object__text': 'hop', 'object__conversation_message_id': 1223, 'object__fwd_messages': [],
                     'object__important': False, 'object__random_id': 0, 'object__attachments': [],
                     'object__is_hidden': False, 'group_id': BOT_GROUPID,
                     'event_id': '2bec39b2d68d6941316221b3f998502b4f9e8b73', 'secret': VK_SECRET}

event_dict_user_me = {'type': 'message_new',
 'object__date': 1601282052,
 'object__from_id': 21070693,
 'object__id': 1078,
 'object__out': 0,
 'object__peer_id': 21070693,
 'object__text': 'hop',
 'object__conversation_message_id': 982,
 'object__fwd_messages': [],
 'object__important': False,
 'object__random_id': 0,
 'object__attachments': [],
 'object__is_hidden': False,
 'group_id': BOT_GROUPID,
 'event_id': '0d9ae3be10f4034546bd83cbe370d0ee0c2e5ef5',
 'secret': VK_SECRET}


def event_dict_user_me_func(text):
    event_dict_user_me = {'type': 'message_new',
 'object__date': 1601282052,
 'object__from_id': 21070693,
 'object__id': 1078,
 'object__out': 0,
 'object__peer_id': 21070693,
 'object__text': text,
 'object__conversation_message_id': 982,
 'object__fwd_messages': [],
 'object__important': False,
 'object__random_id': 0,
 'object__attachments': [],
 'object__is_hidden': False,
 'group_id': BOT_GROUPID,
 'event_id': '0d9ae3be10f4034546bd83cbe370d0ee0c2e5ef5',
 'secret': VK_SECRET}
    return event_dict_user_me


event_dict_chat_title_update_message = {'type': 'message_new', 'object__date': 1600328078, 'object__from_id': 21070693,
                                 'object__id': 0, 'object__out': 0,
                                 'object__peer_id': 2000000005, 'object__text': '',
                                 'object__conversation_message_id': 1212,
                                 'object__action__type': 'chat_title_update', 'object__action__text': '20005',
                                 'object__fwd_messages': [],
                                 'object__important': False, 'object__random_id': 0, 'object__attachments': [],
                                 'object__is_hidden': False,
                                 'group_id': BOT_GROUPID, 'event_id': '92d222dd9d188418efb2628e09829f8d75e3d826',
                                 'secret': VK_SECRET}
