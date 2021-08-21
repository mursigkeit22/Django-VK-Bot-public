import logging

from django.utils import timezone
import vk.models as models
import vk.text_parser
import vk.references as references
from vk.actions.SmartAction import SmartAction
from vk.command_handlers.RegistrationCommandHandler import RegistrationCommandHandler
import vk.helpers as helpers
from vk.actions.IntervalAction import IntervalAction
from vk.usertext import actions_dict, common_dict
from vk.vkbot_exceptions import NotAdminError, NotRegisteredError, LimitError, VKBotException, WrongCommandError
from vk.bot_answer import BotAnswer
from web_vk.constants import BOT_NAME1

code_logger = logging.getLogger('code_process')


@helpers.class_logger(['__init__', 'process'])
class MessageHandler:
    def __init__(self, input_message):
        self.message = input_message

    def is_admin_or_userchat(self):
        """In chat, being an admin, bot is able to receive 'conversation object'.
        Otherwise self.conversation_type (and some other self. fields) would be None.
        In private messages bot is always able to receive 'conversation object',
        even if not allowed to write.
        """
        if self.message.conversation_type:
            return True

    def process(self):
        if self.is_admin_or_userchat():

            if self.message.conversation_type == 'chat':
                return self.chat_process()

            if self.message.conversation_type == 'user':
                return self.user_process()
            else:
                return f"Unknown conversation type '{self.message.conversation_type}'. Nothing will be sent."
        raise NotAdminError(self.message)

    def chat_process(self):
        chat_info = references.ChatReference(self.message.conversation_dict)
        chat_db_object, created = models.Chat.objects.update_or_create(

            chat_id=self.message.peer_id,
            defaults={'local_id': chat_info.local_id, 'owner_id': chat_info.owner_id, 'title': chat_info.title,
                      'members_count': chat_info.members_count, 'last_contact': timezone.now()},
        )
        models.ChatMessage(
            text=self.message.text, chat_id=chat_db_object,
            from_user_id=self.message.from_id).save()  # !!!
        text_object = vk.text_parser.TextParser(self.message)
        if not chat_db_object.conversation_is_registered:
            registration = RegistrationCommandHandler(text_object.wordlist, self.message, chat_db_object)
            if registration.is_asking_for_registration():
                bot_answer = registration.chat_registration()
            else:
                raise NotRegisteredError(self.message,
                                         error_description=common_dict["not_registered"])

        elif text_object.status == 'command':
            return text_object.command_handler_caller(chat_db_object)

        elif text_object.status == 'wrong command':
            if 'варя' in BOT_NAME1:
                raise WrongCommandError(self.message, bot_response="Такой команды нет.")
            else:
                raise WrongCommandError(self.message, error_description="wrong command in chat.")

        else:
            if not self.message.service_message:
                if not chat_db_object.smart_mode and not chat_db_object.interval_mode:
                    bot_answer = BotAnswer('PLAIN_MESSAGE', self.message)
                else:
                    bot_answer_smart = None
                    bot_answer_interval = None
                    if chat_db_object.smart_mode:
                        # we don't want to propagate any exception here 'cause we need to process both modes.

                        try:

                            if not self.message.text or len(
                                    self.message.text) > helpers.SMART_MAX_LEN:
                                raise LimitError(self.message,
                                                 error_description=actions_dict["smart_wrong_message_length"])

                            else:
                                smart_action = SmartAction(chat_db_object, self.message)
                                bot_answer_smart = smart_action.process()
                        except VKBotException as e:
                            bot_answer_smart = BotAnswer.exception_to_answer(e)

                    if chat_db_object.interval_mode:
                        try:
                            interval_action = IntervalAction(chat_db_object, self.message)
                            bot_answer_interval = interval_action.process()
                        except VKBotException as e:
                            bot_answer_interval = BotAnswer.exception_to_answer(e)
                    if bot_answer_interval and not bot_answer_smart:
                        bot_answer = bot_answer_interval
                    elif bot_answer_smart and not bot_answer_interval:
                        bot_answer = bot_answer_smart
                    else:
                        bot_answer = (bot_answer_smart, bot_answer_interval)

            else:
                bot_answer = BotAnswer('SERVICE_MESSAGE', self.message, event_description="It was a service message. "
                                                                                          "Nothing will be sent.")

        return bot_answer

    def user_process(self):
        models.UserMessage(
            text=self.message.text, from_id=self.message.from_id).save()
        text = vk.text_parser.TextParser(self.message)
        if text.status == 'command':
            return text.command_handler_caller()

        if text.status == 'wrong command':
            raise WrongCommandError(self.message, bot_response="Такой команды нет.")
        if text.status == "call":
            return BotAnswer('BOT_CALL', self.message, event_description="bot was called in private chat with user.")

        else:
            return BotAnswer('PLAIN_MESSAGE', self.message, event_description="just a message in private chat with "
                                                                              "user.")
