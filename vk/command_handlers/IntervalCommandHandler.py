from vk.command_handler import *


class IntervalCommandHandler(CommandHandler):
    def __init__(self, text_instance, chatconversation_db_object):
        super().__init__(text_instance, chatconversation_db_object)

    def process(self):
        if self.conversation_type == 'user':
            if super().get_chatconversation_db_object():
                self.process_user()
        elif self.conversation_type == 'chat':
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

    def valid_option(self):
        if self.wordlist[1] == 'off':
            return 'off'
        if self.wordlist[1] == 'info':
            return 'info'
        if self.wordlist[1].isdigit():
            return int(self.wordlist[1])
        super().send_message(f"Command /interval doesn't have option {self.wordlist[1]}")
        return None

    def command(self):
        if self.option == 'off':
            self.chatconversation_db_object.interval_mode = False
            self.chatconversation_db_object.save()
            models.ChatSetting.objects.filter(peer_id=self.chatconversation_db_object).update(
                interval=None,
                messages_till_endpoint=None)
            super().send_message('Interval mode is off.')

        elif self.option == 'info':
            if self.chatconversation_db_object.interval_mode:
                setting_db_object = models.ChatSetting.objects.get(peer_id=self.chatconversation_db_object)
                interval = setting_db_object.interval
                messages_till_endpoint = setting_db_object.messages_till_endpoint
                super().send_message(f'Your interval: {interval}, next bot message in {messages_till_endpoint} messages.')
            else:
                super().send_message('Interval mode is off.')

        else:
            phrases_from_db = models.IntervalPhrase.objects.filter(peer_id=self.chatconversation_db_object.peer_id)
            if len(phrases_from_db) == 0:
                super().send_message("First add some phrases with '/phrase add' command, then you can set the interval")
                return
            if self.option < 2 or self.option > 1000:
                super().send_message("Interval value must be between 2 and 1000")
                return
            self.chatconversation_db_object.interval_mode = True
            self.chatconversation_db_object.save()
            models.ChatSetting.objects.filter(peer_id=self.chatconversation_db_object).update(
                                                                         interval=self.option,
                                                                         messages_till_endpoint=self.option)



