
from django.test import TestCase

import vk.tests.data_for_tests.group_links as links
from vk.tests.tests_actions.remove_action_tests_use_SEPARATELY.shared_remove import SharedRemove


class AllToRemoveChatTest(TestCase, SharedRemove):
    kick_nonmembers_group_link = links.normal_group1
    kick_nonmembers_group_id=links.normal_group1ID

    def setUp(self):
        super().setup()

    def test_chat(self):
        print(4)
        expected_answer = "Deleted users: [4003081, 15300039, 87448687]. Nothing will be sent."
        self.pipeline_chat(expected_answer)

