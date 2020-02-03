import vk.models as models
import os
import logging
import vk.helpers as helpers
from django.core.exceptions import ObjectDoesNotExist
# TODO: ВАЖНО!!!
#  в текст информационных сообщений от бота нельзя ставить '/команда' на первое место, т.к.
#  иногда контакт лажает и отправляет боту на сервер его собственные сообщения.
#  И в этом случае бот отреагирует на собственное информационное сообщение как на команду.


code_logger = logging.getLogger('code_process')
DELIMITER = '|'


class CommandHandler:
    def __init__(self, text_instance, chatconversation_db_object):
        self.text_instance = text_instance
        self.chatconversation_db_object = chatconversation_db_object
        self.peer_id = text_instance.message.peer_id
        self.from_id = text_instance.message.from_id
        self.wordlist = text_instance.wordlist
        self.conversation_type = text_instance.conversation_type
        self.option = None

    def send_message(self, plain_text):
        helpers.make_request_vk('messages.send', random_id=helpers.randomid(),
                                message=plain_text,
                                peer_id=self.peer_id)

    def check_for_admin(self):
        response_content = helpers.make_request_vk('messages.getConversationsById',
                                                   peer_ids=self.chatconversation_db_object.peer_id)
        response_dict = helpers.parse_response(response_content, dict(), prefix='')
        type = response_dict.get('response__items__peer__type',
                                 None)
        if type == 'chat':
            return True
        if self.conversation_type == 'user':
            self.send_message(f"Bot isn't admin in chat {self.chatconversation_db_object.peer_id}")
        return False

    def check_for_registration(self):
        if self.chatconversation_db_object.conversation_is_registered:
            return True
        else:
            if self.conversation_type == 'user':
                self.send_message('Conversation is not registered.')

        return False

    def check_for_owner(self):
        if self.from_id == self.chatconversation_db_object.owner_id:
            return True
        else:
            if self.conversation_type == 'user':
                self.send_message(f"You don't have chat with ID {self.chatconversation_db_object.peer_id}")
            elif self.conversation_type == 'chat':
                self.send_message('Only chat owner can use this command.')

    def check_for_length(self, n):
        if len(self.wordlist) < n:
            self.send_message('Please specify command option.')  # can be other reasons probably
            return False
        return True

    def limit_length(self, n):
        if len(self.wordlist) > n:
            self.send_message('Too many words for this command.')
            return False
        return True
    

    def get_chatconversation_db_object(self):
        if len(self.wordlist) < 2:
            self.send_message('No idea what you want from me, but FYI: there should be a second word in your command, '
                              'and it should be your conversation ID.')
            return False

        chatconversation_id = self.wordlist[1]
        try:
            self.chatconversation_db_object = models.ChatConversation.objects.get(peer_id=chatconversation_id)
            code_logger.info(f'In check_chatconversation_id_user, found object {chatconversation_id}')
            return True
        except (ObjectDoesNotExist, ValueError) as err:
            code_logger.info(err)
            self.send_message(f"Chat conversation with ID '{chatconversation_id}' doesn't exist.")
            return False
