from unittest import mock
from django.test import TestCase

import vk.tests.data_for_tests.group_links as links
from vk import helpers
from vk.tests.tests_actions.remove_action_tests_use_SEPARATELY.shared_remove import SharedRemove


# All 4 people should be in chat


def side_effect_remove_nonmembers(userlist):
    if len(userlist) == 0:
        bot_answer = f"Все участники чата состоят в группе {links.gk4z}"  # for EveryoneIsMemberTest
        return bot_answer
    bot_answer = f"Deleted users: {userlist}. Nothing will be sent."  # for AllToRemoveTest
    return bot_answer


class AllToRemoveTest(TestCase, SharedRemove):
    kick_nonmembers_group_link = links.normal_group1
    kick_nonmembers_group_id = links.normal_group1ID

    def setUp(self):
        super().setup()

    @mock.patch('vk.actions.RemoveAction.RemoveAction.remove_nonmembers')
    def test(self, mock_remove_nonmembers, side_effect=side_effect_remove_nonmembers):
        mock_remove_nonmembers.side_effect = side_effect

        expected_answer = "Deleted users: [4003081, 15300039, 87448687, 175227332]. Nothing will be sent."
        self.pipeline_chat(expected_answer)
        self.pipeline_user(expected_answer)


class SomeToRemoveTest(TestCase, SharedRemove):
    kick_nonmembers_group_link = links.gk4z
    kick_nonmembers_group_id = links.gk4zID

    def setUp(self):
        super().setup()

    @mock.patch('vk.actions.RemoveAction.RemoveAction.remove_nonmembers')
    def test(self, mock_remove_nonmembers, side_effect=side_effect_remove_nonmembers):
        mock_remove_nonmembers.side_effect = side_effect
        expected_answer = "Deleted users: [175227332]. Nothing will be sent."

        self.pipeline_user(expected_answer)
        self.pipeline_chat(expected_answer)


orig = helpers.make_request_vk

def side_effect_make_request(*args, **kwargs, ):

    if "message" in kwargs:
        return kwargs.get("message")
    else:
        return orig(*args, **kwargs,)



class GroupPrivateTest(TestCase, SharedRemove):
    kick_nonmembers_group_link = links.private_group1
    kick_nonmembers_group_id = links.private_group1ID

    def setUp(self):
        super().setup()

    @mock.patch('vk.helpers.make_request_vk')
    def test(self, mock_make_request_vk, side_effect = side_effect_make_request):
        mock_make_request_vk.side_effect = side_effect

        expected_answer = f"Что-то пошло не так. Убедитесь, что группа {links.private_group1} не заблокирована и не является закрытой."
        self.pipeline_user(expected_answer)
        self.pipeline_chat(expected_answer)


class EveryoneIsMemberTest(TestCase, SharedRemove):
    kick_nonmembers_group_link = links.gk4z
    kick_nonmembers_group_id = links.gk4zID

    def setUp(self):
        super().setup()

    @mock.patch('vk.actions.RemoveAction.RemoveAction.remove_nonmembers')
    @mock.patch('vk.actions.RemoveAction.RemoveAction.simple_conversation_members')
    def test(self, mock_simple_conversation_members, mock_remove_nonmembers,
             side_effect=side_effect_remove_nonmembers):
        mock_simple_conversation_members.return_value = [4003081, 15300039, 87448687]
        mock_remove_nonmembers.side_effect = side_effect

        expected_answer = f"Все участники чата состоят в группе {links.gk4z}"
        self.pipeline_user(expected_answer)
        self.pipeline_chat(expected_answer)
