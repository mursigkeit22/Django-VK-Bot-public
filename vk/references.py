import logging
from typing import Optional

import vk.helpers as helpers

code_logger = logging.getLogger('code_process')


class ChatReference:
    def __init__(self, conversation_dict):
        self.response_dict = conversation_dict

        self.peer_id = self.response_dict.get('response__items__peer__id',
                                              None)
        code_logger.debug(f'In ChatReference.__init__. ChatConversation peer_id: {self.peer_id}')
        self.local_id = self.response_dict.get('response__items__peer__local_id', None)
        self.owner_id = self.response_dict.get('response__items__chat_settings__owner_id', None)
        self.members_count = self.response_dict.get('response__items__chat_settings__members_count', None)

        self.title = self.response_dict.get('response__items__chat_settings__title', None)


class GroupReference:
    def __init__(self, content):
        self.response_dict: dict = helpers.parse_vk_object(content)
        self.group_id: Optional[int] = self.response_dict.get('response__id', None)
        self.screen_name: Optional[str] = self.response_dict.get('response__screen_name', None)
        self.is_closed: Optional[int] = self.response_dict.get('response__is_closed', 2)
        self.deactivated: Optional[str] = self.response_dict.get('response__deactivated', None)
        self.type: Optional[str] = self.response_dict.get("response__type", None)
