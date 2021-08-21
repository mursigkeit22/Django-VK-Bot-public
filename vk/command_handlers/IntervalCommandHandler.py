from vk.bot_answer import BotAnswer
from vk.command_handler import *
from vk.helpers import interval, declention_message, interval_phrase, option_off, option_on, option_info
from vk.vkbot_exceptions import PrerequisitesError, AlreadyDoneError, WrongOptionError, LimitError


@helpers.class_logger()
class IntervalCommandHandler(CommandHandler):
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.command_word = interval

    def process_user(self):
        return super().process_user_full()

    def get_option(self):
        possible_options = [option_off, option_on, option_info]
        if self.wordlist[1] in possible_options:
            self.option = self.wordlist[1]

        elif self.wordlist[1].isdigit():
            if int(self.wordlist[1]) <= 2 or int(self.wordlist[1]) >= 1000:
                raise LimitError(self.message, bot_response="Интервал должен быть больше 2 и меньше 1000.")

            self.option = int(self.wordlist[1])
        else:
            raise WrongOptionError(self.message,
                                   bot_response=common_dict["wrong_option"].substitute(command=self.command_word,
                                                                                       wrong_option=self.wordlist[1]))

    def turn_off(self):
        if self.chat_db_object.interval_mode:
            super().set_interval_to_off()

            return BotAnswer("INTERVAL_OFF", self.message,
                             bot_response=f'Режим {self.command_word} выключен.')
        else:
            raise AlreadyDoneError(self.message, bot_response=f'Режим {self.command_word} уже выключен.')

    def turn_on(self):
        if self.chat_db_object.interval_mode:
            raise AlreadyDoneError(self.message,
                                   bot_response=f"Режим {self.command_word} уже включен," \
                                                f" интервал между фразами {self.chat_db_object.interval}, " \
                                                f"следующую фразу бот отправит через {self.chat_db_object.messages_till_endpoint}" \
                                                f" {declention_message(self.chat_db_object.messages_till_endpoint)}.")

        else:

            if self.chat_db_object.interval:
                phrases_from_db = models.IntervalPhrase.objects.filter(chat_id=self.chat_db_object)
                if len(phrases_from_db) > 0:
                    self.chat_db_object.interval_mode = True
                    self.chat_db_object.messages_till_endpoint = self.chat_db_object.interval
                    self.chat_db_object.save()
                    return BotAnswer("INTERVAL_ON", self.message, bot_response=f"Режим {self.command_word} включен.")
                else:
                    raise PrerequisitesError(self.message,
                                             bot_response=f"Сначала добавьте фразы командой {interval_phrase} add', после этого можно включить режим интервал.")

            else:
                raise PrerequisitesError(self.message,
                                         bot_response=f"Сначала установите интервал командой {self.command_word}, например '{self.command_word} 10'.")

    def info(self):
        if self.chat_db_object.interval_mode:
            return BotAnswer("INTERVAL_INFO", self.message, bot_response=f"Режим {self.command_word} включен," \
                                                                         f" интервал между фразами {self.chat_db_object.interval}, " \
                                                                         f"следующую фразу бот отправит через {self.chat_db_object.messages_till_endpoint}" \
                                                                         f" {declention_message(self.chat_db_object.messages_till_endpoint)}.")
        else:
            if self.chat_db_object.interval:
                return BotAnswer("INTERVAL_INFO", self.message,
                                 bot_response=f"Режим {self.command_word} выключен. Сохраненные настройки: интервал между фразами бота "
                                              f"- {self.chat_db_object.interval} {declention_message(self.chat_db_object.interval)}.")

            else:
                return BotAnswer("INTERVAL_INFO", self.message,
                                 bot_response=f"Режим {self.command_word} выключен. Сохраненные настройки: интервал не установлен.")

    def set_interval(self):
        if self.chat_db_object.interval_mode:
            self.chat_db_object.interval = self.option
            self.chat_db_object.messages_till_endpoint = self.option
            self.chat_db_object.save()
            return BotAnswer("INTERVAL_SET", self.message,
                             bot_response=f"Режим {self.command_word} включен, интервал между фразами {self.chat_db_object.interval}.")

        else:
            self.chat_db_object.interval = self.option
            self.chat_db_object.save()
            return BotAnswer("INTERVAL_SET", self.message,
                             bot_response=f"Интервал между фразами установлен. Режим {self.command_word} выключен.")

    def command(self):
        if self.option == option_off:
            return self.turn_off()
        elif self.option == option_on:
            return self.turn_on()
        elif self.option == option_info:
            return self.info()
        else:
            return self.set_interval()
