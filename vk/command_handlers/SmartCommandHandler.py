import string

from vk.bot_answer import BotAnswer
from vk.command_handler import *
from vk.helpers import smart, option_off, option_on, option_info, option_add, option_remove, option_all, \
    option_regex
from web_vk.constants import SMARTREPLY_MAX_COUNT
from vk.usertext import smart_dict

DELIMITER = "||"


@helpers.class_logger()
class SmartCommandHandler(CommandHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.delimiter = DELIMITER
        self.text = self.message.text

        self.ids_to_remove = set()
        self.regex = False

        self.command_word = smart
        self.usertext_dict = smart_dict

    def process_user(self):
        return super().process_user_full()

    def get_option(self):

        possible_options = [option_off, option_on, option_info, ]
        if self.wordlist[1] in possible_options:
            self.option = self.wordlist[1]
            return

        if self.wordlist[1] == option_add:
            self.check_for_length(3, bot_response=self.usertext_dict["absent_or_wrong_add"])
            if self.wordlist[2] == option_regex:
                self.check_for_length(4, bot_response=self.usertext_dict["absent_or_wrong_add"])
                self.regex = True
            self.option = option_add
            return

        if self.wordlist[1] == option_remove:
            if len(self.wordlist) > 2:
                if self.wordlist[2] == option_all:
                    self.option = f"{option_remove} {option_all}"
                    return
                else:
                    self.make_set_id_to_remove()

                    code_logger.info(
                        f'In SmartCommandHandler.get_option. self.wordlist[1] = "remove". IDs of replies to remove: {self.ids_to_remove}')
                    if self.ids_to_remove:
                        self.option = option_remove
                        return

            bot_response = self.usertext_dict["absent_ids_remove"]
            raise AbsentOptionError(self.message, bot_response=bot_response)

        raise WrongOptionError(self.message,
                               bot_response=common_dict["wrong_option"].substitute(command=self.command_word,
                                                                                   wrong_option=self.wordlist[1]))

    def command(self):
        if self.option == option_off:
            return self.off()
        if self.option == option_on:
            return self.on()
        if self.option == option_info:
            return self.info()
        elif self.option == option_add:
            return self.add()

        elif self.option == option_remove:
            return self.remove()
        elif self.option == f'{option_remove} {option_all}':
            smart_entries_from_db = models.SmartReply.objects.filter(chat_id=self.chat_db_object)
            self.check_for_phrases_to_remove(smart_entries_from_db)
            return self.delete_all_smart_entries(smart_entries_from_db)

    def make_set_id_to_remove(self):
        for el in self.wordlist[2:]:
            el = el.strip(string.punctuation)
            if el.isdigit():
                self.ids_to_remove.add(int(el))

    def check_for_phrases_to_remove(self, phrases_from_db):
        if len(phrases_from_db) == 0:
            code_logger.info('In SmartCommandHandler.check_for_phrases_to_remove.'
                             ' Nothing to remove: 0 smart messages in database.')
            raise AlreadyDoneError(self.message, bot_response=self.usertext_dict["cannot_remove_empty_db"])

    def remove(self):
        phrases_from_db = models.SmartReply.objects.filter(chat_id=self.chat_db_object)
        self.check_for_phrases_to_remove(phrases_from_db)
        ids_from_db = {phrase.id for phrase in phrases_from_db}

        absent_ids = self.ids_to_remove.difference(ids_from_db)
        actual_ids_to_remove = ids_from_db.intersection(self.ids_to_remove)

        if len(actual_ids_to_remove) == 0:
            bot_response = self.usertext_dict["cannot_remove_wrong_id"].substitute(
                ids=', '.join(str(i) for i in self.ids_to_remove))
            raise PrerequisitesError(self.message, bot_response=bot_response)

        if len(ids_from_db) == len(actual_ids_to_remove):
            if len(absent_ids) == 0:
                return self.delete_all_smart_entries(phrases_from_db)
            else:
                bot_response = self.usertext_dict["cannot_remove_absent_ids"].substitute(ids=
                                                                                         ', '.join(str(i) for i in
                                                                                                   absent_ids)) + " " + \
                               self.usertext_dict["all_db_entries_deleted"]
                if self.chat_db_object.smart_mode:
                    self.chat_db_object.smart_mode = False
                    self.chat_db_object.save()
                    bot_response += " " + self.usertext_dict["off"]


        else:
            if len(absent_ids) == 0:
                bot_response = self.usertext_dict["remove_ids"].substitute(
                    ids=', '.join(str(i) for i in self.ids_to_remove))

            else:
                bot_response = self.usertext_dict["cannot_remove_absent_ids"].substitute(
                    ids=', '.join(str(i) for i in absent_ids)) + " " + self.usertext_dict[
                                   "remove_ids"].substitute(ids=', '.join(str(i) for i in actual_ids_to_remove))

        phrases_from_db.filter(id__in=actual_ids_to_remove).delete()
        return BotAnswer("SMART_REMOVE", self.message, bot_response=bot_response)

    def delete_all_smart_entries(self, smart_entries_from_db):
        bot_response = self.usertext_dict['all_db_entries_deleted']
        if self.chat_db_object.smart_mode:
            self.chat_db_object.smart_mode = False
            self.chat_db_object.save()
            bot_response += " " + self.usertext_dict["off"]
        smart_entries_from_db.delete()
        return BotAnswer("SMART_REMOVE_ALL", self.message, bot_response=bot_response)

    def info(self, add_flag=None):
        bot_response = self.usertext_dict["on"] if self.chat_db_object.smart_mode else self.usertext_dict["off"]
        phrases_db_objects = models.SmartReply.objects.filter(
            chat_id=self.chat_db_object).order_by('id')

        bot_response += self.usertext_dict["saved_entries"].substitute(number=len(phrases_db_objects))
        for el in phrases_db_objects:

            new_line = f'ID: {el.id}.{" REGEX" if el.regex else ""} Сообщение-триггер: {el.trigger} . Smart-ответ: {el.reply}\n'
            if len(bot_response) + len(new_line) > 4100:
                code_logger.info('In SmartCommandHandler.info, len(info_message) + len(new_line) > 4100 ')
                helpers.make_request_vk('messages.send', random_id=helpers.randomid(),
                                        message=bot_response,
                                        peer_id=self.message.peer_id)

                bot_response = new_line
            else:
                bot_response += new_line

        code_logger.info(f'In SmartCommandHandler.info. len last info_message {len(bot_response)}')
        event_code = "SMART_ADD_INFO" if add_flag else "SMART_INFO"
        return BotAnswer(event_code, self.message, bot_response=bot_response)

    def add(self):
        count = models.SmartReply.objects.filter(chat_id=self.chat_db_object).count()
        if count >= SMARTREPLY_MAX_COUNT:
            raise LimitError(self.message, bot_response=self.usertext_dict['too_many_entries'])

        if self.regex:
            index = self.text.find(option_regex)
            text = self.text[index + 5:]
        else:
            index = self.text.find(option_add)
            text = self.text[index + 3:]
        text = text.split(self.delimiter)
        if len(text) != 2:
            raise WrongOptionError(self.message, bot_response=self.usertext_dict["absent_or_wrong_add"])

        trigger = text[0].strip() if self.regex else " ".join(
            text[0].lower().split())  # убираем все лишние пробелы, регистр и проч., если это не регулярка
        reply = text[1].strip()
        if len(trigger) > helpers.SMART_MAX_LEN or len(reply) > helpers.SMART_MAX_LEN:
            raise LimitError(self.message, bot_response=self.usertext_dict['too_long_entry'])
        if len(trigger) < 1 or len(reply) < 1:
            raise LimitError(self.message, bot_response=self.usertext_dict['empty_entry'])

        models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger=trigger, reply=reply,
                                         regex=self.regex)
        return self.info(add_flag=True)

    def off(self):
        if self.chat_db_object.smart_mode:
            self.chat_db_object.smart_mode = False
            self.chat_db_object.save()

            models.SmartReply.objects.filter(chat_id=self.chat_db_object).update(
                last_used=helpers.five_minutes_ago())

            return BotAnswer("SMART_OFF", self.message, bot_response=self.usertext_dict['off'])
        else:
            raise AlreadyDoneError(self.message, bot_response=self.usertext_dict['already_off'])

    def on(self):
        if self.chat_db_object.smart_mode:
            raise AlreadyDoneError(self.message, bot_response=self.usertext_dict['already_on'])
        else:
            smart_messages_from_db = models.SmartReply.objects.filter(chat_id=self.chat_db_object)
            if len(smart_messages_from_db) > 0:
                self.chat_db_object.smart_mode = True
                self.chat_db_object.save()
                return BotAnswer("SMART_ON", self.message, bot_response=self.usertext_dict['on'])

            else:
                raise PrerequisitesError(self.message, bot_response=self.usertext_dict['zero_entries'])
