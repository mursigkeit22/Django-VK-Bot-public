from django.test import TestCase

from vk import models
from vk.command_handlers.RandomPostCommandHandler import RandomPostCommandHandler
from vk.helpers import random_post, option_on
from vk.tests.shared.pipelines_and_setups import PipelinesAndSetUps
from vk.usertext import common_dict
from vk.vkbot_exceptions import UserProfileError
from web_vk.constants import test_personal_token, test_personal_expired_token, LOGIN_LINK


class CheckForPersonalToken(TestCase, PipelinesAndSetUps):
    command = random_post
    command_handler = RandomPostCommandHandler
    setting_model = models.RandomPostSetting
    field_dict = dict()

    def setUp(self):
        self.setup_command_handler_object()

    def test_no_profile(self):
        self.handler_object.option = {option_on}

        with self.assertRaises(UserProfileError) as context:
            self.handler_object.check_for_personal_token()
        self.assertEqual('USER_PROFILE_ERROR', context.exception.error_code)
        bot_response = common_dict["not_login"].substitute(
            command=f'{self.command} {self.handler_object.option}')
        self.assertEqual(bot_response, context.exception.bot_response)

    def test_expired_token(self):
        self.handler_object.option = {option_on}
        self.set_user_profile(test_personal_expired_token)

        with self.assertRaises(UserProfileError) as context:
            self.handler_object.check_for_personal_token()
        self.assertEqual('USER_PROFILE_ERROR', context.exception.error_code)
        bot_response = common_dict["refresh_token"].substitute(
            command=f'{self.command} {self.handler_object.option}')
        self.assertEqual(bot_response, context.exception.bot_response)



    def test_too_many_request_per_second(self):
        # can't find a good way to reproduce the error. #TODO: threads?
        pass

    def test_valid_token(self):
        self.set_user_profile(test_personal_token)
        result = self.handler_object.check_for_personal_token()
        self.assertEqual(None, result)
