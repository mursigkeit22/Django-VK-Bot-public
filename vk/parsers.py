import os
import logging
from vk.command_handlers.RegistrationCommandHandler import RegistrationCommandHandler
from vk.command_handlers.RemoveGroupCommandHandler import RemoveGroupCommandHandler
from vk.command_handlers.RemoveCommandHandler import RemoveCommandHandler
from vk.command_handlers.PhraseCommandHandler import PhraseCommandHandler
from vk.command_handlers.IntervalCommandHandler import IntervalCommandHandler
from vk.command_handlers.PostGroupCommandHandler import PostGroupCommandHandler
from vk.command_handlers.PostCommandHandler import PostCommandHandler
from vk.command_handlers.NewPostCommandHandler import NewPostCommandHandler


code_logger = logging.getLogger('code_process')

DELIMITER = '|'


bot_name = os.environ['BOT_NAME']

command_list = ['/grouppurge', '/purge', '/interval', '/reg', '/phrase', '/grouppost', '/post', '/newpost']


class TextParser:
    def __init__(self, message_instance):
        self.message = message_instance
        self.text = message_instance.text
        self.conversation_type = message_instance.conversation_type
        self.wordlist = message_instance.text.lower().split()
        code_logger.info(f'In TextParser, self.wordlist: {self.wordlist}')
        self.status = self.status_check()
        code_logger.info(f'Text status: {self.status}')

    def command_handler_caller(self, chatconversation_db_object=None):  # если юзер, то нан, если чат - объект базы данных передается из мессаджХендлера
        if self.wordlist[0] == '/grouppurge':
            RemoveGroupCommandHandler(self, chatconversation_db_object).process()
        elif self.wordlist[0] == '/grouppost':
            PostGroupCommandHandler(self, chatconversation_db_object).process()
        elif self.wordlist[0] == '/purge':
            RemoveCommandHandler(self, chatconversation_db_object).process()
        elif self.wordlist[0] == '/interval':
            IntervalCommandHandler(self, chatconversation_db_object).process()
        elif self.wordlist[0] == '/reg':
            RegistrationCommandHandler(self, chatconversation_db_object).process()
        elif self.wordlist[0] == '/phrase':
            PhraseCommandHandler(self, chatconversation_db_object).process()
        elif self.wordlist[0] == '/post':
            PostCommandHandler(self, chatconversation_db_object).process()
        elif self.wordlist[0] == '/newpost':
            NewPostCommandHandler(self, chatconversation_db_object).process()

    def status_check(self):
        if not self.wordlist:
            return None
        if self.wordlist[0] in command_list:
            return 'command'
        if self.wordlist[0][0] == '/':   #
            return 'wrong command'
        if bot_name in self.wordlist:  # calling doesn't work in user_chat vk
            return 'call'
        return 'usual'

