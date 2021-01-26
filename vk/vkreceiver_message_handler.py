import logging
from typing import Optional

from django.utils import timezone
import vk.models as models
import vk.text_parser
import vk.references as references
from vk.actions.SmartAction import SmartAction
from vk.command_handlers.RegistrationCommandHandler import RegistrationCommandHandler
import vk.helpers as helpers
from vk.actions.IntervalAction import IntervalAction

code_logger = logging.getLogger('code_process')



class MessageHandler:
    def __init__(self, event_dict):
        self.from_id: Optional[int] = event_dict.get('object__from_id', None)
        self.peer_id: Optional[int] = event_dict.get('object__peer_id', None)

        code_logger.debug(f'Message peer_id: {self.peer_id}')

        self.text: Optional[str] = event_dict.get('object__text', None)

        code_logger.info(f'TEXT: {self.text}')

        self.action_type: Optional[str] = event_dict.get('object__action__type', None)
        self.conversation_dict: dict = self.get_conversation_dict()
        self.conversation_type: Optional[str] = self.conversation_dict.get('response__items__peer__type', None)

        code_logger.info(f'MessageHandler, in get_conversation_function, conversation type: {self.conversation_type} ')

        self.service_message: bool = self.is_service_message()

    def is_service_message(self):
        if self.action_type:
            return True
        return False

    def get_conversation_dict(self):
        conversation_vk_object = helpers.make_request_vk('messages.getConversationsById', peer_ids=self.peer_id)
        conversation_dict = helpers.parse_vk_object(conversation_vk_object)
        return conversation_dict

    # def guess_conversation_type(self): # не удалять, пусть лежит
    #     if self.peer_id > 2000000000:
    #         return 'chat'
    #     return 'not a chat'  # Возможные значения: user, chat, group, email

    def is_admin_or_userchat(self):
        """Being an admin, bot is able to receive 'conversation object'.
        Otherwise self.conversation_type (and some other self fields) would be None
        """
        if self.conversation_type:
            return True

    def process(self):
        if self.is_admin_or_userchat():

            if self.conversation_type == 'chat':
                return self.chat_process()

            if self.conversation_type == 'user':
                return self.user_process()
            else:
                return f"Unknown conversation type '{self.conversation_type}'. Nothing will be sent."
        return "Bot is not an admin in this chat. Nothing will be sent."

    def chat_process(self):
        chat_info = references.ChatReference(self.conversation_dict)
        chat_db_object, created = models.Chat.objects.update_or_create(

            chat_id=self.peer_id,
            defaults={'local_id': chat_info.local_id, 'owner_id': chat_info.owner_id, 'title': chat_info.title,
                      'members_count': chat_info.members_count, 'last_contact': timezone.now()},
        )
        models.ChatMessage(
            text=self.text, chat_id=chat_db_object,
            from_user_id=self.from_id).save()
        text_object = vk.text_parser.TextParser(self)
        if not chat_db_object.conversation_is_registered:
            registration = RegistrationCommandHandler(text_object, chat_db_object)
            if registration.is_asking_for_registration():
                bot_answer = registration.chat_registration()
            else:
                bot_answer = "Conversation isn't registered. Nothing will be sent."
        elif text_object.status == 'command':
            return text_object.command_handler_caller(chat_db_object)

        elif text_object.status == 'wrong command':  # TODO: только для Вари, для кирила - не отправлять
            bot_answer = 'Такой команды нет.'
            helpers.make_request_vk('messages.send', random_id=helpers.randomid(), message=bot_answer,
                                    peer_id=self.peer_id)

        else:
            if not self.service_message:
                if not chat_db_object.smart_mode and not chat_db_object.interval_mode:
                    bot_answer = "It was normal message. Nothing will be sent."
                else:
                    bot_answer_smart = ""
                    bot_answer_interval = ""
                    if chat_db_object.smart_mode:
                        if not self.text or len(self.text) > helpers.SMART_MAX_LEN:
                            bot_answer_smart = "Not a valid message length for SmartAction. Nothing will be sent."
                        else:
                            smart_action = SmartAction(chat_db_object, self.text, self.from_id)
                            bot_answer_smart = smart_action.process()

                    if chat_db_object.interval_mode:
                        interval_action = IntervalAction(chat_db_object)
                        bot_answer_interval = interval_action.process()
                    bot_answer = bot_answer_smart + " " + bot_answer_interval

            else:
                bot_answer = "It was service message. Nothing will be sent."

        return bot_answer

    def user_process(self):
        code_logger.info('in user process')
        models.UserMessage(
            text=self.text, from_id=self.from_id).save()
        text = vk.text_parser.TextParser(self)
        if text.status == 'command':
            return text.command_handler_caller()

        if text.status == 'wrong command':
            bot_answer = "Такой команды нет."
            helpers.make_request_vk('messages.send', random_id=helpers.randomid(), message=bot_answer,
                                    peer_id=self.peer_id)
            return bot_answer

        return
