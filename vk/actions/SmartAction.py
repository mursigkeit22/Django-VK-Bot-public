import logging
import re
from datetime import timedelta

from django.utils import timezone

from vk import models, helpers
from vk.bot_answer import BotAnswer
from vk.input_message import InputMessage

code_logger = logging.getLogger('code_process')

COOLDOWN = timedelta(minutes=5)


@helpers.class_logger()
class SmartAction:
    def __init__(self, chat_db_object, input_message: InputMessage, ):
        self.chat_db_object = chat_db_object
        self.input_message = input_message
        self.text = " ".join(input_message.text.split())
        self.from_id = input_message.from_id

    def process(self):
        reply_object = self.choose_reply()

        if not reply_object:
            return BotAnswer("SMART_NOT_TRIGGER", self.input_message)

        reply_text = reply_object.reply
        if "@имя@" in reply_object.reply:
            name = self.get_name()
            reply_text = re.sub("@имя@", name, reply_text)
            code_logger.info("In SmartAction.process. Name changed.")

        reply_object.last_used = timezone.now()
        reply_object.save()

        return BotAnswer("SMART_REPLY_SENT", self.input_message,
                         bot_response=reply_text,
                         )

    def get_name(self):
        first_name = helpers.make_request_vk('users.get', user_ids=self.from_id)['response'][0]['first_name']
        return first_name

    def choose_reply(self):
        smart_replies = models.SmartReply.objects.filter(chat_id=self.chat_db_object).order_by('last_used')
        smart_replies_fullmatch = smart_replies.filter(trigger=self.text.lower(), regex=False, )
        if len(smart_replies_fullmatch) != 0:
            reply_object = smart_replies_fullmatch[0]
            code_logger.info(f"In SmartAction.choose_reply. Found fullmatch: id {reply_object.id}, text: {reply_object.reply}.")  #  TODO: how is it displayed in logs?
            return reply_object
        smart_replies_regex = smart_replies.filter(regex=True, )
        code_logger.info(f"In SmartAction.choose_reply. Fullmatch not found."
                         f" Number of possible regex replies:  {len(smart_replies_regex)}")
        for reply in smart_replies_regex:
            if re.search(reply.trigger, self.text):
                reply_object = reply
                code_logger.info(f'In SmartAction.choose_reply. Regex match found: {reply_object} ')
                return reply_object
        return None
