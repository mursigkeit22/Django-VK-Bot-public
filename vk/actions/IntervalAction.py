import logging
import random

import vk.models as models
from vk import helpers
from vk.bot_answer import BotAnswer
from vk.input_message import InputMessage

code_logger = logging.getLogger('code_process')


@helpers.class_logger()
class IntervalAction:

    def __init__(self, chat_db_object, input_message: InputMessage):
        self.input_message = input_message
        self.chat_db_object = chat_db_object
        self.chat_id = chat_db_object.chat_id
        self.local_id = chat_db_object.local_id
        self.count = self.counter()

    def counter(self):
        till_endpoint = self.chat_db_object.messages_till_endpoint
        interval = self.chat_db_object.interval
        new_till_endpoint = till_endpoint - 1
        code_logger.info(f'In IntervalAction.counter. till_endpoint: {till_endpoint}, '
                         f'interval: {interval}, new_till_endpoint {new_till_endpoint}')
        return new_till_endpoint

    def process(self):
        if self.count == 0:
            phrases_from_db = models.IntervalPhrase.objects.filter(chat_id=self.chat_id)
            message = random.choice(phrases_from_db).phrase
            self.chat_db_object.messages_till_endpoint = self.chat_db_object.interval
            self.chat_db_object.save()

            code_logger.info(
                f'In IntervalAction.process.  new_till_endpoint = {self.chat_db_object.interval} saved to db. '
                f'Interval message will be sent.')

            bot_answer = BotAnswer("INTERVAL_MESSAGE_SENT", self.input_message, bot_response=message,)

        else:
            self.chat_db_object.messages_till_endpoint = self.count
            self.chat_db_object.save()
            bot_answer = BotAnswer("INTERVAL_COUNTER", self.input_message)
            code_logger.info(f'In IntervalAction.process. new_till_endpoint = {self.count} saved to db.')
        return bot_answer
