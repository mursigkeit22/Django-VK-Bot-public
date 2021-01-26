import datetime
import time
from typing import Optional

import requests
import logging

from django.utils import timezone

from botsite.models import UserProfile
from web_vk.constants import BOT_TOKEN

code_logger = logging.getLogger('code_process')
send_logger = logging.getLogger('send')
request_vk_logger = logging.getLogger("request_vk")

remove = "/kick"  # TODO: rename  for Kiril '/purge'  instead of '/kick'
interval = "/interval"
random_post = "/post"
new_post = "/newpost"
interval_phrase = "/phrase"
registration = "/reg"
smart = "/smart"
smart_reply = "/smartreply"

SMART_MAX_LEN = 100


def randomid():
    x = time.time()
    return int(x * 10000000)


class PersonalTokenException(Exception):
    pass


def make_request_vk(method: str, personal: bool = False, chat_owner: Optional[int] = None, **params):
    url = 'https://api.vk.com/method/' + method
    if method == 'messages.send':
        log_line = ''
        for key, value in params.items():
            temp_line = f'{key}: {value} '
            log_line += temp_line
        send_logger.info(log_line)

    parameters = {'v': 5.92, 'access_token': BOT_TOKEN}
    if personal:
        if not chat_owner:
            code_logger.info("raising RequestVK('Chat owner is not provided when personal parameter is True.')")
            raise PersonalTokenException("Chat owner was not provided when 'personal' argument was True.") # TODO: проверить, попадает ли в джанго лог
        try:
            user_profile = UserProfile.objects.get(vk_id=chat_owner)
            parameters = {'v': 5.92, 'access_token': user_profile.vk_token}
        except UserProfile.DoesNotExist as e:
            raise PersonalTokenException(str(e) + f' Chat owner: {chat_owner}.')

    parameters.update(params)
    response = requests.post(url, data=parameters)
    code_logger.info(f'method: {method}, {response}')
    request_vk_logger.info(f'method: {method}, {response.json()}')

    return response.json()


def parse_vk_object(content: dict, new_dict: dict = None, prefix: str = ''):
    new_dict = new_dict or dict()
    if prefix:
        prefix = prefix + '__'
    for key, item in content.items():
        if type(item) == list and len(item) == 1 and type(item[0]) == dict:
            new_dict = parse_vk_object(item[0], new_dict, prefix + str(key))
        elif type(item) == dict:
            new_dict = parse_vk_object(item, new_dict, prefix + str(key))
        else:
            new_dict[prefix + str(key)] = item
    return new_dict


def five_minutes_ago():
    return timezone.now() - datetime.timedelta(minutes=5)
