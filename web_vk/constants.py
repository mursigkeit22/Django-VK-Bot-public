import os

CONFIRMATION_RESPONSE = os.environ['CONFIRMATION_RESPONSE']
VK_SECRET = os.environ['VK_SECRET']


test_personal_token = os.environ['TEST_PERSONAL_VALID_TOKEN']
test_personal_expired_token = os.environ['TEST_PERSONAL_EXPIRED_TOKEN']

BOT_TOKEN = os.environ['BOT_TOKEN']

LOGIN_LINK = os.environ['LOGIN_LINK']

BOT_GROUPID = int(os.environ['BOT_GROUPID'])
BOT_NAME = os.environ['BOT_NAME']

VK_AUTH_ID = os.environ['VK_AUTH_ID']
VK_AUTH_SECRET = os.environ['VK_AUTH_SECRET']
VK_REDIRECT_URI = os.environ['VK_REDIRECT_URI']
VK_AUTHORIZATION_URL = 'http://oauth.vk.com/authorize'
VK_ACCESS_TOKEN_URL = 'https://oauth.vk.com/access_token/'
