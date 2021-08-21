from vk.bot_answer import BotAnswer
from vk.command_handler import *
from vk.helpers import registration, option_off, option_info, option_on
from vk.vkbot_exceptions import UserRegCommandError, WrongOptionError, AlreadyDoneError


@helpers.class_logger()
class RegistrationCommandHandler(CommandHandler):
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.command_word = registration

    def is_asking_for_registration(self):
        if self.wordlist == [f'{self.command_word}', option_on]:
            super().check_for_owner_silent_option()
            return True
        return False

    def chat_registration(self):

        self.chat_db_object.conversation_is_registered = True
        self.chat_db_object.save()
        models.NewPostSetting.objects.update_or_create(chat_id=self.chat_db_object)
        models.KickNonMembersSetting.objects.update_or_create(chat_id=self.chat_db_object)
        models.RandomPostSetting.objects.update_or_create(chat_id=self.chat_db_object)

        code_logger.info(f"Conversation is registered with id {self.chat_db_object.chat_id}")
        return BotAnswer('REGISTRATION_SUCCESSFUL', self.message, bot_response=f'Беседа успешно зарегистрирована, '
                                                                               f'ID вашей беседы: {self.chat_db_object.chat_id}')

    def process(self):
        if self.conversation_type == 'user':
            return self.process_user()

        elif self.conversation_type == 'chat':
            return self.process_chat()

    def get_option(self):
        possible_options = [option_off, option_info]
        if self.wordlist[1] in possible_options:
            self.option = self.wordlist[1]

        elif self.wordlist[1] == option_on:
            raise AlreadyDoneError(self.message,
                                   bot_response=f'Эта беседа уже зарегистрирована, ID вашей беседы {self.peer_id}')

        else:
            raise WrongOptionError(self.message,
                                   bot_response=f"У команды {self.command_word} нет опции '{self.wordlist[1]}'")

    def command(self):
        if self.option == option_off:
            models.NewPostSetting.objects.filter(chat_id=self.chat_db_object).update(newpost_mode=False,
                                                                                     newpost_group_link="",
                                                                                     newpost_group_id=None)
            models.KickNonMembersSetting.objects.filter(chat_id=self.chat_db_object).update(kick_nonmembers_mode=False,
                                                                                            kick_nonmembers_group_link="",
                                                                                            kick_nonmembers_group_id=None)
            models.RandomPostSetting.objects.filter(chat_id=self.chat_db_object).update(random_post_mode=False,
                                                                                        random_post_group_link="",
                                                                                        random_post_group_id=None)

            self.chat_db_object.interval_mode = False
            self.chat_db_object.interval = None
            self.chat_db_object.messages_till_endpoint = None

            self.chat_db_object.smart_mode = False

            self.chat_db_object.conversation_is_registered = False
            self.chat_db_object.save()

            return BotAnswer('REGISTRATION_OFF', self.message,
                             bot_response='Регистрация отменена: бот будет игнорировать вас и ваши команды.')

        if self.option == option_info:
            return BotAnswer('REGISTRATION_INFO', self.message,
                             bot_response=f'ID вашей беседы {self.chat_db_object.chat_id}')

    def process_user(self):
        raise UserRegCommandError(self.message)
