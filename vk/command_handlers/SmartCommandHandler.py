import datetime

from django.utils import timezone

from vk import models
from vk.command_handler import CommandHandler

from vk.helpers import smart, smart_reply, five_minutes_ago


class SmartCommandHandler(CommandHandler):

    def process_user(self):
        return super().process_user_full()

    def valid_option(self):

        if self.wordlist[1] == 'off':
            return True, 'off'
        if self.wordlist[1] == 'info':
            return True, 'info'
        if self.wordlist[1] == "on":
            return True, "on"

        else:
            bot_answer = f"У команды {smart} нет опции '{self.wordlist[1]}'"
            super().send_message(bot_answer)
            return False, bot_answer

    def command(self):

        if self.option == 'off':
            if self.chat_db_object.smart_mode:
                self.chat_db_object.smart_mode = False
                self.chat_db_object.save()

                models.SmartReply.objects.filter(chat_id=self.chat_db_object).update(last_used=five_minutes_ago())

                bot_answer = f'Режим {smart} выключен.'
            else:
                bot_answer = f'Режим {smart} уже выключен.'
            super().send_message(bot_answer)

        elif self.option == 'on':
            if self.chat_db_object.smart_mode:
                bot_answer = f"Режим {smart} уже включен."
                super().send_message(bot_answer)
            else:
                smart_messages_from_db = models.SmartReply.objects.filter(chat_id=self.chat_db_object)
                if len(smart_messages_from_db) > 0:
                    self.chat_db_object.smart_mode = True
                    self.chat_db_object.save()
                    bot_answer = f"Режим {smart} включен."
                    super().send_message(bot_answer)
                else:
                    bot_answer = f"Сначала добавьте smart-сообщения командой {smart_reply} add, после этого можно включить режим {smart[1:]}."
                    super().send_message(bot_answer)

        elif self.option == 'info':
            if self.chat_db_object.smart_mode:
                bot_answer = f"Режим {smart} включен."
                super().send_message(bot_answer)
            else:

                bot_answer = f"Режим {smart} выключен."
                super().send_message(bot_answer)
        return bot_answer
