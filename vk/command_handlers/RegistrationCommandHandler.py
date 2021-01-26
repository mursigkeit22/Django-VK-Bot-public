from vk.command_handler import *


class RegistrationCommandHandler(CommandHandler):

    def is_asking_for_registration(self):
        is_owner, bot_answer = super().check_for_owner()
        if self.wordlist == ['/reg', 'on'] and is_owner:
            return True

        code_logger.debug("RegistrationCommandHandler, is_asking_for_registration: False")

    def chat_registration(self):

        self.chat_db_object.conversation_is_registered = True
        self.chat_db_object.save()
        models.NewPostSetting.objects.update_or_create(chat_id=self.chat_db_object)
        models.KickNonMembersSetting.objects.update_or_create(chat_id=self.chat_db_object)
        models.RandomPostSetting.objects.update_or_create(chat_id=self.chat_db_object)

        code_logger.debug(f"Conversation is registered with id {self.chat_db_object.chat_id}")

        answer = super().send_message(f'Беседа успешно зарегистрирована,'
                                      f' ID вашей беседы: {self.chat_db_object.chat_id}')
        return answer

    def process(self):
        if self.conversation_type == 'user':
            answer = super().send_message("Команду /reg нельзя использовать в личной беседе с ботом.")
            return answer
        elif self.conversation_type == 'chat':
            answer = self.process_chat()
            return answer

    def valid_option(self):
        if self.wordlist[1] == 'off':
            return True, "off"
        elif self.wordlist[1] == 'info':
            return True, "info"
        elif self.wordlist[1] == 'on':
            bot_answer = super().send_message(
                f'Эта беседа уже зарегистрирована, ID вашей беседы {self.peer_id}')
            return False, bot_answer
        else:
            bot_answer = super().send_message(f"У команды /reg нет опции {self.wordlist[1]}")
            return False, bot_answer

    def command(self):
        if self.option == 'off':
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
            self.chat_db_object.conversation_is_registered = False
            self.chat_db_object.save()
            models.IntervalPhrase.objects.filter(chat_id=self.chat_db_object).delete()
            bot_answer = super().send_message('Регистрация отменена: бот будет игнорировать вас и ваши команды.')
            return bot_answer

        if self.option == 'info':
            bot_answer = super().send_message(f'ID вашей беседы {self.chat_db_object.chat_id}')
            return bot_answer

    def process_user(self):
        pass
