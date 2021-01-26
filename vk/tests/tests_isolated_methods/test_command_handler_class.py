
from django.test import TestCase

from vk import models
from vk.command_handlers.RandomPostCommandHandler import RandomPostCommandHandler
from vk.helpers import random_post
from vk.tests.shared.pipelines_and_setups import PipelinesAndSetUps
from web_vk.constants import test_personal_token, test_personal_expired_token, LOGIN_LINK


class CheckForPersonalToken(TestCase, PipelinesAndSetUps):
    command = f"{random_post}"
    command_handler = RandomPostCommandHandler
    setting_model = models.RandomPostSetting
    field_dict = dict()

    def setUp(self):
        self.setup_class()

    def test_no_profile(self):
        result = self.handler_object.check_for_personal_token()
        expected_result = (False, f"Чтобы пользоваться командой '{self.command} on', пройдите по ссылке {LOGIN_LINK}")
        self.assertEqual(expected_result, result)

    def test_expired_token(self):
        self.set_user_profile(test_personal_expired_token)
        result = self.handler_object.check_for_personal_token()
        expected_result = (False, f'Обновите токен по ссылке {LOGIN_LINK}')
        self.assertEqual(expected_result, result)

    def test_too_many_request_per_second(self):
        # can't find a good way to reproduce the error. #TODO: threads?
        pass

    def test_valid_token(self):
        self.set_user_profile(test_personal_token)
        result = self.handler_object.check_for_personal_token()
        expected_result = (True, None)
        self.assertEqual(expected_result, result)
