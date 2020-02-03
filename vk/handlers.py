import json
import logging
import random
from django.utils import timezone

import vk.helpers as vk_req
import vk.models as models
import vk.parsers as pars
import vk.data_classes as dat
from vk.command_handlers.RegistrationCommandHandler import RegistrationCommandHandler
import vk.helpers as helpers

code_logger = logging.getLogger('code_process')


# vk_request('messages.send', random_id= randomid(), message='from jupiter', peer_id=2000000001)


class PostRequestHandler:

    def __init__(self, request):
        self.post_request_content = json.loads(request.body)

    def process(self):
        code_logger.info('=======================')
        code_logger.debug('in PostHandler.process')
        event = EventHandler(self.post_request_content)

        if event.type == 'confirmation':
            return event.type
        if event.type == 'message_new':  # TODO: IF TYPE 'message_reply' - тоже в счетчик и в базу
            event.message.process()
            return


# в каждом чате есть счетчик сообщений conversation_message_id' и он начинает отсчитываться с самого начала, админство не влияет

# def is_member(user_id, group):
#     url = 'https://api.vk.com/method/groups.isMember'
#     params = {
#         'group_id': group,
#         'access_token': token,
#         'v': 5.92,
#         'user_id': user_id,
#     }
#     r = requests.post(url, params=params)
#     return r.json()['response']  # TODO errors
#
class EventHandler:
    """
    List (not exhaustive) of possible event types can be found here https://vk.com/dev/groups_events
    Event types for bot to handle can be chosen on bot api&server page.

    
    """

    def __init__(self, content):
        self.event_dict = self.parse_event(content)
        code_logger.debug('in EventHandler, event is parsed, new_dict is below:')
        code_logger.debug(self.event_dict)
        self.type = self.event_dict.get('type', None)
        self.secret_key = self.event_dict.get('secret', None)
        self.message = self._init_message_if_exists()

    def _init_message_if_exists(self):
        if self.type == 'message_new':  # todo: message_reply? for userchat only
            code_logger.debug('self.type == "message_new", in EventHandler')
            return MessageHandler(self.event_dict)
        return None

    def parse_event(self, content: dict, new_dict=None, prefix=''):  # TODO: откуда тут внезапно вообще парсер???
        new_dict = new_dict or dict()
        if prefix:
            prefix = prefix + '_'
        for key, item in content.items():
            if type(item) != dict:
                new_dict[prefix + str(key)] = item
            if type(item) == dict:
                self.parse_event(item, new_dict, prefix + str(key), )

        return new_dict


