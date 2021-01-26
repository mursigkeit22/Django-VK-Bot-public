import requests

import vk.models as models
import logging
import vk.helpers as helpers
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from abc import ABC, abstractmethod

import web_vk.constants
from botsite.models import UserProfile
from vk.validators import group_validator

""" 
ВАЖНО!!!
в текст сообщений от бота нельзя ставить '/команда' на первое место, т.к.
иногда контакт лажает и отправляет боту на сервер его собственные сообщения.
И в этом случае бот отреагирует на собственное информационное сообщение как на команду.

"""
code_logger = logging.getLogger('code_process')
DELIMITER = '|'


class CommandHandler(ABC):
    def __init__(self, text_instance, chat_db_object):
        self.text_instance = text_instance
        self.chat_db_object = chat_db_object
        self.peer_id = text_instance.message.peer_id
        self.from_id = text_instance.message.from_id
        self.wordlist = text_instance.wordlist
        self.conversation_type = text_instance.conversation_type
        self.chat_db_object = chat_db_object
        self.setting_db_object = None
        self.option = None
        self.command_word = None

    def check_for_personal_token(self):
        try:
            profile = UserProfile.objects.get(vk_id=self.chat_db_object.owner_id)

        except UserProfile.DoesNotExist:
            bot_answer = f"Чтобы пользоваться командой '{self.command_word} on', пройдите по ссылке {web_vk.constants.LOGIN_LINK}"
            return False, bot_answer

        url = 'https://api.vk.com/method/users.get'
        params = {'v': 5.92, 'access_token': profile.vk_token}
        response = requests.post(url, params=params).json()
        try:
            check = response['response']
            return True, None
        except KeyError:
            if response['error']['error_code'] == 5:
                bot_answer = f'Обновите токен по ссылке {web_vk.constants.LOGIN_LINK}'
                return False, bot_answer
            if response['error']['error_code'] == 6:
                bot_answer = 'Повторите попытку через несколько секунд.'
                return False, bot_answer





    def send_message(self, plain_text):
        code_logger.debug("in send_message")
        helpers.make_request_vk('messages.send', random_id=helpers.randomid(),
                                message=plain_text,
                                peer_id=self.peer_id)
        code_logger.debug(f"after sending. plain_text: {plain_text} ")

        return plain_text

    def check_for_admin(self):
        """ For now this method is only used in user conversations anyway,
            but I added
            self.conversation_type == 'user'
            check for future possible use in chat conversations.

        """
        response_content = helpers.make_request_vk('messages.getConversationsById',
                                                   peer_ids=self.chat_db_object.chat_id)
        response_dict = helpers.parse_vk_object(response_content)
        admin_indicator = response_dict.get('response__count', None)
        if admin_indicator and admin_indicator > 0:
            return True, None
        else:
            code_logger.debug(f"Bot isn't admin in chat {self.chat_db_object.chat_id}")
            bot_answer = f"Бот не является админом в чате {self.chat_db_object.chat_id} и не может выполнять команды."
            if self.conversation_type == 'user':
                self.send_message(bot_answer)
            return False, bot_answer

    def check_for_registration(self):
        """ For now this method is only used in user conversations,
                   but I added
                   self.conversation_type == 'user'
                   check for future possible use in chat conversations.

               """
        if self.chat_db_object.conversation_is_registered:
            return True, None
        else:
            code_logger.debug(f'Conversation {self.chat_db_object.chat_id} is not registered.')
            if self.conversation_type == 'user':
                bot_answer = f"Беседа {self.chat_db_object.chat_id} не зарегистрирована. Зарегистрировать беседу можно командой /reg on."
                self.send_message(bot_answer)
                return False, bot_answer

    def check_for_owner(self):
        if self.from_id == self.chat_db_object.owner_id:
            return True, None
        else:
            if self.conversation_type == 'user':
                bot_answer = f"У вас нет беседы с ID {self.chat_db_object.chat_id}."
                self.send_message(bot_answer)
                return False, bot_answer
            elif self.conversation_type == 'chat':
                bot_answer = 'Только владелец беседы может использовать эту команду.'
                self.send_message(bot_answer)
                return False, bot_answer

    def check_for_length(self, n):
        if len(self.wordlist) < n:
            bot_answer = "Пожалуйста, уточните опцию."
            self.send_message(bot_answer)  # can be other reasons, probably
            return False, bot_answer
        return True, None

    def common_group_valid_option(self, command):
        if self.wordlist[1] == 'off':
            return True, 'off'
        if self.wordlist[1] == 'info':
            return True, 'info'
        if self.wordlist[1] == "on":
            return True, "on"
        if self.wordlist[1] == 'delete':
            bot_answer = f"Возможно, вы имели в виду команду '{command} group delete'?"
            self.send_message(bot_answer)
            return False, bot_answer
        if self.wordlist[1] == "group":
            if self.wordlist[2] == 'delete':
                return True, 'delete'
            else:
                try:
                    group_screen_name, group_id = group_validator(self.wordlist[2])
                    return True, (group_screen_name, group_id)
                except ValidationError:
                    bot_answer = f'Группа {self.wordlist[2]} не может быть зарегистрирована для команды {command}.' \
                                 ' Убедитесь, что ссылка правильная, и группа не является закрытой'

                    self.send_message(bot_answer)
                    return False, bot_answer
        bot_answer = f"У команды {command} нет опции '{self.wordlist[1]}'."
        self.send_message(bot_answer)
        return False, bot_answer

    def check_for_chat_db_object(self):
        if len(self.wordlist) < 2:
            bot_answer = 'Пожалуйста, укажите ID беседы.'
            self.send_message(bot_answer)
            return False, bot_answer

        chat_id = self.wordlist[1]
        try:
            self.chat_db_object = models.Chat.objects.get(chat_id=chat_id)
            code_logger.info(f'In check_chatconversation_id_user, found object {chat_id}')
            return True, None
        except (ObjectDoesNotExist, ValueError) as err:
            code_logger.info(err)
            bot_answer = f"У вас нет беседы с ID '{chat_id}'."  # quotes for better readability (for case when user have sent some nonsence instead of ID)
            self.send_message(bot_answer)
            return False, bot_answer

    @abstractmethod
    def command(self):
        ...

    @abstractmethod
    def valid_option(self):
        ...

    def process(self):
        if self.conversation_type == 'user':
            proceed, bot_answer = self.check_for_chat_db_object()
            if proceed:
                return self.process_user()
            return bot_answer
        elif self.conversation_type == 'chat':
            return self.process_chat()

    @abstractmethod
    def process_user(self):
        ...

    def process_user_part(self):
        """
        - is_owner check: to prevent user from messing with smb.else's chat;
        - is_admin check: to make sure that vkbot has admin status in chat. Admin status is needed to get conversation object (necessary for some vkbot options).
            In case of chat messages, this check is permormed in message_handler.
            In case of private message this check is possible only after parsing the message and getting conversation ID;
        - is_registered check: to ensure, that all necessary db entries for this chat exist.

        We made sure, that user has indicated chat ID and that chat with such an ID exists, earlier.
        """
        self.wordlist = self.wordlist[0:1] + self.wordlist[2:]
        is_owner, bot_answer = self.check_for_owner()
        if is_owner:
            is_admin, bot_answer = self.check_for_admin()
            if is_admin:
                is_registered, bot_answer = self.check_for_registration()
                if is_registered:
                    return True, None
        return False, bot_answer

    def process_user_full(self):

        proceed, bot_answer = self.process_user_part()
        if proceed:
            length_ok, bot_answer = self.check_for_length(2)
            if length_ok:
                option = self.valid_option()
                if option[0]:
                    self.option = option[1]
                    bot_answer = self.command()

                else:
                    bot_answer = option[1]
        return bot_answer

    def process_chat(self):
        is_owner, bot_answer = self.check_for_owner()
        if is_owner:
            length_ok, bot_answer = self.check_for_length(2)
            if length_ok:
                option = self.valid_option()
                if option[0]:
                    self.option = option[1]
                    bot_answer = self.command()

                else:
                    bot_answer = option[1]

        return bot_answer

    def set_interval_to_off(self):
        self.chat_db_object.interval_mode = False
        self.chat_db_object.interval = None
        self.chat_db_object.messages_till_endpoint = None
        self.chat_db_object.save()

