from vk.command_handler import *
# todo: количество сохраняемых фраз за один раз
# todo: количество фраз на чат
DELIMITER = '|'


class PhraseCommandHandler(CommandHandler):
    def __init__(self, text_instance, chatconversation_db_object):
        super().__init__(text_instance, chatconversation_db_object)
        self.delimiter = DELIMITER
        self.text = self.text_instance.text
        self.option = None
        self.phrases = None
        self.id_to_remove = set()

    def process(self):
        code_logger.debug('PhraseCommandHandler')
        if self.conversation_type == 'user':
            if super().get_chatconversation_db_object():
                self.chatconversation_id = self.chatconversation_db_object.peer_id
                self.process_user()
        if self.conversation_type == 'chat':
            self.chatconversation_id = self.chatconversation_db_object.peer_id
            self.process_chat()

    def process_user(self):
        self.wordlist = self.wordlist[0:1] + self.wordlist[2:]
        if super().check_for_owner() and super().check_for_admin() and super().check_for_registration():
            if super().check_for_length(2):
                self.option = self.valid_option()
                if self.option:
                    self.command()

    def process_chat(self):
        if super().check_for_owner():
            if super().check_for_length(2):
                self.option = self.valid_option()
                if self.option:
                    self.command()

    def command(self):
        if self.option == 'info':
            self.info()
        elif self.option == 'add':
            self.add()
        elif self.option == 'remove':
            self.remove()
        elif self.option == 'remove all':
            self.remove_all()

    def remove(self):
        code_logger.debug('remove function.')
        phrases_from_db = models.IntervalPhrase.objects.filter(peer_id=self.chatconversation_id)
        if len(phrases_from_db) == 0:
            code_logger.debug('Nothing to remove: 0 phrases in database.')
            super().send_message("You don't have any phrases yet.")
            return

        id_from_db = {phrase.id for phrase in phrases_from_db}
        code_logger.info(f"All the phrases' ids from database: {id_from_db}")

        absent_ids = self.id_to_remove.difference(id_from_db)
        if len(absent_ids) != 0:
            super().send_message(f"You don't have phrases with ids: {absent_ids}")
        actual_id_to_remove = id_from_db.intersection(self.id_to_remove)
        if len(actual_id_to_remove) == 0:
            return

        if len(id_from_db) == len(actual_id_to_remove) and self.chatconversation_db_object.interval_mode:
            self.set_interval_mode_to_off()
            super().send_message("You are deleting all your phrases. Interval mode is set to off")

        phrases_from_db.filter(id__in=self.id_to_remove).delete()      # why not actual ids?
        super().send_message(f"Phrases with ids: {actual_id_to_remove} were deleted.")# todo: join to str

    def set_interval_mode_to_off(self):
        code_logger.debug('PhraseCommandHandler. set_interval_mode_to_off function. ')
        self.chatconversation_db_object.interval_mode = False
        self.chatconversation_db_object.save()
        models.ChatSetting.objects.filter(peer_id=self.chatconversation_db_object).update(
            interval=None,
            messages_till_endpoint=None,
        )

    def remove_all(self):
        phrases_from_db = models.IntervalPhrase.objects.filter(peer_id=self.chatconversation_id)
        if len(phrases_from_db) == 0:
            super().send_message("You don't have any phrases yet")
            return
        self.set_interval_mode_to_off()
        # self.chatconversation_db_object.interval_mode = False
        # self.chatconversation_db_object.save()
        # models.ChatSetting.objects.filter(peer_id=self.chatconversation_db_object).update(
        #     interval=None,
        #     messages_till_endpoint=None,
        # )

        phrases_from_db.delete()
        super().send_message('All your phrases are gone, interval mode is set to off.')

    def valid_option(self):
        code_logger.debug('valid_option function.')
        if self.wordlist[1] == 'info':
            return 'info'
        if self.wordlist[1] == 'add':
            if len(self.wordlist) > 2:
                return 'add'
            else:
                super().send_message('You should write your phrase after "add". For several phrases use delimiter "|".')
                return None
        if self.wordlist[1] == 'remove':
            if len(self.wordlist) > 2:
                if self.wordlist[2] == 'all':
                    return 'remove all'
                else:
                    for el in self.wordlist[2:]:
                        el = el.strip(',')
                        if el.isdigit():
                            self.id_to_remove.add(int(el))

                    code_logger.debug(f'self.wordlist[1] == remove. IDs of phrases to remove: {self.id_to_remove}')
                    if not self.id_to_remove:
                        super().send_message('You should write ids of phrases you want to remove after '
                                             'the word "remove". Command "/phrase info" will give you those ids')
                        return None
                    return 'remove'
        super().send_message('Please specify command option.')
        return None

    def add(self):
        if self.conversation_type == 'user':
            text = self.text.split()
            text = text[3:]
            text = ' '.join(text)
        else:
            text = self.text.split()
            text = text[2:]
            text = ' '.join(text)
        text = text.split(self.delimiter)
        phrases_list = [phrase.strip() for phrase in text if self.phrase_length_check(phrase.strip())]

        phrase_model_list = [models.IntervalPhrase(
                phrase=phrase, peer_id=self.chatconversation_db_object) for phrase in phrases_list]
        models.IntervalPhrase.objects.bulk_create(phrase_model_list)

        self.info()
        # TODO: probably not info, but only just saved phrases. but there will be difficulties with identical phrases

    def phrase_length_check(self, phrase):
        if len(phrase) > 0:
            if len(phrase) < 4000:
                return True
            else:
                code_logger.debug(f'Checking length of the phrase, phrase is too big: {len(phrase)}')
                super().send_message(f'Phrase "{phrase[0:1000]}..." is too long and will not be used in interval mode')
        return False

    def info(self):
        phrases_db_objects = models.IntervalPhrase.objects.filter(
            peer_id=self.chatconversation_id)

        if len(phrases_db_objects) == 1:
            super().send_message(f'You have 1 phrase saved.')
        else:
            super().send_message(f'You have {len(phrases_db_objects)} phrases saved.')
        info_message = ''

        for el in phrases_db_objects:
            new_line = f'id: {el.id}. Phrase: {el.phrase}\n'
            if len(info_message) + len(new_line) > 4100:
                code_logger.info('In phrase info, len(info_message) + len(new_line) > 4100 ')
                super().send_message(info_message)
                info_message = new_line
            else:
                info_message += new_line

        code_logger.info(f'len last info_message {len(info_message)}')

        super().send_message(info_message)



