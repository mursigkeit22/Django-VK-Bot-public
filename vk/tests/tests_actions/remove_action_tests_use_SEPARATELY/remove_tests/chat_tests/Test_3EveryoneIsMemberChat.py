from django.test import TestCase

import vk.tests.data_for_tests.group_links as links
from vk.tests.tests_actions.remove_action_tests_use_SEPARATELY.shared_remove import SharedRemove


class EveryoneIsMemberChatTest(TestCase, SharedRemove):
    # сначала удалить Иру
    kick_nonmembers_group_link = links.gk4z
    kick_nonmembers_group_id = links.gk4zID

    def setUp(self):
        super().setup()

    def test(self):
        expected_answer = f"Все участники чата состоят в группе {links.gk4z}"
        print(3)

        self.pipeline_chat(expected_answer)