class MessageHandler:
    def __init__(self, event_dict):
        self.from_id = event_dict.get('object_from_id', None)
        self.peer_id = event_dict.get('object_peer_id', None)
        code_logger.debug(f'Message peer_id: {self.peer_id}')
        self.text = event_dict.get('object_text', None)
        code_logger.info(f'TEXT: {self.text}')
        self.action_type = event_dict.get('object_action_type', None)
        self.action_member_id = event_dict.get('object_action_member_id', None)
        self.conversation_type, self.conversation_dict = self.get_conversation()
        self.message_id = event_dict.get('object_conversation_message_id', None)
        self.service_message = self.check_if_service_message()

    def check_if_service_message(self):
        if self.action_type:
            return True
        return False

    def get_conversation(self):
        response_content = vk_req.make_request_vk('messages.getConversationsById', peer_ids=self.peer_id)
        response_dict = helpers.parse_response(response_content, dict(), prefix='')
        type = response_dict.get('response__items__peer__type',
                                 None)  # user, chat, group, email, None (when bot isn't admin)
        code_logger.info(f'in get_conversation_function, type: {type} ')
        return type, response_dict

    def guess_conversation_type(self):
        peer_id = str(self.peer_id)
        if len(peer_id) == 10 and peer_id[0] == '2':
            return 'chat'
        return 'something else'  # TODO: Find out and fix.  #type (string) — тип. Возможные значения: user, chat, group, email

    def check_if_allowed_to_write(self):   # Todo: single responsibility
        """ бот может не быть админом только в чате. когда юзер, значит, юзер запретил ему писать (не проверено!).
        с остальными типами вообще неизвестно.
        оставляем угадывание типа конверсейшна, остальные типы поищем потом.
      """
        if self.conversation_type:
            return True
        if not self.conversation_type:
            guessed_type = self.guess_conversation_type()
            if guessed_type == 'chat':
                chatconversation_object = models.ChatConversation.objects.filter(peer_id=self.peer_id)   # если уже был админом, то найдется
                code_logger.info(f'In MessageHandler in check_if_admin (False). Chatconversation_object: {chatconversation_object}')
                if chatconversation_object:        #TODO: тех, кто не сделал бота админом, записывать в базу тоже
                    models.ChatMessage(
                        text=self.text, peer_id=chatconversation_object[0], message_id=self.message_id,
                        user_id=self.from_id).save()
            if guessed_type == 'something else': # for future
                pass
            return False

    def process(self):
        if self.check_if_allowed_to_write():

            if self.conversation_type == 'chat':
                self.chat_process()

            elif self.conversation_type == 'user':
                self.user_process()

    def chat_process(self):
        chat_info = dat.ChatConversationInfo(self.conversation_dict)
        chatconversation_db_object, created = models.ChatConversation.objects.update_or_create(
            peer_id=self.peer_id, local_id=chat_info.local_id, owner_id=chat_info.owner_id,
            type=chat_info.type,
            defaults={'members_count': chat_info.members_count, 'last_contact': timezone.now()},
        )
        models.ChatMessage(
            text=self.text, peer_id=chatconversation_db_object, message_id=self.message_id,
            user_id=self.from_id).save()
        text = pars.TextParser(self)
        if not chatconversation_db_object.conversation_is_registered:
            RegistrationCommandHandler(text, chatconversation_db_object).chat_registration()
            return
        if text.status == 'command':
            text.command_handler_caller(chatconversation_db_object)
            return
        if text.status == 'wrong command':  # только для Вари, для кирила - пасс
            # pass
            vk_req.make_request_vk('messages.send', random_id=vk_req.randomid(), message='No such command.',
                                   peer_id=self.peer_id)
        else:
            if chatconversation_db_object.interval_mode and not self.service_message:
                Action(chatconversation_db_object).interval_action()
        return

    def user_process(self):
        code_logger.info('in user process')
        user_info = dat.UserConversationInfo(self.conversation_dict)
        userconversation_db_object, created = models.UserConversation.objects.update_or_create(
            peer_id=user_info.peer_id, local_id=user_info.local_id,
            type=user_info.type,
            defaults={'last_contact': timezone.now()},
        )
        models.UserMessage(
            text=self.text, peer_id=userconversation_db_object, message_id=self.message_id,
            user_id=self.from_id).save()
        text = pars.TextParser(self)
        if text.status == 'command':
            text.command_handler_caller()
            return
        if text.status == 'wrong command':
            vk_req.make_request_vk('messages.send', random_id=vk_req.randomid(), message='No such command.',
                                   peer_id=self.peer_id)

        return


class Action:
    def __init__(self, conversation_db_object):
        self.conversation_db_object = conversation_db_object
        self.peer_id = conversation_db_object.peer_id
        self.local_id = conversation_db_object.local_id

    def interval_action(self):
        setting_db_object = models.ChatSetting.objects.get(peer_id=self.peer_id)
        code_logger.debug(f'setting_db_object: {setting_db_object}')
        till_endpoint = setting_db_object.messages_till_endpoint
        interval = setting_db_object.interval
        new_till_endpoint = till_endpoint - 1
        code_logger.debug(f'in Action subtract_endpoint. till_endpoint: {till_endpoint}, '
                          f'interval: {interval}, new_till_endpoint {new_till_endpoint}')

        if new_till_endpoint == 0:
            phrases_from_db = models.IntervalPhrase.objects.filter(peer_id=self.peer_id)
            message = random.choice(phrases_from_db).phrase
            setting_db_object.messages_till_endpoint = interval
            setting_db_object.save()
            vk_req.make_request_vk('messages.send', random_id=vk_req.randomid(), message=message,
                                   peer_id=self.peer_id)
            code_logger.debug(
                'in interval_action, new_till_endpoint == 0,saving and sending is supposed to be done')

        else:
            setting_db_object.messages_till_endpoint = new_till_endpoint
            code_logger.debug(f'setting_db_object.till_endpoint: {setting_db_object.messages_till_endpoint}')
            setting_db_object.save()
            code_logger.debug('in interval_action, new_till_endpoint != 0, saving is supposed to be done')
