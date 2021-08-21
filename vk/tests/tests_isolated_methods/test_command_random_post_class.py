from django.test import TestCase

from vk.command_handlers.RandomPostCommandHandler import RandomPostCommandHandler
from vk.helpers import random_post
from vk.tests.shared.shared_tests.common_valid_option_test import ValidOptionMixinTest


class ValidOptionTest(TestCase, ValidOptionMixinTest):  # 9+1
    command = f"{random_post}"
    command_handler = RandomPostCommandHandler

    @classmethod
    def setUpTestData(cls):
        super().setup_with_setting_object()

    def test_post(self):
        self.pipeline([])
        self.assertEqual(self.handler_object.option, "post")


