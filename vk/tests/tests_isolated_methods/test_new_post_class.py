from django.test import TestCase

from vk.command_handlers.NewPostCommandHandler import NewPostCommandHandler
from vk.helpers import newpost

from vk.tests.shared.shared_tests.common_valid_option_test import ValidOptionMixinTest


class ValidOptionTest(TestCase, ValidOptionMixinTest):  # 9
    command = f"{newpost}"
    command_handler = NewPostCommandHandler

    @classmethod
    def setUpTestData(cls):
        super().setup_with_setting_object()

