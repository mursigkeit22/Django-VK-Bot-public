from django.test import TestCase

import vk.tests.data_for_tests.group_links as links
from vk.tests.tests_actions.remove_action_tests_use_SEPARATELY.shared_remove import SharedRemove


class GroupPrivateChatTest(TestCase, SharedRemove):
    """ NB: vkontakte doesn't return information about members of private groups.
    However such information is available for closed groups."""
    kick_nonmembers_group_link = links.private_group1
    kick_nonmembers_group_id = links.private_group1ID

    def setUp(self):
        super().setup()

    def test(self):
        print(1)
        expected_answer = f"Что-то пошло не так. Убедитесь, что группа {links.private_group1} не заблокирована и не является закрытой."
        self.pipeline_chat(expected_answer)
