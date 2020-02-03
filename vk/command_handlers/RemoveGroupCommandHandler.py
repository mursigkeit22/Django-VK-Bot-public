from vk.command_handler import *
from vk.data_classes import GroupInfo


class RemoveGroupCommandHandler(CommandHandler):
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
        if self.wordlist[1].startswith(
                ('https://vk.com/', 'http://vk.com/')):
            group_name = self.wordlist[1].split('/vk.com/')[-1]
            response_content = helpers.make_request_vk('groups.getById', group_id=group_name)
            code_logger.info(response_content)
            group = GroupInfo(response_content)
            if group.screen_name == group_name and group.is_closed != 2:
                return group.group_id
            else:
                super().send_message(f"Group {self.wordlist[1]} can't be registered. "
                                     f"Check that your link is correct and that the group isn't private.")
                return None
        if self.wordlist[1] == 'off':
            return 'off'
        if self.wordlist[1] == 'info':
            return 'info'
        super().send_message(f"Command /grouppurge doesn't have option '{self.wordlist[1]}'.")
        return None

    def command(self):
        code_logger.debug('in command_group')

        if self.option == 'off':
            if self.chatconversation_db_object.kick_nonmembers_mode:
                self.chatconversation_db_object.kick_nonmembers_mode = False
                self.chatconversation_db_object.save()
                models.ChatSetting.objects.filter(peer_id=self.chatconversation_db_object).update(
                                                                                remove_group=None)
                super().send_message("Your registered group for /purge command is deleted. /purge command is off.")
            else:
                super().send_message("You don't have a registered group for /purge command.")

        elif self.option == 'info':
            if self.chatconversation_db_object.kick_nonmembers_mode:
                group = models.ChatSetting.objects.get(peer_id=self.chatconversation_db_object).remove_group
                super().send_message(f'For /purge command you have registered a group with ID {group}')
            else:
                super().send_message("You don't have a registered group for /purge command.")

        else:  # link like this: https://vk.com/club186232173
            self.chatconversation_db_object.kick_nonmembers_mode = True
            self.chatconversation_db_object.save()
            models.ChatSetting.objects.filter(peer_id=self.chatconversation_db_object).update(
                                                                        remove_group=self.option)
            super().send_message(f'Group {self.option} is registered successfully.')
