import logging
from vk.vkreceiver_message_handler import MessageHandler
import vk.helpers as helpers

code_logger = logging.getLogger('code_process')


class EventHandler:
    def __init__(self, vkreceiver_object):
        self.event_dict = helpers.parse_vk_object(vkreceiver_object)

        code_logger.debug('in EventHandler, event is parsed, new_dict is below:')
        code_logger.debug(self.event_dict)

        self.event_type = self.event_dict.get('type', None)
        self.vk_secret_key = self.event_dict.get('secret', None)

    def process(self):
        code_logger.info('=======================')
        code_logger.debug('in EventHandler.process')

        if self.event_type == 'message_new':
            answer = MessageHandler(self.event_dict).process()  # for testing
            return answer
        else:
            return self.event_type
            # 'message_reply' это исходящее сообщение бота В ЛИЧНЫХ СООБЩЕНИЯХ,
            # чтобы их получать, нужно поставить настройку на странице бота
