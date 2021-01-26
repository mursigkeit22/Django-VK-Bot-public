from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from vk import models
from vk.tests.data_for_tests.message_data import OwnerAndBotChatData
import vk.tests.data_for_tests.group_links as links
from vk.tests.shared.pipelines_and_setups import PipelinesAndSetUps
from web_vk.constants import test_personal_token, test_personal_expired_token


class SharedMethods(TestCase, PipelinesAndSetUps):

    def call_command(self, *args, **kwargs):
        out = StringIO()
        call_command(
            "newpost",
            *args,
            stdout=out,
            stderr=StringIO(),
            **kwargs,
        )
        return out.getvalue()

    def clean_string(self, string: str):
        index = string.rfind("]")
        return string[index + 1:]

    def save_settings(self, link: str, id: int, timestamp: int = 0):
        self.settings_object.newpost_group_link = link
        self.settings_object.newpost_group_id = id
        self.settings_object.newpost_mode = True
        self.settings_object.latest_newpost_timestamp = timestamp
        self.settings_object.save()


class NewPostTest(SharedMethods):

    def setUp(self):
        self.chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True)
        self.settings_object = models.NewPostSetting.objects.create(chat_id=self.chat_db_object)
        self.set_user_profile(test_personal_token)

    def test_off(self):
        out = self.call_command(f"{OwnerAndBotChatData.peer_id}")
        self.assertEqual(self.clean_string(out), f" Newpost_mode is off for chat {OwnerAndBotChatData.peer_id}.\n")

    def test_empty_wall(self):
        self.save_settings(links.public_name_with_empty_wall, links.public_name_with_empty_wallID)

        out = self.call_command(f"{OwnerAndBotChatData.peer_id}")
        self.assertEqual(self.clean_string(out),
                         f' Newpost script. Group {links.public_name_with_empty_wall}. Wall is empty.\n')

    def test_turned_out_closed_for_bot(self):
        """  Так как для бота группа всё равно закрыта, бот отправит пустое сообщение."""
        self.save_settings(links.closed_event_name, links.closed_event_nameID)

        out = self.call_command(f"{OwnerAndBotChatData.peer_id}")
        self.assertEqual(self.clean_string(out),
                         f' Message with new post (ID 1) is sent.\n')

    def test_turned_out_closed_for_user(self):
        self.save_settings(links.closed_group_for_me, links.closed_group_for_meID)

        out = self.call_command(f"{OwnerAndBotChatData.peer_id}")
        self.assertEqual(self.clean_string(out),
                         f' KeyError while getting two upper posts: Access denied: this wall available only for community members Workgroup -{links.closed_group_for_meID}\n')

    def test_only_one_post_on_wall(self):
        self.save_settings(links.group_with_one_post, links.group_with_one_postID)
        out = self.call_command(f"{OwnerAndBotChatData.peer_id}")
        self.assertEqual(self.clean_string(out), ' Message with new post (ID 1) is sent.\n')
        out = self.call_command(f"{OwnerAndBotChatData.peer_id}")
        self.assertEqual(self.clean_string(out), " No new posts to send.\n")

    def test_there_is_new_post(self):
        self.save_settings(links.group_with_three_posts, links.group_with_three_postsID,
                           timestamp=links.group_with_three_posts_timestamp2)
        out = self.call_command(f"{OwnerAndBotChatData.peer_id}")
        self.assertEqual(self.clean_string(out), ' Message with new post (ID 3) is sent.\n')
        self.settings_object.refresh_from_db()
        self.assertEqual(self.settings_object.latest_newpost_timestamp, links.group_with_three_posts_timestamp3)

    def test_pinned_post_old(self):
        self.save_settings(links.public_name_pinned, links.public_name_pinnedID,
                           timestamp=links.public_name_pinned_timestamp2)
        out = self.call_command(f"{OwnerAndBotChatData.peer_id}")
        self.assertEqual(self.clean_string(out), ' Message with new post (ID 3) is sent.\n')
        out = self.call_command(f"{OwnerAndBotChatData.peer_id}")
        self.assertEqual(self.clean_string(out), " No new posts to send.\n")
        self.settings_object.refresh_from_db()
        self.assertEqual(self.settings_object.latest_newpost_timestamp, links.public_name_pinned_timestamp3)

    def test_last_post_deleted(self):
        self.save_settings(links.group_with_three_posts, links.group_with_three_postsID,
                           timestamp=links.group_with_three_posts_timestamp3 + 1)
        out = self.call_command(f"{OwnerAndBotChatData.peer_id}")
        self.assertEqual(self.clean_string(out), " No new posts to send.\n")
        self.assertEqual(self.settings_object.latest_newpost_timestamp, links.group_with_three_posts_timestamp3 + 1)

    def test_edited(self):
        # vkontakte doesn't change timestamp (date) when post is edited.
        pass


class NewPostBadTokenTest(SharedMethods):

    def setUp(self):
        self.chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id,
            conversation_is_registered=True)
        self.settings_object = models.NewPostSetting.objects.create(chat_id=self.chat_db_object)

    def test_no_user_profile(self):
        self.save_settings(links.group_with_three_posts, links.group_with_three_postsID,
                           timestamp=links.group_with_three_posts_timestamp2)
        out = self.call_command(f"{OwnerAndBotChatData.peer_id}")
        self.assertEqual(self.clean_string(out),
                         f' UserProfile matching query does not exist. Chat owner: {OwnerAndBotChatData.owner_id}.\n')

    def test_expired_token(self):
        self.set_user_profile(test_personal_expired_token)
        self.save_settings(links.group_with_three_posts, links.group_with_three_postsID,
                           timestamp=links.group_with_three_posts_timestamp2)
        out = self.call_command(f"{OwnerAndBotChatData.peer_id}")
        expected_answer = f' KeyError while getting two upper posts: User authorization failed: invalid access_token (4). Workgroup -{links.group_with_three_postsID}\n'

        self.assertEqual(self.clean_string(out),
                         expected_answer)


