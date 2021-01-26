import logging
import random
import vk.models as models

import vk.helpers as helpers

code_logger = logging.getLogger('code_process')


class IntervalAction:

    def __init__(self, chat_db_object):
        self.chat_db_object = chat_db_object
        self.peer_id = chat_db_object.chat_id
        self.local_id = chat_db_object.local_id
        code_logger.debug(f'IntervalAction. chat_db_object: {self.chat_db_object}')
        self.count = self.counter()

    def counter(self):
        till_endpoint = self.chat_db_object.messages_till_endpoint
        interval = self.chat_db_object.interval
        new_till_endpoint = till_endpoint - 1
        code_logger.debug(f'IntervalAction counter. till_endpoint: {till_endpoint}, '
                          f'interval: {interval}, new_till_endpoint {new_till_endpoint}')
        return new_till_endpoint

    def process(self):
        if self.count == 0:
            phrases_from_db = models.IntervalPhrase.objects.filter(chat_id=self.peer_id)
            message = random.choice(phrases_from_db).phrase
            self.chat_db_object.messages_till_endpoint = self.chat_db_object.interval
            self.chat_db_object.save()

            helpers.make_request_vk('messages.send', random_id=helpers.randomid(), message=message,
                                    peer_id=self.peer_id)
            code_logger.debug(
                f'IntervalAction. new_till_endpoint == {self.chat_db_object.interval}, saving and sending is supposed to be done.')
            bot_answer = f"IntervalAction. message was sent: {message}"
        else:
            self.chat_db_object.messages_till_endpoint = self.count
            code_logger.debug(
                f'IntervalAction. setting_db_object.till_endpoint: {self.chat_db_object.messages_till_endpoint}')
            self.chat_db_object.save()
            bot_answer = "IntervalAction. Nothing will be sent."
            code_logger.debug('IntervalAction. new_till_endpoint != 0, saving is supposed to be done')
        return bot_answer
