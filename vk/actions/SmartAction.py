import datetime
from datetime import timedelta

from django.utils import timezone

from vk import models, helpers

COOLDOWN = timedelta(minutes=5)


class SmartAction:
    def __init__(self, chat_db_object, text, from_id):
        self.chat_db_object = chat_db_object
        self.peer_id = chat_db_object.chat_id
        self.text = text
        self.from_id = from_id

    def process(self):
        smart_replies = models.SmartReply.objects.filter(chat_id=self.chat_db_object, trigger=self.text.lower()).order_by(
            'last_used')
        if len(smart_replies) == 0:
            bot_answer = "No such trigger. Nothing will be sent."
            return bot_answer
        reply_object = smart_replies[0]

        delta = timezone.now() - reply_object.last_used
        if delta > COOLDOWN:

            helpers.make_request_vk('messages.send', random_id=helpers.randomid(), message=reply_object.reply,
                                    peer_id=self.peer_id)
            reply_object.last_used = timezone.now()
            reply_object.save()
            bot_answer = f"SmartReplyAction. Message was sent: '{reply_object.reply}'."
        else:
            bot_answer = f"SmartReplyAction. 5 minutes break for trigger '{self.text.lower()}'."
        return bot_answer
