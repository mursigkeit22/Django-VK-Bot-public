import logging
import vk.helpers as helpers

code_logger = logging.getLogger('code_process')


class ChatConversationInfo:
    def __init__(self, conversation_dict):
        self.response_dict = conversation_dict
        self.response_count = self.response_dict.get('response__count', 0)  # тут, наверное, уже не надо
        self.bot_is_admin = self.bot_is_admin()  # тут, наверное, уже не надо
        self.peer_id = self.response_dict.get('response__items__peer__id',
                                              None)  # is it different from message.peer_id?
        code_logger.debug(f'ChatConversation peer_id: {self.peer_id}')
        self.local_id = self.response_dict.get('response__items__peer__local_id', None)
        self.owner_id = self.response_dict.get('response__items__chat_settings__owner_id', None)
        self.members_count = self.response_dict.get('response__items__chat_settings__members_count', None)
        self.type = self.response_dict.get('response__items__peer__type', None)  # user, chat, group, email
        self.admins = self.response_dict.get('response__items__chat_settings__admin_ids',
                                             None)  # TODO later: foreign key?

    def bot_is_admin(self):  # тут, наверное, уже не надо
        if self.response_count < 1:
            return False
        return True


class UserConversationInfo:  # TODO: read about data classes
    def __init__(self, conversation_dict):
        self.response_dict = conversation_dict
        self.response_count = self.response_dict.get('response__count', 0)  # тут, наверное, уже не надо
        self.peer_id = self.response_dict.get('response__items__peer__id', None)  # peer_id = local_id в личке. всегда?
        self.local_id = self.response_dict.get('response__items__peer__local_id', None)
        self.type = self.response_dict.get('response__items__peer__type', None)  # user, chat, group, email


class GroupInfo:
    def __init__(self, content):
        self.response_dict = helpers.parse_response(content, dict(), prefix='')
        self.group_id = self.response_dict.get('response__id', None)
        self.screen_name = self.response_dict.get('response__screen_name', None)
        self.is_closed = self.response_dict.get('response__is_closed', 2)
