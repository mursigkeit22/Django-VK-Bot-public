from vk.bot_answer import BotAnswer
from vk.command_handler import *
import string

# todo: количество сохраняемых фраз за один раз
# todo: количество фраз на чат # 100
from vk.helpers import interval_phrase, interval, option_info, option_remove, option_add
from vk.usertext import interval_phrase_dict
from vk.vkbot_exceptions import WrongOptionError, AlreadyDoneError

DELIMITER = '|'

""" если контактик получает в чате сообщение длиною больше ≈ 4110 символов, 
он разбивает его на два сообщения (или больше, при необходимости), 
и боту сначала приходит первая часть сообщения, которая умещается в лимит символов, 
следом приходит вторая часть сообщения с неуместившимися символами.
Т.о, если юзер пришлет слишком много больших фраз для сохранения, будет сохранено только то, 
что уместилось в первое сообщение.
Это можно решить установкой специального символа окончания сообщения."""


@helpers.class_logger()
class IntervalPhraseCommandHandler(CommandHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.delimiter = DELIMITER
        self.text = self.message.text
        self.phrases = None
        self.ids_to_remove = set()
        self.command_word = interval_phrase
        self.usertext_dict = interval_phrase_dict

    def process_user(self):
        return super().process_user_full()

    def get_option(self):

        possible_options = [option_info]
        if self.wordlist[1] in possible_options:
            self.option = self.wordlist[1]

        elif self.wordlist[1] == option_add:
            if len(self.wordlist) > 2:
                self.option = option_add
                return
            else:
                raise AbsentOptionError(self.message,
                                        bot_response=self.usertext_dict["absent_or_wrong_add"],
                                        error_description='interval phrase command. add option not specified.')

        elif self.wordlist[1] == option_remove:
            if len(self.wordlist) > 2:
                if self.wordlist[2] == 'all':
                    self.option = f'{option_remove} all'
                    return
                else:
                    self.make_set_id_to_remove()

                    code_logger.info(f'self.wordlist[1] == remove. IDs of phrases to remove: {self.ids_to_remove}')
                    if self.ids_to_remove:
                        self.option = option_remove
                        return
            raise AbsentOptionError(self.message,
                                    bot_response=self.usertext_dict["absent_ids_remove"], )
        else:
            raise WrongOptionError(self.message,
                                   bot_response=common_dict["wrong_option"].substitute(command=self.command_word,
                                                                                       wrong_option=self.wordlist[1]))

    def make_set_id_to_remove(self):
        for el in self.wordlist[2:]:
            el = el.strip(string.punctuation)
            if el.isdigit():
                self.ids_to_remove.add(int(el))

    def command(self):
        if self.option == option_info:
            return self.info()
        elif self.option == option_add:
            return self.add()
        elif self.option == option_remove:
            return self.remove()
        elif self.option == f'{option_remove} all':
            phrases_from_db = models.IntervalPhrase.objects.filter(chat_id=self.chat_db_object)
            self.check_for_phrases_to_remove(phrases_from_db)

            return self.delete_all_phrases(phrases_from_db)

    def check_for_phrases_to_remove(self, phrases_from_db):
        if len(phrases_from_db) == 0:
            code_logger.info('Nothing to remove: 0 phrases in database.')
            raise AlreadyDoneError(self.message,
                                   bot_response=self.usertext_dict["cannot_remove_empty_db"])

    def remove(self):
        phrases_from_db = models.IntervalPhrase.objects.filter(chat_id=self.chat_db_object)
        self.check_for_phrases_to_remove(phrases_from_db)

        ids_from_db = {phrase.id for phrase in phrases_from_db}
        code_logger.info(f"All the phrases' ids from database: {ids_from_db}")

        absent_ids = self.ids_to_remove.difference(ids_from_db)
        actual_ids_to_remove = ids_from_db.intersection(self.ids_to_remove)

        if len(actual_ids_to_remove) == 0:
            bot_response = self.usertext_dict["cannot_remove_wrong_id"].substitute(
                ids=', '.join(str(i) for i in self.ids_to_remove))
            raise PrerequisitesError(self.message, bot_response=bot_response)

        if len(ids_from_db) == len(actual_ids_to_remove):
            if len(absent_ids) == 0:
                return self.delete_all_phrases(phrases_from_db)
            else:
                bot_response = self.usertext_dict["cannot_remove_absent_ids"].substitute(
                    ids=', '.join(str(i) for i in absent_ids)) + " " + self.usertext_dict["all_db_entries_deleted"]
                if self.chat_db_object.interval_mode:
                    super().set_interval_to_off()
                    bot_response += " " + self.usertext_dict["off"]

        else:
            if len(absent_ids) == 0:
                bot_response = self.usertext_dict["remove_ids"].substitute(
                    ids=', '.join(str(i) for i in self.ids_to_remove))

            else:
                bot_response = self.usertext_dict["cannot_remove_absent_ids"].substitute(
                    ids=', '.join(str(i) for i in absent_ids)) + " " + self.usertext_dict["remove_ids"].substitute(
                    ids=', '.join(str(i) for i in actual_ids_to_remove))

        phrases_from_db.filter(id__in=actual_ids_to_remove).delete()
        return BotAnswer("INTERVAL_PHRASE_REMOVE", self.message, bot_response=bot_response)

    def delete_all_phrases(self, phrases_from_db):
        bot_response = self.usertext_dict["all_db_entries_deleted"]
        if self.chat_db_object.interval_mode:
            super().set_interval_to_off()
            bot_response += " " + self.usertext_dict["off"]
        phrases_from_db.delete()
        return BotAnswer("INTERVAL_PHRASE_REMOVE_ALL", self.message, bot_response=bot_response)

    def add(self):
        index = self.text.find("add")
        text = self.text[index + 3:]
        text = text.split(self.delimiter)
        phrases_list = [phrase.strip() for phrase in text if self.phrase_length_check(phrase.strip())]

        phrase_model_list = [models.IntervalPhrase(
            phrase=phrase, chat_id=self.chat_db_object) for phrase in phrases_list]
        models.IntervalPhrase.objects.bulk_create(phrase_model_list)

        return self.info(add_flag=True)

    def phrase_length_check(self, phrase):
        """ not raising exceptions here 'cause we don't want to stop the flow; we just exclude long phrases,
         but ones with normal length should proceed. """
        if len(phrase) > 0:
            if len(phrase) < 4000:
                return True
            else:
                code_logger.info(f'Interval phrase is too big: {len(phrase)}')
                helpers.make_request_vk('messages.send', random_id=helpers.randomid(),
                                        message=f'Фраза "{phrase[0:100]}..." слишком длинная и не будет сохранена.',
                                        peer_id=self.message.peer_id)
                return False

    def info(self, add_flag=None):
        phrases_db_objects = models.IntervalPhrase.objects.filter(
            chat_id=self.chat_db_object).order_by('id')
        bot_response = self.usertext_dict["saved_entries"].substitute(number=len(phrases_db_objects))

        for el in phrases_db_objects:
            new_line = f'id: {el.id}. Фраза: {el.phrase}\n'
            if len(bot_response) + len(new_line) > 4100:
                code_logger.info('In IntervalPhraseCommandHandler.info, len(info_message) + len(new_line) > 4100 ')
                helpers.make_request_vk('messages.send', random_id=helpers.randomid(),
                                        message=bot_response,
                                        peer_id=self.message.peer_id)

                bot_response = new_line
            else:
                bot_response += new_line

        code_logger.info(f'In IntervalPhraseCommandHandler.info, len last info_message {len(bot_response)}')
        event_code = "INTERVAL_PHRASE_INFO"
        if add_flag:
            event_code = "INTERVAL_PHRASE_ADD_INFO"
        return BotAnswer(event_code, self.message, bot_response=bot_response)
