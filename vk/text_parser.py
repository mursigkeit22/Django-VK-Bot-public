import logging
from vk.command_handlers.RegistrationCommandHandler import RegistrationCommandHandler
from vk.command_handlers.RemoveCommandHandler import RemoveCommandHandler
from vk.command_handlers.IntervalPhraseCommandHandler import IntervalPhraseCommandHandler
from vk.command_handlers.IntervalCommandHandler import IntervalCommandHandler
from vk.command_handlers.RandomPostCommandHandler import RandomPostCommandHandler
from vk.command_handlers.NewPostCommandHandler import NewPostCommandHandler
from vk.command_handlers.SmartCommandHandler import SmartCommandHandler
from vk.command_handlers.SmartReplyCommandHandler import SmartReplyCommandHandler
from vk.helpers import remove, new_post, interval, registration, interval_phrase, random_post, smart_reply, smart
from web_vk.constants import BOT_NAME

code_logger = logging.getLogger('code_process')

# DELIMITER = '|'

command_list = [f'{remove}', f'{interval}', f'{registration}', f'{interval_phrase}', f'{random_post}', f'{new_post}',
                f'{smart_reply}', f'{smart}']


class TextParser:
    def __init__(self, message_instance):
        self.message = message_instance
        self.text = message_instance.text
        self.conversation_type = message_instance.conversation_type
        self.wordlist = self.text.lower().split()
        code_logger.info(f'In TextParser, self.wordlist: {self.wordlist}')
        self.status = self.status_check()
        code_logger.info(f'In TextParser, text status: {self.status}')

    def command_handler_caller(self, chat_db_object=None):

        """ if conversation_type == "user", then chat_db_object=None and we get it later.
        if conversation_type == "chat", then we already have chat_db_object """

        if self.wordlist[0] == remove:
            bot_answer = RemoveCommandHandler(self, chat_db_object).process()
        elif self.wordlist[0] == interval:
            bot_answer = IntervalCommandHandler(self, chat_db_object).process()
        elif self.wordlist[0] == registration:
            bot_answer = RegistrationCommandHandler(self, chat_db_object).process()
        elif self.wordlist[0] == interval_phrase:
            bot_answer = IntervalPhraseCommandHandler(self, chat_db_object).process()
        elif self.wordlist[0] == random_post:
            bot_answer = RandomPostCommandHandler(self, chat_db_object).process()
        elif self.wordlist[0] == new_post:
            bot_answer = NewPostCommandHandler(self, chat_db_object).process()
        elif self.wordlist[0] == smart_reply:
            bot_answer = SmartReplyCommandHandler(self, chat_db_object).process()
        elif self.wordlist[0] == smart:
            bot_answer = SmartCommandHandler(self, chat_db_object).process()
        return bot_answer

    def status_check(self):
        """ 'call' option is for possible forthcoming features.
         Makes sense for chat conversations only, not for user conversations. """
        if not self.wordlist:
            return None
        if self.wordlist[0] in command_list:
            return 'command'
        if self.wordlist[0][0] == '/':
            return 'wrong command'
        if BOT_NAME in self.wordlist:
            return 'call'
        return 'usual'
