import logging
from vk.command_handlers.RegistrationCommandHandler import RegistrationCommandHandler
from vk.command_handlers.KickCommandHandler import KickCommandHandler
from vk.command_handlers.IntervalPhraseCommandHandler import IntervalPhraseCommandHandler
from vk.command_handlers.IntervalCommandHandler import IntervalCommandHandler
from vk.command_handlers.RandomPostCommandHandler import RandomPostCommandHandler
from vk.command_handlers.NewPostCommandHandler import NewPostCommandHandler
from vk.command_handlers.SmartCommandHandler import SmartCommandHandler
from vk.helpers import kick, newpost, interval, registration, interval_phrase, random_post, smart
from web_vk.constants import BOT_NAME1, BOT_NAME2

code_logger = logging.getLogger('code_process')


command_list = [f'{kick}', f'{interval}', f'{registration}', f'{interval_phrase}', f'{random_post}', f'{newpost}',
                f'{smart}', ]


class TextParser:
    def __init__(self, message_instance):
        self.message = message_instance
        self.text = message_instance.text
        self.conversation_type = message_instance.conversation_type
        self.wordlist = self.text.lower().split()
        self.status = self.status_check()
        code_logger.info(f'In TextParser.__init__, text status: {self.status}')

    def command_handler_caller(self, chat_db_object=None):

        """ if conversation_type == "user", then chat_db_object=None and we get it later.
        if conversation_type == "chat", then we already have chat_db_object """

        if self.wordlist[0] == kick:
            bot_answer = KickCommandHandler(self.wordlist, self.message, chat_db_object).process()
        elif self.wordlist[0] == interval:
            bot_answer = IntervalCommandHandler(self.wordlist, self.message, chat_db_object).process()
        elif self.wordlist[0] == registration:
            bot_answer = RegistrationCommandHandler(self.wordlist, self.message, chat_db_object).process()
        elif self.wordlist[0] == interval_phrase:
            bot_answer = IntervalPhraseCommandHandler(self.wordlist, self.message, chat_db_object).process()
        elif self.wordlist[0] == random_post:
            bot_answer = RandomPostCommandHandler(self.wordlist, self.message, chat_db_object).process()
        elif self.wordlist[0] == newpost:
            bot_answer = NewPostCommandHandler(self.wordlist, self.message, chat_db_object).process()
        elif self.wordlist[0] == smart:
            bot_answer = SmartCommandHandler(self.wordlist, self.message, chat_db_object).process()

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
        if BOT_NAME1 in self.wordlist or BOT_NAME2 in self.wordlist:
            return 'call'
        return 'usual'
