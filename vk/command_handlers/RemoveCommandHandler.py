from vk.command_handler import *


class RemoveCommandHandler(CommandHandler):
    def __init__(self, text_instance, chatconversation_db_object):
        super().__init__(text_instance, chatconversation_db_object)
        self.workgroup = None

    def process(self):
        if self.conversation_type == 'user':
            if super().get_chatconversation_db_object():
                self.process_user()
        elif self.conversation_type == 'chat':
            self.process_chat()

    def process_user(self):
        if super().check_for_owner() and super().check_for_admin() and super().check_for_registration() and super().limit_length(2):
            if not self.chatconversation_db_object.kick_nonmembers_mode:
                self.send_message(
                    'Cannot kick people. '
                    'First you should register the group like this: /grouppurge https://vk.com/link_to_the_group')
                return
            self.command()

    def process_chat(self):
        if super().check_for_owner() and super().limit_length(1):
            if not self.chatconversation_db_object.kick_nonmembers_mode:
                self.send_message(
                    'Cannot kick people. '
                    'First you should register the group like this: /grouppurge https://vk.com/link_to_the_group')
                return
            self.command()

    def command(self):
        self.workgroup = models.ChatSetting.objects.get(
            peer_id=self.chatconversation_db_object).remove_group
        code_logger.debug(f'In RemoveCommandHandler command(), workgroup: {self.workgroup}')
        chat_user_list = self.get_conversation_members()
        code_logger.debug(f'Chat_user_list: {chat_user_list}')
        if len(chat_user_list) == 0:
            super().send_message('Nobody to kick.')
            return
        non_member_user_list = self.get_group_nonmembers(chat_user_list)
        code_logger.debug(f'Non_member_user_list: {non_member_user_list}')
        local_id = self.chatconversation_db_object.local_id
        self.remove_nonmembers(local_id, non_member_user_list)

    def get_conversation_members(self):
        code_logger.debug('In get_conversation_members')
        members_content = helpers.make_request_vk('messages.getConversationMembers',
                                                  peer_id=self.chatconversation_db_object.peer_id)
        chat_user_list = self.simple_conversation_members(members_content)
        return chat_user_list

    def simple_conversation_members(self, content):
        items = content['response']['items']
        code_logger.debug(f'Simple_conversation_members items: {items}')
        users_list = []
        for item in items:
            if 'is_admin' not in item and 'is_owner' not in item and int(item['member_id'] > 0):
                users_list.append(item['member_id'])
        return users_list

    def remove_nonmembers(self, local_chat_id, userlist):
        if len(userlist) == 0:
            super().send_message(f'Everybody in chat is a member of your chosen group with ID {self.workgroup}.')
            return
        code_logger.debug('In remove non-members ')
        for user in userlist:
            helpers.make_request_vk('messages.removeChatUser', chat_id=local_chat_id, member_id=user)

    def get_group_nonmembers(self, users_list):
        user_ids = ', '.join(str(user) for user in users_list)
        content = helpers.make_request_vk('groups.isMember', user_ids=user_ids, group_id=self.workgroup)
        code_logger.debug(f'In get_group_nonmembers, content of groups.isMember request {content}')
        not_members_list = []
        items = content['response']
        for item in items:
            if item['member'] == 0:
                not_members_list.append(item['user_id'])
        if len(not_members_list) == 0:
            code_logger.debug('all no-admin and no-bot chat users are already your group members')
        return not_members_list
