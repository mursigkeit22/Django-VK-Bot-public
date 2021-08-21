from django.test import TestCase
import vk.tests.data_for_tests.group_links as links

from vk import models, helpers
from vk.helpers import PersonalTokenException
from vk.tests.data_for_tests.message_data import OwnerAndBotChatData

from vk.tests.shared.pipelines_and_setups import PipelinesAndSetUps
from web_vk.constants import test_personal_token, test_personal_expired_token


class MakeRequestPersonalTest(TestCase, PipelinesAndSetUps):

    def setUp(self):
        self.chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True)

    def test_chat_owner_not_provided(self):
        workgroup = "-" + str(links.normal_group1ID)
        with self.assertRaises(PersonalTokenException) as context:
            two_upper_posts = helpers.make_request_vk('wall.get', personal=True, count=2,
                                                      owner_id=workgroup)['response']['items']
        self.assertEqual(str(context.exception), "Chat owner was not provided when 'personal' argument was True.")

    def test_chat_owner_doesnt_have_profile(self):
        workgroup = "-" + str(links.normal_group1ID)
        with self.assertRaises(PersonalTokenException) as context:
            two_upper_posts = \
            helpers.make_request_vk('wall.get', personal=True, count=2, chat_owner=OwnerAndBotChatData.owner_id,
                                    owner_id=workgroup)['response']['items']
        self.assertEqual(str(context.exception),
                         f"UserProfile matching query does not exist. Chat owner: {OwnerAndBotChatData.owner_id}.")

    def test_profile_exists_valid_token(self):
        self.set_user_profile(test_personal_token)
        workgroup = "-" + str(links.group_with_three_postsID)
        two_upper_posts = \
            helpers.make_request_vk('wall.get', personal=True, count=2, chat_owner=OwnerAndBotChatData.owner_id,
                                    owner_id=workgroup)['response']['items']
        self.assertEqual(len(two_upper_posts), 2)

    def test_profile_exists_expired_token(self):
        self.set_user_profile(test_personal_expired_token)
        workgroup = "-" + str(links.group_with_three_postsID)
        with self.assertRaises(KeyError):
            two_upper_posts = \
            helpers.make_request_vk('wall.get', personal=True, count=2, chat_owner=OwnerAndBotChatData.owner_id,
                                    owner_id=workgroup)['response']['items']

