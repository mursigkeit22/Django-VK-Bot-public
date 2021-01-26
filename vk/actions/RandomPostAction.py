import random

from vk import helpers
from vk.command_handler import code_logger
from vk.helpers import PersonalTokenException
from web_vk.constants import LOGIN_LINK


class RandomPostAction:
    def __init__(self, peer_id, setting_db_object, chat_db_object):
        self.peer_id = peer_id
        self.setting_db_object = setting_db_object
        self.chat_id = chat_db_object.chat_id
        self.chat_owner = chat_db_object.owner_id
        self.workgroup = None

    def get_post_quantity(self):
        """ will get Key Error when:
        - too many requests per second (more than 3);
            {'error': {'error_code': 6, 'error_msg': 'Too many requests per second',...
        - group is blocked;
            {'error': {'error_code': 15, 'error_msg': 'Access denied: group is blocked',...
        - wall is available only for community members
            {'error': {'error_code': 15, 'error_msg': 'Access denied: this wall available only for community members'...
        - user authorization failed: invalid access_token
            {'error': {'error_code': 5, 'error_msg': 'User authorization failed: invalid access_token (4).',...
        """

        try:
            post_quantity = helpers.make_request_vk('wall.get', personal=True, chat_owner=self.chat_owner, count=1,
                                                    owner_id=self.workgroup)
        except PersonalTokenException as e:
            code_logger.info("RandomPostAction: " + str(e))
            return False, e  # this shouldn't happen, random_post option should be true only after profile check

        try:
            return True, post_quantity['response']['count']

        except KeyError:
            code_logger.info(post_quantity)
            if post_quantity['error']['error_code'] == 6:
                return False, post_quantity['error']['error_msg']

            if post_quantity['error']['error_code'] == 15:
                bot_answer = f"Что-то пошло не так. Убедитесь, что группа {self.setting_db_object.random_post_group_link} не заблокирована и не является закрытой."
                helpers.make_request_vk('messages.send', random_id=helpers.randomid(), message=bot_answer,
                                        peer_id=self.chat_id)
                return False, bot_answer

            if post_quantity['error']['error_code'] == 5:
                bot_answer = f"Для корректной работы бота пройдите по ссылке {LOGIN_LINK}."
                helpers.make_request_vk('messages.send', random_id=helpers.randomid(), message=bot_answer,
                                        peer_id=self.chat_owner)
                return False, bot_answer

            else:  # maybe another error exists
                return False, post_quantity

    def choose_post(self, post_quantity):
        max_offset = post_quantity - 1
        code_logger.debug(f'RandomPostAction. choose_post function. Max offset: {max_offset}')
        random_offset = random.randint(0, max_offset)
        code_logger.debug(f'RandomPostAction. choose_post function. Random offset: {random_offset}')
        one_post = helpers.make_request_vk('wall.get', personal=True, chat_owner=self.chat_owner, count=1,
                                           offset=random_offset, owner_id=self.workgroup)['response']['items'][0]
        return one_post

    def send_post(self, one_post):
        one_post_id = one_post['id']
        code_logger.debug(f'ID of the post that will be sent: {one_post_id}')
        attachment = 'wall' + self.workgroup + '_' + str(one_post_id)
        helpers.make_request_vk(
            'messages.send', random_id=helpers.randomid(),
            attachment=attachment, peer_id=self.chat_id)

    def process(self):
        code_logger.debug('RandomPostAction. process function.')
        self.workgroup = '-' + str(self.setting_db_object.random_post_group_id)
        code_logger.debug(f'RandomPostAction. process function. ID of the workgroup: {self.workgroup}')
        proceed, bot_answer = self.get_post_quantity()
        if not proceed:
            return bot_answer
        post_quantity = bot_answer

        code_logger.debug(
            f'RandomPostAction. process function. Number of posts on the workgroup wall: {post_quantity}')

        if post_quantity == 0:
            bot_answer = "Стена пуста."
            helpers.make_request_vk('messages.send', random_id=helpers.randomid(), message=bot_answer,
                                    peer_id=self.peer_id)
            return bot_answer
        one_post = self.choose_post(post_quantity)
        self.send_post(one_post)
        bot_answer = "random post is sent."
        return bot_answer
