import random

from vk import helpers
from vk.bot_answer import BotAnswer
from vk.command_handler import code_logger
from vk.helpers import PersonalTokenException, random_post
from vk.input_message import InputMessage
from vk.usertext import common_dict
from vk.vkbot_exceptions import UserProfileError, GroupValidationError, LimitError, VKBotException, PrerequisitesError


@helpers.class_logger()
class RandomPostAction:
    def __init__(self, setting_db_object, chat_db_object, input_message: InputMessage):
        """ we need chat_db_object.owner_id for calling vk methods with personal token
         - tokens are linked to user profiles."""
        self.input_message = input_message
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
            # this shouldn't happen, random_post option should be true only after profile check
            code_logger.info("In RandomPostAction.get_post_quantity. PersonalTokenException: " + str(e))

            raise UserProfileError(self.input_message,
                                   error_description=f"An error message is sent to chat owner.",
                                   bot_response={"message": common_dict["not_login"].substitute(command=random_post),
                                                 "peer_id": self.chat_owner})

        try:
            return post_quantity['response']['count']

        except KeyError as e:
            code_logger.info(post_quantity)
            if post_quantity['error']['error_code'] == 6:
                raise LimitError(self.input_message,
                                 error_description=f"RandomPostAction. get_post_quantity. {post_quantity['error']}")

            if post_quantity['error']['error_code'] == 15:
                raise GroupValidationError(self.input_message, bot_response=common_dict["group_turned_bad"].substitute(
                    group_link=self.setting_db_object.random_post_group_link))

            if post_quantity['error']['error_code'] == 5:

                raise UserProfileError(self.input_message, error_description="An error message is sent to chat owner.",
                                       bot_response={
                                           "message": common_dict["refresh_token"].substitute(command=random_post),
                                           "peer_id": self.chat_owner})

            else:  # maybe another error exists
                raise VKBotException(self.input_message,
                                     error_description=f"RandomPostAction. get_post_quantity. unknown KeyError: {e}")

    def choose_post(self, post_quantity):
        max_offset = post_quantity - 1
        code_logger.info(f'In RandomPostAction.choose_post. Max offset: {max_offset}')
        random_offset = random.randint(0, max_offset)
        code_logger.info(f'In RandomPostAction.choose_post. Random offset: {random_offset}')
        one_post = helpers.make_request_vk('wall.get', personal=True, chat_owner=self.chat_owner, count=1,
                                           offset=random_offset, owner_id=self.workgroup)['response']['items'][0]
        return one_post

    def prepare_attachment(self, one_post):
        one_post_id = one_post['id']
        code_logger.info(f'ID of the post that will be sent: {one_post_id}')
        attachment = 'wall' + self.workgroup + '_' + str(one_post_id)
        return attachment

    def process(self):
        self.workgroup = '-' + str(self.setting_db_object.random_post_group_id)
        code_logger.info(f'In RandomPostAction.process. ID of the workgroup: {self.workgroup}')
        post_quantity = self.get_post_quantity()

        code_logger.debug(
            f'In RandomPostAction.process. Number of posts on the workgroup wall: {post_quantity}')

        if post_quantity == 0:
            raise PrerequisitesError(self.input_message, bot_response="Стена пуста.")

        one_post = self.choose_post(post_quantity)
        attachment = self.prepare_attachment(one_post)
        return BotAnswer("RANDOM_POST_SENT", self.input_message,
                         bot_response={
                             "attachment": attachment, "peer_id": self.chat_id,
                             # /post command can be called from user chat, that's why we have to use chat_id
                         })
