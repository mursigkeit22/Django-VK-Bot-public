import time
from typing import Optional

from django.test import TestCase

from vk import models
from vk.actions.RandomPostAction import RandomPostAction
from vk.helpers import PersonalTokenException
from vk.tests.data_for_tests.message_data import OwnerAndBotChatData
from vk.tests.shared.pipelines_and_setups import PipelinesAndSetUps
from web_vk.constants import test_personal_token, test_personal_expired_token, LOGIN_LINK
import vk.tests.data_for_tests.group_links as links


class ActionPostTest(TestCase, PipelinesAndSetUps):

    @classmethod
    def setUpTestData(cls):
        cls.chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True)
        super().set_user_profile(test_personal_token)

    def pipeline(self, expected_answer: str, groupID: Optional[int] = None,
                 grouplink: str = "", ):
        setting_object = models.RandomPostSetting.objects.create(chat_id=self.chat_db_object, random_post_group_id=groupID,
                                                random_post_group_link=grouplink, random_post_mode=True)
        action_object = RandomPostAction(OwnerAndBotChatData.peer_id, setting_object, self.chat_db_object)
        returned_answer = action_object.process()
        self.assertEqual(returned_answer, expected_answer)

    def test_wall_is_empty(self):
        time.sleep(1)
        expected_answer = "Стена пуста."
        self.pipeline(expected_answer=expected_answer, groupID=links.public_name_with_empty_wallID, grouplink=links.public_name_with_empty_wall)

    def test_group_turned_out_closed_for_user(self):
        expected_answer = f"Что-то пошло не так. Убедитесь, что группа {links.closed_group_for_me} не заблокирована и не является закрытой."
        self.pipeline(expected_answer=expected_answer, groupID=links.closed_group_for_meID,
                      grouplink=links.closed_group_for_me)

    def test_group_turned_out_closed_for_bot(self):
        expected_answer = f"random post is sent."
        self.pipeline(expected_answer=expected_answer, groupID=links.closed_groupID,
                      grouplink=links.closed_group)

    def test_group_turned_out_deactivated(self):
        expected_answer = f"Что-то пошло не так. Убедитесь, что группа {links.deactivated_group} не заблокирована и не является закрытой."
        self.pipeline(expected_answer=expected_answer, groupID=links.deactivated_groupID,
                      grouplink=links.deactivated_group)

    def test_group_turned_out_private(self):
        expected_answer = f"Что-то пошло не так. Убедитесь, что группа {links.private_group1} не заблокирована и не является закрытой."
        self.pipeline( expected_answer=expected_answer, groupID=links.private_group1ID,
                      grouplink=links.private_group1)

    def test_normal_post(self):
        expected_answer = "random post is sent."
        self.pipeline(expected_answer=expected_answer, groupID=links.normal_group1ID,
                      grouplink=links.normal_group1)

    def test_only_one_post_on_the_wall(self):
        expected_answer = "random post is sent."
        self.pipeline(expected_answer=expected_answer, groupID=links.group_with_one_postID,
                      grouplink=links.group_with_one_post)


class ActionPostBadTokenTest(TestCase, PipelinesAndSetUps):

    def setUp(self):
        self.chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id,
            conversation_is_registered=True)
        self.setting_object = models.RandomPostSetting.objects.create(chat_id=self.chat_db_object,
                                                                 random_post_group_id=links.normal_group1ID,
                                                                 random_post_group_link=links.normal_group1,
                                                                 random_post_mode=True)
        self.action_object = RandomPostAction(OwnerAndBotChatData.peer_id, self.setting_object, self.chat_db_object)

    def test_no_user_profile(self):  # shouldn't happen
        returned_answer = self.action_object.process()
        self.assertIsInstance(returned_answer, PersonalTokenException)
        self.assertEqual(returned_answer.args[0],
                         f"UserProfile matching query does not exist. Chat owner: {OwnerAndBotChatData.owner_id}.")

    def test_expired_token(self):
        self.set_user_profile(test_personal_expired_token)
        returned_answer = self.action_object.process()
        self.assertEqual(returned_answer, f"Для корректной работы бота пройдите по ссылке {LOGIN_LINK}.")
