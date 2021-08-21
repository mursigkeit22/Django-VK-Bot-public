import logging

from vk.bot_answer import BotAnswer
from vk.input_message import InputMessage
from vk.vkbot_exceptions import VKBotException
from vk.vkreceiver_message_handler import MessageHandler
import vk.helpers as helpers

code_logger = logging.getLogger('code_process')


class EventHandler:
    def __init__(self, vkreceiver_object: dict):

        self.event_dict = helpers.parse_vk_object(vkreceiver_object)

        self.event_type = self.event_dict.get('type', None)
        self.vk_secret_key = self.event_dict.get('secret', None)

    def process(self):
        code_logger.info('=======================')
        code_logger.info(
            f"In EventHandler.process. self.event_dict: {self.event_dict}")
        if self.event_type == 'message_new':
            input_message = InputMessage(self.event_dict)
            try:
                result = MessageHandler(input_message).process()
            except VKBotException as e:
                result = BotAnswer.exception_to_answer(e)
            for answer in result:
                if answer.check_if_need_send():
                    answer.send_message()

            return result
        else:
            return self.event_type

            # 'message_reply' - это исходящее сообщение бота В ЛИЧНЫХ СООБЩЕНИЯХ.
            # Чтобы их получать, нужно поставить соответствующую настройку на странице бота.
