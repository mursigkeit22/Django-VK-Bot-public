import re
import string

from vk.command_handler import *
from vk.helpers import smart_reply

DELIMITER = "||"


class SmartReplyCommandHandler(CommandHandler):

    def __init__(self, text_instance, chat_db_object):
        super().__init__(text_instance, chat_db_object)
        self.delimiter = DELIMITER
        self.text = self.text_instance.text

        self.ids_to_remove = set()

    def process_user(self):
        return super().process_user_full()


    def valid_option(self):

        code_logger.debug('SmartReplyCommandHandler. valid_option function.')
        # if self.wordlist[1] == "change":
        #     return True, "change"

        if self.wordlist[1] == 'info':
            return True, 'info'
        if self.wordlist[1] == 'add':
            return True, 'add'

        if self.wordlist[1] == 'remove':
            if len(self.wordlist) > 2:
                if self.wordlist[2] == 'all':
                    return True, 'remove all'
                else:
                    self.make_set_id_to_remove()

                    code_logger.debug(f'self.wordlist[1] == remove. IDs of replies to remove: {self.ids_to_remove}')
                    if self.ids_to_remove:
                        return True, 'remove'

            bot_answer = f"После команды {smart_reply} remove нужно написать ID smart-сообщений, которые вы хотите удалить, " \
                         f"например '{smart_reply} remove 35, 44, 28'. Узнать ID smart-сообщений можно командой {smart_reply} info."
            super().send_message(bot_answer)
            return False, bot_answer

        bot_answer = super().send_message(f"У команды {smart_reply} нет опции '{self.wordlist[1]}'")
        return False, bot_answer

    def command(self):
        if self.option == 'info':
            return self.info()
        elif self.option == 'add':
            return self.add()
        elif self.option == 'remove':
            return self.remove()
        elif self.option == 'remove all':
            smart_entries_from_db = models.SmartReply.objects.filter(chat_id=self.chat_db_object)
            smart_entries_exist, bot_answer = self.check_for_phrases_to_remove(smart_entries_from_db)
            if not smart_entries_exist:
                return bot_answer
            return self.delete_all_smart_entries(smart_entries_from_db)

        # elif self.option == "change":
        #     return self.change_reply()

    def make_set_id_to_remove(self):
        for el in self.wordlist[2:]:
            el = el.strip(string.punctuation)
            if el.isdigit():
                self.ids_to_remove.add(int(el))

    def check_for_phrases_to_remove(self, phrases_from_db):
        if len(phrases_from_db) == 0:
            code_logger.debug('Nothing to remove: 0 smart messages in database.')
            bot_answer = "Невозможно выполнить удаление: у вас не сохранено ни одного smart-сообщения."
            super().send_message(bot_answer)
            return False, bot_answer
        else:
            return True, None

    def remove(self):
        code_logger.debug('remove function.')
        phrases_from_db = models.SmartReply.objects.filter(chat_id=self.chat_db_object)
        phrases_exist, bot_answer = self.check_for_phrases_to_remove(phrases_from_db)
        if not phrases_exist:
            return bot_answer

        ids_from_db = {phrase.id for phrase in phrases_from_db}
        code_logger.info(f"All the smart messages' ids from database: {ids_from_db}")

        absent_ids = self.ids_to_remove.difference(ids_from_db)
        actual_ids_to_remove = ids_from_db.intersection(self.ids_to_remove)

        if len(actual_ids_to_remove) == 0:
            bot_answer = f"Невозможно выполнить удаление: у вас нет smart-сообщений с ID {', '.join(str(i) for i in self.ids_to_remove)}."
            super().send_message(bot_answer)
            return bot_answer

        if len(ids_from_db) == len(actual_ids_to_remove):
            if len(absent_ids) == 0:
                return self.delete_all_smart_entries(phrases_from_db)
            else:
                bot_answer = f"Smart-сообщений с ID {', '.join(str(i) for i in absent_ids)} у вас нет. Удалены все сохраненные smart-сообщения."
                if self.chat_db_object.smart_mode:
                    code_logger.debug('SmartReplyCommandHandler. set_smartmode_to_off.')
                    self.chat_db_object.smart_mode = False
                    self.chat_db_object.save()
                    bot_answer += " Режим /smart отключен."
                super().send_message(bot_answer)

        else:
            if len(absent_ids) == 0:
                bot_answer = f"Smart-сообщения с ID {', '.join(str(i) for i in self.ids_to_remove)} удалены."

            else:
                bot_answer = f"Smart-сообщений с ID {', '.join(str(i) for i in absent_ids)} у вас нет." \
                             f" Smart-сообщения с ID {', '.join(str(i) for i in actual_ids_to_remove)} удалены."

            super().send_message(bot_answer)

        phrases_from_db.filter(id__in=actual_ids_to_remove).delete()
        return bot_answer

    def delete_all_smart_entries(self, smart_entries_from_db):
        bot_answer = "Удалены все сохраненные smart-сообщения."
        if self.chat_db_object.smart_mode:
            code_logger.debug('SmartReplyCommandHandler. set_smartmode_to_off.')
            self.chat_db_object.smart_mode = False
            self.chat_db_object.save()
            bot_answer += " Режим /smart отключен."
        smart_entries_from_db.delete()
        super().send_message(bot_answer)
        return bot_answer

    def info(self):
        phrases_db_objects = models.SmartReply.objects.filter(
            chat_id=self.chat_db_object).order_by('id')

        bot_answer = f"Сохраненных сообщений для режима /smart: {len(phrases_db_objects)}.\n"

        for el in phrases_db_objects:

            new_line = f'ID: {el.id}. Сообщение-триггер: {el.trigger} . Smart-ответ: {el.reply}\n'
            if len(bot_answer) + len(new_line) > 4100:
                code_logger.info('In smartreply info, len(info_message) + len(new_line) > 4100 ')

                super().send_message(bot_answer)
                bot_answer = new_line
            else:
                bot_answer += new_line

        code_logger.info(f'len last info_message {len(bot_answer)}')

        super().send_message(bot_answer)
        return bot_answer

    def add(self):
        count = models.SmartReply.objects.filter(chat_id=self.chat_db_object).count()
        if count > 99:
            bot_answer = "У вас уже сохранено 100 smart-сообщений. Это максимально возможное количество."
            super().send_message(bot_answer)
            return bot_answer
        index = self.text.find("add")
        text = self.text[index + 3:]
        text = text.split(self.delimiter)
        if len(text) != 2:
            bot_answer = f"После команды {smart_reply} add нужно написать сообщение, на которое будет реагировать бот, " \
                         f"затем, через разделитель ||, ответ бота. " \
                         f"Например: '{smart_reply} add Привет || Сам привет'"
            super().send_message(bot_answer)
            return bot_answer
        trigger = text[0].strip()
        reply = text[1].strip()
        if len(trigger) > helpers.SMART_MAX_LEN or len(reply) > helpers.SMART_MAX_LEN:
            bot_answer = f"Сообщения не могут быть длинее {helpers.SMART_MAX_LEN} знаков."
            super().send_message(bot_answer)
            return bot_answer
        if len(trigger) < 1 or len(reply) < 1:
            bot_answer = "Нельзя сохранить пустое сообщение."
            super().send_message(bot_answer)
            return bot_answer
        models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger=trigger.lower(), reply=reply.lower())
        return self.info()

    def get_reply_entry(self, reply_id):
        try:
            smart_object = models.SmartReply.objects.get(chat_id=self.chat_db_object, id=reply_id)
            return smart_object
        except (ObjectDoesNotExist, ValueError) as err:
            code_logger.info(err)

            return False

    # def change_reply(self):
    #     reply_id = self.wordlist[2]
    #     smart_object = self.get_reply_entry(reply_id)
    #     if smart_object:
    #         match = re.search(f"{reply_id}", self.text)
    #         index = match.end()
    #         reply = self.text[index:].strip()
    #         if len(reply) > 100 or len(reply) < 1:
    #             bot_answer = "error"
    #             super().send_message(bot_answer)
    #             return bot_answer
    #         smart_object.reply = reply
    #         smart_object.save()
    #         bot_answer = "reply 1 success"
    #         super().send_message(bot_answer)
    #         return bot_answer



        else:
            bot_answer = "error"
            super().send_message(bot_answer)
            return bot_answer

