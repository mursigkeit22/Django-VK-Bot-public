from vk.command_handler import *
import string

# todo: количество сохраняемых фраз за один раз
# todo: количество фраз на чат # 100
DELIMITER = '|'


class IntervalPhraseCommandHandler(CommandHandler):
    def __init__(self, text_instance, chat_db_object):
        super().__init__(text_instance, chat_db_object)
        self.delimiter = DELIMITER
        self.text = self.text_instance.text
        self.phrases = None
        self.ids_to_remove = set()

    def process_user(self):
        return super().process_user_full()

    def valid_option(self):

        code_logger.debug('PhraseCommandHandler. valid_option function.')

        if self.wordlist[1] == 'info':
            return True, 'info'
        if self.wordlist[1] == 'add':
            if len(self.wordlist) > 2:
                return True, 'add'
            else:
                bot_answer = "Напишите фразы для бота после команды /phrase add. Используйте разделитель '|'," \
                             " если хотите добавить сразу несколько фраз."
                super().send_message(bot_answer)
                return False, bot_answer
        if self.wordlist[1] == 'remove':
            if len(self.wordlist) > 2:
                if self.wordlist[2] == 'all':
                    return True, 'remove all'
                else:
                    self.make_set_id_to_remove()

                    code_logger.debug(f'self.wordlist[1] == remove. IDs of phrases to remove: {self.ids_to_remove}')
                    if self.ids_to_remove:
                        return True, 'remove'

            bot_answer = "После команды /phrase remove нужно написать id фраз, которые вы хотите удалить, " \
                         "например '/phrase remove 35, 44, 28'. Узнать id фраз можно командой /phrase info."
            super().send_message(bot_answer)
            return False, bot_answer

        bot_answer = super().send_message(f"У команды /phrase нет опции '{self.wordlist[1]}'")
        return False, bot_answer

    def make_set_id_to_remove(self):
        for el in self.wordlist[2:]:
            el = el.strip(string.punctuation)
            if el.isdigit():
                self.ids_to_remove.add(int(el))

    def command(self):
        if self.option == 'info':
            return self.info()
        elif self.option == 'add':
            return self.add()
        elif self.option == 'remove':
            return self.remove()
        elif self.option == 'remove all':
            phrases_from_db = models.IntervalPhrase.objects.filter(chat_id=self.chat_db_object)
            phrases_exist, bot_answer = self.check_for_phrases_to_remove(phrases_from_db)
            if not phrases_exist:
                return bot_answer
            return self.delete_all_phrases(phrases_from_db)

    def check_for_phrases_to_remove(self, phrases_from_db):
        if len(phrases_from_db) == 0:
            code_logger.debug('Nothing to remove: 0 phrases in database.')
            bot_answer = "Невозможно выполнить удаление: у вас не сохранено ни одной фразы."
            super().send_message(bot_answer)
            return False, bot_answer
        else:
            return True, None

    def remove(self):
        code_logger.debug('remove function.')
        phrases_from_db = models.IntervalPhrase.objects.filter(chat_id=self.chat_db_object)
        phrases_exist, bot_answer = self.check_for_phrases_to_remove(phrases_from_db)
        if not phrases_exist:
            return bot_answer

        ids_from_db = {phrase.id for phrase in phrases_from_db}
        code_logger.info(f"All the phrases' ids from database: {ids_from_db}")

        absent_ids = self.ids_to_remove.difference(ids_from_db)
        actual_ids_to_remove = ids_from_db.intersection(self.ids_to_remove)

        if len(actual_ids_to_remove) == 0:
            bot_answer = f"Невозможно выполнить удаление: у вас нет фраз с ID {', '.join(str(i) for i in self.ids_to_remove)}."
            super().send_message(bot_answer)
            return bot_answer

        if len(ids_from_db) == len(actual_ids_to_remove):
            if len(absent_ids) == 0:
                return self.delete_all_phrases(phrases_from_db)
            else:
                bot_answer = f"Фраз с ID {', '.join(str(i) for i in absent_ids)} у вас нет. Удалены все сохраненные фразы."
                if self.chat_db_object.interval_mode:
                    code_logger.debug('PhraseCommandHandler. set_interval_to_off.')
                    super().set_interval_to_off()
                    bot_answer += " Режим /interval отключен."
                super().send_message(bot_answer)

        else:
            if len(absent_ids) == 0:
                bot_answer = f"Фразы с ID {', '.join(str(i) for i in self.ids_to_remove)} удалены."

            else:
                bot_answer = f"Фраз с ID {', '.join(str(i) for i in absent_ids)} у вас нет." \
                             f" Фразы с ID {', '.join(str(i) for i in actual_ids_to_remove)} удалены."

            super().send_message(bot_answer)

        phrases_from_db.filter(id__in=actual_ids_to_remove).delete()
        return bot_answer

    def delete_all_phrases(self, phrases_from_db):
        bot_answer = "Удалены все сохраненные фразы."
        if self.chat_db_object.interval_mode:
            code_logger.debug('PhraseCommandHandler. set_interval_to_off.')
            super().set_interval_to_off()
            bot_answer += " Режим /interval отключен."
        phrases_from_db.delete()
        super().send_message(bot_answer)
        return bot_answer

    def add(self):
        index = self.text.find("add")
        text = self.text[index+3:]
        text = text.split(self.delimiter)
        phrases_list = [phrase.strip() for phrase in text if self.phrase_length_check(phrase.strip())]

        phrase_model_list = [models.IntervalPhrase(
            phrase=phrase, chat_id=self.chat_db_object) for phrase in phrases_list]
        models.IntervalPhrase.objects.bulk_create(phrase_model_list)

        return self.info()

    def phrase_length_check(self, phrase):
        if len(phrase) > 0:
            if len(phrase) < 4000:
                return True
            else:
                code_logger.debug(f'Checking length of the phrase, phrase is too big: {len(phrase)}')
                super().send_message(f'Фраза "{phrase[0:100]}..." слишком длинная и не будет сохранена.')
        return False

    def info(self):
        phrases_db_objects = models.IntervalPhrase.objects.filter(
            chat_id=self.chat_db_object).order_by('id')

        bot_answer = f"Сохраненных фраз для режима /interval: {len(phrases_db_objects)}.\n"

        for el in phrases_db_objects:
            new_line = f'id: {el.id}. Phrase: {el.phrase}\n'
            if len(bot_answer) + len(new_line) > 4100:
                code_logger.info('In phrase info, len(info_message) + len(new_line) > 4100 ')

                super().send_message(bot_answer)
                bot_answer = new_line
            else:
                bot_answer += new_line

        code_logger.info(f'len last info_message {len(bot_answer)}')

        super().send_message(bot_answer)
        return bot_answer
