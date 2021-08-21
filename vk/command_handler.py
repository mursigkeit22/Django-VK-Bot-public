import logging
from abc import ABC, abstractmethod

import requests
from django.core.exceptions import ObjectDoesNotExist, ValidationError

import vk.helpers as helpers
import vk.models as models
from botsite.models import UserProfile
from vk.usertext import common_dict
from vk.validators import group_validator
from vk.vkbot_exceptions import *

""" 
ВАЖНО!!!
в текст сообщений от бота нельзя ставить '/команда' на первое место, т.к.
иногда контакт лажает и отправляет боту на сервер его собственные сообщения.
И в этом случае бот отреагирует на собственное информационное сообщение как на команду.

"""
code_logger = logging.getLogger('code_process')
DELIMITER = '|'


@helpers.class_logger(['__init__'])
class CommandHandler(ABC):
    def __init__(self, wordlist, input_message, chat_db_object):
        self.message = input_message
        self.chat_db_object = chat_db_object
        self.peer_id = self.message.peer_id
        self.from_id = self.message.from_id
        self.wordlist = wordlist
        self.conversation_type = self.message.conversation_type
        self.chat_db_object = chat_db_object
        self.setting_db_object = None
        self.option = None
        self.command_word = None

    def check_for_personal_token(self):
        try:
            profile = UserProfile.objects.get(vk_id=self.chat_db_object.owner_id)

        except UserProfile.DoesNotExist:
            raise UserProfileError(self.message, bot_response=common_dict["not_login"].substitute(
                command=f'{self.command_word} {self.option}'))

        url = 'https://api.vk.com/method/users.get'
        params = {'v': 5.92, 'access_token': profile.vk_token}
        response = requests.post(url, params=params).json()
        try:
            check = response['response']
        except KeyError:
            bot_response = "Не удалось получить токен: неизвестная ошибка."  # never happened
            if response['error']['error_code'] == 5:
                bot_response = common_dict["refresh_token"].substitute(
                    command=f'{self.command_word} {self.option}')
            elif response['error']['error_code'] == 6:
                bot_response = 'Повторите попытку через несколько секунд.'
            raise UserProfileError(self.message, bot_response=bot_response)

    def check_for_admin(self):
        """ For now this method is only used in user conversations anyway,
            but I added
            self.conversation_type == 'user'
            check for future possible use in chat conversations.

        """
        response_content = helpers.make_request_vk('messages.getConversationsById',
                                                   peer_ids=self.chat_db_object.chat_id)  # !!!
        response_dict = helpers.parse_vk_object(response_content)
        admin_indicator = response_dict.get('response__count', None)
        if admin_indicator and admin_indicator > 0:
            return
        else:
            code_logger.debug(f"Bot isn't admin in chat {self.chat_db_object.chat_id}")
            bot_response = f"Бот не является админом в чате {self.chat_db_object.chat_id} и не может выполнять команды."
            if self.conversation_type == 'user':
                raise NotAdminError(self.message, bot_response=bot_response)

    def check_for_registration_user(self):
        """ this method is used in user conversations only """
        if self.chat_db_object.conversation_is_registered is False:
            code_logger.debug(f'Conversation {self.chat_db_object.chat_id} is not registered.')
            bot_response = f"Беседа {self.chat_db_object.chat_id} не зарегистрирована. Зарегистрировать беседу можно командой /reg on."
            raise NotRegisteredError(self.message, bot_response=bot_response)

    def check_for_owner_silent_option(self, bot_response=None, error_description=None):
        if self.from_id != self.chat_db_object.owner_id:
            raise NotOwnerError(self.message, bot_response=bot_response, error_description=error_description)

    def check_for_owner_send(self):
        if self.from_id != self.chat_db_object.owner_id:
            raise NotOwnerError(self.message,
                                bot_response=f'Только владелец беседы может использовать команду {self.command_word}.')

    def check_for_owner_userchat(self):
        if self.from_id != self.chat_db_object.owner_id:
            raise WrongChatIdError(self.message, bot_response=f"У вас нет беседы с ID {self.chat_db_object.chat_id}.")

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

    def check_for_length(self, n, **kwargs):
        if len(self.wordlist) < n:
            raise AbsentOptionError(self.message, **kwargs)

    def common_group_get_option(self, ):
        possible_options = [helpers.option_off, helpers.option_on, helpers.option_info]
        if self.wordlist[1] in possible_options:
            self.option = self.wordlist[1]
            return

        if self.wordlist[1] == helpers.option_delete:
            bot_response = f"Возможно, вы имели в виду команду '{self.command_word} {helpers.option_group} {helpers.option_delete}'?"
            raise WrongOptionError(self.message, bot_response=bot_response)

        if self.wordlist[1] == helpers.option_group:
            if self.wordlist[2] == helpers.option_delete:
                self.option = helpers.option_delete
                return
            else:
                try:
                    group_screen_name, group_id = group_validator(self.wordlist[2])
                    self.option = (group_screen_name, group_id)
                    return
                except ValidationError:
                    bot_response = f'Группа {self.wordlist[2]} не может быть зарегистрирована для команды {self.command_word}.' \
                                   ' Убедитесь, что ссылка правильная, и группа не является закрытой'
                    raise GroupValidationError(self.message, bot_response=bot_response)

        raise WrongOptionError(self.message,
                               bot_response=f"У команды {self.command_word} нет опции '{self.wordlist[1]}'.")

    def check_for_chat_db_object(self):
        if len(self.wordlist) < 2:
            raise AbsentChatIdError(self.message)

        chat_id = self.wordlist[1]
        try:
            self.chat_db_object = models.Chat.objects.get(chat_id=chat_id)
            code_logger.info(f'In CommandHandler.check_for_chat_db_object. Found object {chat_id}')

        except (ObjectDoesNotExist, ValueError) as err:
            raise NonExistingChatIdError(self.message,
                                         bot_response=f"У вас нет беседы с ID '{chat_id}'.")  # quotes for better readability (for case when user have sent some nonsence instead of ID)

    @abstractmethod
    def command(self):
        ...

    @abstractmethod
    def get_option(self):
        ...

    def process(self):
        if self.conversation_type == 'user':
            self.check_for_chat_db_object()
            return self.process_user()
        elif self.conversation_type == 'chat':
            return self.process_chat()

    @abstractmethod
    def process_user(self):
        ...

    def process_user_part(self):
        """
        - is_owner check: to prevent user from messing with smb.else's chat;
        - is_admin check: to make sure that vkbot has admin status in chat. Admin status is needed to get conversation object (necessary for some vkbot options).
            In case of chat messages, this check is performed in message_handler.
            In case of private(user) messages, this check is possible only after parsing the message and getting conversation ID;
        - is_registered check: to ensure that all necessary db entries for this chat exist.

        We made sure, that user has indicated chat ID and that chat with such an ID exists, earlier.
        (check_for_chat_db_object method called from process)
        """
        self.wordlist = self.wordlist[0:1] + self.wordlist[2:]
        self.check_for_owner_userchat()
        self.check_for_admin()
        self.check_for_registration_user()

    def process_user_full(self):

        self.process_user_part()
        self.check_for_length(2)
        self.get_option()
        return self.command()

    def process_chat(self):
        self.check_for_owner_send()
        self.check_for_length(2)
        self.get_option()
        return self.command()

    def set_interval_to_off(self):
        self.chat_db_object.interval_mode = False
        self.chat_db_object.interval = None
        self.chat_db_object.messages_till_endpoint = None
        self.chat_db_object.save()
