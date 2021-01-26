from vk.command_handler import *


class RemoveAction:

    def __init__(self, peer_id, setting_db_object, chat_db_object):
        self.chat_id = chat_db_object.chat_id
        self.peer_id = peer_id
        self.setting_db_object = setting_db_object
        self.local_id = chat_db_object.local_id

    def command(self):
        code_logger.debug(f'In RemoveAction command(), workgroup: {self.setting_db_object.kick_nonmembers_group_id}')

        chat_user_list = self.get_conversation_members()
        code_logger.debug(f'Chat_user_list: {chat_user_list}')

        if len(chat_user_list) == 0:
            bot_answer = "Чтобы кого-нибудь удалить из беседы, нужно сначала кого-нибудь в неё добавить."
            helpers.make_request_vk('messages.send', random_id=helpers.randomid(), message=bot_answer,
                                    peer_id=self.peer_id)
            return bot_answer

        list_group_nonmembers = self.get_group_nonmembers(chat_user_list)
        if list_group_nonmembers is False:
            bot_answer = f"Что-то пошло не так. Убедитесь, что группа {self.setting_db_object.kick_nonmembers_group_link} не заблокирована и не является закрытой."
            helpers.make_request_vk('messages.send', random_id=helpers.randomid(), message=bot_answer,
                                    peer_id=self.peer_id)
        else:
            non_member_user_list = sorted(list_group_nonmembers)
            code_logger.debug(f'Non_member_user_list: {non_member_user_list}')
            bot_answer = self.remove_nonmembers(non_member_user_list)
        return bot_answer


    def get_conversation_members(self):
        code_logger.debug('In get_conversation_members')
        members_content = helpers.make_request_vk('messages.getConversationMembers',
                                                  peer_id=self.chat_id)
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

    def remove_nonmembers(self, userlist):
        if len(userlist) == 0:
            bot_answer = f"Все участники чата состоят в группе {self.setting_db_object.kick_nonmembers_group_link}"
            helpers.make_request_vk('messages.send', random_id=helpers.randomid(), message=bot_answer,
                                    peer_id=self.peer_id)
            return bot_answer
        code_logger.debug('In remove non-members ')
        for user in userlist:
            helpers.make_request_vk('messages.removeChatUser', chat_id=self.local_id, member_id=user)
        bot_anwer = f"Deleted users: {userlist}. Nothing will be sent."
        return bot_anwer

    def get_group_nonmembers(self, users_list):

        user_ids = ', '.join(str(user) for user in users_list)

        content = helpers.make_request_vk('groups.isMember', user_ids=user_ids,
                                          group_id=self.setting_db_object.kick_nonmembers_group_id)
        code_logger.debug(f'In get_group_nonmembers, content of groups.isMember request {content}')
        not_members_list = []
        try:
            items = content['response']
            for item in items:
                if item['member'] == 0:
                    not_members_list.append(item['user_id'])
            if len(not_members_list) == 0:
                code_logger.debug('all no-admin and no-bot chat users are already your group members')
            return not_members_list
        except KeyError:

            return False
