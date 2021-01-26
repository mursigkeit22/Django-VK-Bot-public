from vk.command_handler import *


class IntervalCommandHandler(CommandHandler):

    def process_user(self):
        return super().process_user_full()

    def valid_option(self):

        if self.wordlist[1] == 'off':
            return True, 'off'
        if self.wordlist[1] == 'info':
            return True, 'info'
        if self.wordlist[1] == "on":
            return True, "on"

        if self.wordlist[1].isdigit():
            if int(self.wordlist[1]) <= 2 or int(self.wordlist[1]) >= 1000:
                bot_answer = "Интервал должен быть больше 2 и меньше 1000."
                super().send_message(bot_answer)
                return False, bot_answer
            return True, int(self.wordlist[1])
        else:
            bot_answer = f"У команды /interval нет опции '{self.wordlist[1]}'"
            super().send_message(bot_answer)
            return False, bot_answer

    def command(self):

        if self.option == 'off':
            if self.chat_db_object.interval_mode:
                super().set_interval_to_off()

                bot_answer = 'Режим /interval выключен.'
            else:
                bot_answer = 'Режим /interval уже выключен.'
            super().send_message(bot_answer)

        elif self.option == 'on':
            if self.chat_db_object.interval_mode:
                bot_answer = f"Режим /interval уже включен, интервал между фразами {self.chat_db_object.interval}, " \
                             f"следующую фразу бот отправит через {self.chat_db_object.messages_till_endpoint} сообщений."
                super().send_message(bot_answer)
            else:

                if self.chat_db_object.interval:
                    phrases_from_db = models.IntervalPhrase.objects.filter(chat_id=self.chat_db_object)
                    if len(phrases_from_db) > 0:
                        self.chat_db_object.interval_mode = True
                        self.chat_db_object.messages_till_endpoint = self.chat_db_object.interval
                        self.chat_db_object.save()
                        bot_answer = f"Режим /interval включен."
                        super().send_message(bot_answer)
                    else:
                        bot_answer = "Сначала добавьте фразы командой /phrase add', после этого можно включить режим интервал."
                        super().send_message(bot_answer)
                else:
                    bot_answer = "Сначала установите интервал командой /interval, например '/interval 10'."
                    super().send_message(bot_answer)

        elif self.option == 'info':
            if self.chat_db_object.interval_mode:
                bot_answer = f"Режим /interval включен, интервал между фразами {self.chat_db_object.interval}, " \
                             f"следующую фразу бот отправит через {self.chat_db_object.messages_till_endpoint} сообщений."
                super().send_message(bot_answer)
            else:
                if self.chat_db_object.interval:
                    bot_answer = f"Режим /interval выключен. Настройки: фраза бота через каждые {self.chat_db_object.interval} сообщений."
                else:
                    bot_answer = f"Режим /interval выключен. Настройки: интервал не установлен."
                super().send_message(bot_answer)

        else:
            if self.chat_db_object.interval_mode:
                self.chat_db_object.interval = self.option
                self.chat_db_object.messages_till_endpoint = self.option
                self.chat_db_object.save()
                bot_answer = f"Режим /interval включен, интервал между фразами {self.chat_db_object.interval}"
                super().send_message(bot_answer)
            else:
                self.chat_db_object.interval = self.option
                self.chat_db_object.save()
                bot_answer = "Интервал между фразами установлен. Режим /interval выключен."
                super().send_message(bot_answer)
        return bot_answer


