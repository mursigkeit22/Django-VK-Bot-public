import logging

import requests
site_logger = logging.getLogger('site')


def get_user_data(newly_received_token):
    url = 'https://api.vk.com/method/users.get'
    params = {'v': 5.92, 'access_token': newly_received_token,
              'fields': 'first_name, last_name, screen_name'}
    try:
        response = requests.post(url, params=params)
        user_data = response.json()['response'][0]
        site_logger.info(user_data)
        return {'first_name': user_data['first_name'], 'last_name': user_data['last_name'],
                'screen_name': user_data['screen_name'], }

    except KeyError as e:
        site_logger.info(e)
        return
