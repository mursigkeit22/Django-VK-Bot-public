from vk.command_handler import *


class RegistrationCommandHandler(CommandHandler):
    def __init__(self, text_instance, chatconversation_db_object):
        super().__init__(text_instance, chatconversation_db_object)

    def chat_registration(self):
        if self.wordlist == ['/reg', 'on'] and super().check_for_owner():
            self.chatconversation_db_object.conversation_is_registered = True
            self.chatconversation_db_object.save()
            models.ChatSetting.objects.update_or_create(peer_id=self.chatconversation_db_object)
            super().send_message(f'Conversation is successfully registered,'
                                 f' your conversation id: {self.chatconversation_db_object.peer_id}')

    def process(self):
        if self.conversation_type == 'user':    # может, проверять, есть ли вообще у этого юзера какие-то чаты, прежде чем реагировать на команды?
            super().send_message("You can't use /reg command in private dialog with Bot.")
        elif self.conversation_type == 'chat':
            self.process_chat()

    def process_chat(self):
        if super().check_for_owner():
            if super().check_for_length(2):
                if self.wordlist[1] == 'off':
                    self.option = 'off'
                elif self.wordlist[1] == 'info':
                    self.option = 'info'
                elif self.wordlist[1] == 'on':
                    super().send_message(f'Your conversation is already registered,'
                                         f' your conversation id: {self.peer_id}')
                else:
                    super().send_message(f"Command /reg doesn't have option {self.wordlist[1]}")
            if self.option:
                self.command()

    def command(self):
        if self.option == 'off':
            models.ChatSetting.objects.filter(peer_id=self.chatconversation_db_object).update(
                                                                  remove_group=None,
                                                                  interval=None,
                                                                  messages_till_endpoint=None,
                                                                  random_post_group=None,
                                                                  newpost_group=None,
                                                                  latest_newpost_timestamp=0,)
            self.chatconversation_db_object.interval_mode = False
            self.chatconversation_db_object.kick_nonmembers_mode = False
            self.chatconversation_db_object.random_post_mode = False
            self.chatconversation_db_object.newpost_mode = False
            self.chatconversation_db_object.conversation_is_registered = False  # TODO:how to combine?
            self.chatconversation_db_object.save()
            models.IntervalPhrase.objects.filter(peer_id=self.chatconversation_db_object).delete()
            super().send_message('Registration was successfully cancelled')

        if self.option == 'info':
            super().send_message(f'Your conversation id is {self.chatconversation_db_object.peer_id}')


