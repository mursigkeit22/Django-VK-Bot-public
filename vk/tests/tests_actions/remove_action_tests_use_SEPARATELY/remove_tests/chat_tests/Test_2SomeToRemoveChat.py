from django.test import TestCase

import vk.tests.data_for_tests.group_links as links
from vk.tests.tests_actions.remove_action_tests_use_SEPARATELY.shared_remove import SharedRemove


class SomeToRemoveChatTest(TestCase, SharedRemove):
    kick_nonmembers_group_link = links.gk4z
    kick_nonmembers_group_id = links.gk4zID

    def setUp(self):
        super().setup()

    def test(self):
        print(2)
        expected_answer = "Deleted users: [175227332]. Nothing will be sent."

        self.pipeline_chat(expected_answer)

