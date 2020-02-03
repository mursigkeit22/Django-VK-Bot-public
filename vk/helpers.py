import os
import time
import requests
import logging

code_logger = logging.getLogger('code_process')
send_logger = logging.getLogger('send')

bot_token = os.environ['BOT_TOKEN']
personal_token = os.environ['PERSONAL_TOKEN']


def randomid():
    x = time.time()
    return int(x * 10000000)


def make_request_vk(method, personal=False, **params):
    url = 'https://api.vk.com/method/' + method
    if method == 'messages.send':
        log_line = ''
        for key, value in params.items():
            temp_line = f'{key}: {value} '
            log_line += temp_line
        send_logger.info(log_line)

    parameters = {'v': 5.92, 'access_token': bot_token}
    if personal:
        parameters = {'v': 5.92, 'access_token': personal_token}
    parameters.update(params)
    response = requests.post(url, data=parameters)
    code_logger.info(f'method: {method}, {response}')

    return response.json()


def parse_response(content, new_dict, prefix=''):
    if prefix:
        prefix = prefix + '__'
    for key, item in content.items():
        if type(item) == list and len(item) == 1 and type(item[0]) == dict:
            for el in item:
                parse_response(el, new_dict, prefix + str(key))
        elif type(item) == dict:
            parse_response(item, new_dict, prefix + str(key), )
        else:
            new_dict[prefix + str(key)] = item

    return new_dict
