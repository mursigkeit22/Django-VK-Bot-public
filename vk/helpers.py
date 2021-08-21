import datetime
import time
import uuid
from functools import wraps
from typing import Optional

import requests
import logging

from django.utils import timezone
from log_request_id import local

from botsite.models import UserProfile
from web_vk.constants import BOT_TOKEN

code_logger = logging.getLogger('code_process')
send_logger = logging.getLogger('send')
request_vk_logger = logging.getLogger("request_vk")

kick = "/kick"  # TODO: rename  for Kiril '/purge'  instead of '/kick'
interval = "/interval"
random_post = "/post"
newpost = "/newpost"
interval_phrase = "/phrase"
registration = "/reg"
smart = "/smart"

option_off = "off"
option_on = "on"
option_info = "info"
option_remove = "remove"
option_add = "add"
option_group = "group"
option_delete = "delete"
option_all = "all"
option_regex = "regex"

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
            code_logger.info("In helpers.make_request_vk. raising PersonalTokenException('Chat owner is not provided when personal parameter is "
                             "True.')")
            raise PersonalTokenException(
                "Chat owner was not provided when 'personal' argument was True.")
        try:
            user_profile = UserProfile.objects.get(vk_id=chat_owner)
            parameters = {'v': 5.92, 'access_token': user_profile.vk_token}
        except UserProfile.DoesNotExist as e:
            raise PersonalTokenException(str(e) + f' Chat owner: {chat_owner}.')

    parameters.update(params)
    response = requests.post(url, data=parameters)
    code_logger.debug(f'In helpers.make_request_vk. method: {method}, {response}')
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


def add_log_unique_string():
    unique_string = uuid.uuid4()
    setattr(local, 'request_id', unique_string)


def declention_message(number: int):
    str_number = str(number)
    if str_number[-1] == "1" and str_number[-2:] != "11":
        return "сообщение"
    if str_number[-1] == "2" and str_number[-2:] != "12":
        return "сообщения"
    if str_number[-1] == "3" and str_number[-2:] != "13":
        return "сообщения"
    if str_number[-1] == "4" and str_number[-2:] != "14":
        return "сообщения"

    return "сообщений"


def func_logger(fn):
    """ Decorator takes a function and logs every time the function is called."""

    @wraps(fn)
    def inner(*args, **kwargs):
        code_logger.debug(f"In {fn.__qualname__}")
        result = fn(*args, **kwargs)
        return result

    return inner


def class_logger(exclude=None):
    """ Decorator takes a class and applies func_logger to every callable in the class.
    NB: static, class methods and properties are not included.
    """
    def inner_class_logger(cls, exclude_list=exclude):
        exclude_list = exclude_list or []
        for name, obj in vars(cls).items():
            if callable(obj) and name not in exclude_list:
                setattr(cls, name, func_logger(obj))
        return cls
    return inner_class_logger
