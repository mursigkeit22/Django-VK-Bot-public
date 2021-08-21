import time

from django.test import TestCase

import vk.tests.data_for_tests.group_links as links
from vk.helpers import random_post
from vk.tests.data_for_tests.message_data import OwnerAndBotChatData
from vk.tests.shared.pipelines_and_setups import PipelinesAndSetUps
from vk.usertext import common_dict
from web_vk.constants import test_personal_token, test_personal_expired_token


class Shared(PipelinesAndSetUps):
    command = random_post

    def pipeline(self, event_code, bot_response=None, event_description=None):
        with self.subTest(test_number="chat_owner"):
            self.pipeline_chat_from_owner("", event_code, bot_response=bot_response,
                                          event_description=event_description)
        with self.subTest(test_number="user"):
            self.pipeline_user("", event_code, bot_response=bot_response, event_description=event_description)
        with self.subTest(test_number="chat_not_owner"):
            self.pipeline_chat_not_owner("", event_code, bot_response=bot_response, event_description=event_description)

    def pipeline_post_sent(self, expected_bot_response_dict):
        with self.subTest(test_number="chat_owner"):
            self.pipeline_part_dict(OwnerAndBotChatData.peer_id, OwnerAndBotChatData.owner_id, self.command,
                                    "RANDOM_POST_SENT", expected_bot_response_dict,
                                    )
        with self.subTest(test_number="user"):
            self.pipeline_part_dict(OwnerAndBotChatData.owner_id, OwnerAndBotChatData.owner_id,
                                    f"{self.command} {OwnerAndBotChatData.peer_id}",
                                    "RANDOM_POST_SENT", expected_bot_response_dict)
        with self.subTest(test_number="chat_not_owner"):
            self.pipeline_part_dict(OwnerAndBotChatData.peer_id, OwnerAndBotChatData.not_owner_id, self.command,
                                    "RANDOM_POST_SENT", expected_bot_response_dict)


class ActionPostTest(TestCase, Shared):

    @classmethod
    def setUpTestData(cls):
        cls.setup_chat(True)
        cls.setup_newpost()
        cls.setup_kick()
        super().set_user_profile(test_personal_token)

    def test_wall_is_empty(self):
        time.sleep(1)
        self.setup_randompost(mode=True, group_link=links.public_name_with_empty_wall,
                              group_id=links.public_name_with_empty_wallID)
        self.pipeline("PREREQUISITES_ERROR", bot_response="Стена пуста.")

    def test_group_turned_out_closed_for_chat_owner(self):
        self.setup_randompost(mode=True, group_link=links.closed_group_for_me,
                              group_id=links.closed_group_for_meID)

        bot_response = common_dict["group_turned_bad"].substitute(group_link=links.closed_group_for_me)
        self.pipeline("WRONG_GROUP", bot_response=bot_response)

    def test_group_turned_out_closed_for_bot(self):
        """ bot will get the post from the wall, cause it will be using user token,
         but will send an empty message to chat"""
        self.setup_randompost(mode=True, group_link=links.closed_group,
                              group_id=links.closed_groupID)
        self.pipeline_post_sent({"peer_id": OwnerAndBotChatData.peer_id})

    def test_group_turned_out_deactivated(self):
        self.setup_randompost(mode=True, group_link=links.deactivated_group,
                              group_id=links.deactivated_groupID)

        bot_response = common_dict["group_turned_bad"].substitute(group_link=links.deactivated_group)
        self.pipeline("WRONG_GROUP", bot_response=bot_response)

    def test_group_turned_out_private(self):
        self.setup_randompost(mode=True, group_link=links.private_group1,
                              group_id=links.private_group1ID)

        bot_response = common_dict["group_turned_bad"].substitute(group_link=links.private_group1)
        self.pipeline("WRONG_GROUP", bot_response=bot_response)

    def test_normal_post(self):
        self.setup_randompost(mode=True, group_link=links.normal_group1,
                              group_id=links.normal_group1ID)
        self.pipeline_post_sent({"peer_id": OwnerAndBotChatData.peer_id})

    def test_only_one_post_on_the_wall(self):
        self.setup_randompost(mode=True, group_link=links.group_with_one_post,
                              group_id=links.group_with_one_postID)
        self.pipeline_post_sent({"peer_id": OwnerAndBotChatData.peer_id})


class ActionPostBadTokenTest(TestCase, Shared):
    event_description = "An error message is sent to chat owner."

    def setUp(self):
        self.setup_chat(True)
        self.setup_newpost()
        self.setup_kick()
        self.setup_randompost(mode=True, group_link=links.normal_group1,
                              group_id=links.normal_group1ID)

    def test_no_user_profile(self):  # shouldn't happen
        bot_response = {"message": common_dict["not_login"].substitute(command=random_post),
                        "peer_id": OwnerAndBotChatData.owner_id}
        self.pipeline("USER_PROFILE_ERROR", event_description=self.event_description,
                      bot_response=bot_response
                      )

    def test_expired_token(self):
        self.set_user_profile(test_personal_expired_token)
        bot_response = {"message": common_dict["refresh_token"].substitute(command=random_post),
                        "peer_id": OwnerAndBotChatData.owner_id}
        self.pipeline("USER_PROFILE_ERROR", event_description=self.event_description,
                      bot_response=bot_response)
