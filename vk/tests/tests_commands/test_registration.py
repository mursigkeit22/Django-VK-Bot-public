from django.test import TestCase

import vk.models as models
import vk.tests.data_for_tests.group_links as links
from vk.helpers import registration, option_on, option_off, option_info
from vk.tests.data_for_tests.message_data import OwnerAndBotChatData
from vk.tests.shared.pipelines_and_setups import PipelinesAndSetUps


class SharedMethods(TestCase, PipelinesAndSetUps):
    command = registration

    def check_db(self, expected):
        chat_db_object = models.Chat.objects.get(chat_id=OwnerAndBotChatData.peer_id)
        new_post_setting_object_exists = models.NewPostSetting.objects.filter(chat_id=chat_db_object).exists()
        random_post_setting_object_exists = models.RandomPostSetting.objects.filter(chat_id=chat_db_object).exists()
        kick_non_members_setting_object_exists = models.KickNonMembersSetting.objects.filter(
            chat_id=chat_db_object).exists()
        self.assertEqual(expected, chat_db_object.conversation_is_registered)
        self.assertEqual(expected, new_post_setting_object_exists)
        self.assertEqual(expected, random_post_setting_object_exists)
        self.assertEqual(expected, kick_non_members_setting_object_exists)

    def check_db_registration_off(self):
        self.chat_db_object.refresh_from_db()
        self.newpost_setting_object.refresh_from_db()
        self.kick_setting_object.refresh_from_db()
        self.randompost_setting_object.refresh_from_db()

        self.assertFalse(self.chat_db_object.conversation_is_registered)
        self.assertFalse(self.chat_db_object.interval_mode)
        self.assertFalse(self.chat_db_object.smart_mode)
        self.assertIsNone(self.chat_db_object.interval)
        self.assertIsNone(self.chat_db_object.messages_till_endpoint)

        self.assertFalse(self.newpost_setting_object.newpost_mode)
        self.assertEqual(self.newpost_setting_object.newpost_group_link, "")
        self.assertIsNone(self.newpost_setting_object.newpost_group_id)

        self.assertFalse(self.kick_setting_object.kick_nonmembers_mode)
        self.assertEqual(self.kick_setting_object.kick_nonmembers_group_link, "")
        self.assertIsNone(self.kick_setting_object.kick_nonmembers_group_id)

        self.assertFalse(self.randompost_setting_object.random_post_mode)
        self.assertEqual(self.randompost_setting_object.random_post_group_link, "")
        self.assertIsNone(self.randompost_setting_object.random_post_group_id)

        interval_phrase_exists = models.IntervalPhrase.objects.filter(chat_id=self.chat_db_object).exists()
        self.assertTrue(interval_phrase_exists)

        smart_phrase_exists = models.SmartReply.objects.filter(chat_id=self.chat_db_object).exists()
        self.assertTrue(smart_phrase_exists)


class RegistrationFirstTimeTests(SharedMethods):

    def test_chat_owner_register(self):
        self.pipeline_chat_from_owner(option_on, 'REGISTRATION_SUCCESSFUL',
                                      bot_response=f'Беседа успешно зарегистрирована, '
                                                   f'ID вашей беседы: {OwnerAndBotChatData.peer_id}')

        self.check_db(True)

    def test_chat_not_owner_tries_register(self):
        self.pipeline_chat_not_owner(option_on, 'NOT_OWNER', )
        self.check_db(False)

    def test_ask_reg_info_before_registration(self):
        self.pipeline_chat_from_owner(option_info, "NOT_REGISTERED",
                                      event_description="Conversation isn't registered. Nothing will be sent.")

    def test_ask_reg_off_before_registration(self):
        self.pipeline_chat_from_owner(option_off, "NOT_REGISTERED",
                                      event_description="Conversation isn't registered. Nothing will be sent.")


class RegistrationWithExistingDBEntryTests(SharedMethods):
    def setUp(self):
        self.basic_setup(is_registered=False)

    def test_chat_owner_register(self):
        self.pipeline_chat_from_owner(option_on, 'REGISTRATION_SUCCESSFUL', bot_response=f'Беседа успешно зарегистрирована, '
                                                                                    f'ID вашей беседы: {OwnerAndBotChatData.peer_id}')
        self.check_db(True)

    def test_chat_not_owner_tries_register(self):
        self.pipeline_chat_not_owner(option_on, 'NOT_OWNER', )
        self.chat_db_object.refresh_from_db()
        self.assertFalse(self.chat_db_object.conversation_is_registered)

    def test_ask_reg_info_before_registration(self):
        self.pipeline_chat_from_owner(option_info, "NOT_REGISTERED",
                                      event_description="Conversation isn't registered. Nothing will be sent.")
        self.chat_db_object.refresh_from_db()
        self.assertFalse(self.chat_db_object.conversation_is_registered)

    def test_ask_reg_off_before_registration(self):
        self.pipeline_chat_from_owner(option_off, "NOT_REGISTERED",
                                      event_description="Conversation isn't registered. Nothing will be sent.")
        self.chat_db_object.refresh_from_db()
        self.assertFalse(self.chat_db_object.conversation_is_registered)

    def test_user_owner_tries_register(self):
        self.pipeline_user(option_on, 'USER_REG_ERROR',
                           bot_response=f"Команду {self.command} нельзя использовать в личной беседе с ботом.", )


class RegistrationInfoRegisteredTrueTests(SharedMethods):

    @classmethod
    def setUpTestData(cls):
        cls().basic_setup()

    def test_info(self):
        self.pipeline_chat_from_owner(option_info, "REGISTRATION_INFO",
                                      bot_response=f'ID вашей беседы {OwnerAndBotChatData.peer_id}')

    def test_info_not_owner(self):
        self.pipeline_chat_not_owner(option_info, 'NOT_OWNER',
                                     bot_response=f'Только владелец беседы может использовать команду {self.command}.')

    def test_info_wrong_option(self):
        self.pipeline_chat_from_owner('inf', 'WRONG_OPTION',
                                      bot_response=f"У команды {self.command} нет опции 'inf'")

    def test_info_extra_word(self):
        self.pipeline_chat_from_owner(f'{option_info} extra word', "REGISTRATION_INFO",
                                      bot_response=f'ID вашей беседы {OwnerAndBotChatData.peer_id}')

    def test_registration_info_user_owner(self):
        self.pipeline_user(option_info, 'USER_REG_ERROR',

                           bot_response=f"Команду {self.command} нельзя использовать в личной беседе с ботом.", )


class RegistrationOffRegisteredTrueTests(SharedMethods):

    def setUp(self):
        self.setup_chat(is_registered=True, interval_mode=True, interval=4,
                        messages_till_endpoint=1)
        models.IntervalPhrase.objects.create(chat_id=self.chat_db_object, phrase="phrase1")
        models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger="trigger-message",
                                         reply="smart_reply")
        self.setup_newpost(group_link=links.normal_group1,
                           group_id=links.normal_group1ID,
                           mode=True)
        self.setup_kick(group_link=links.normal_group1,
                        group_id=links.normal_group1ID,
                        mode=True)
        self.setup_randompost(group_link=links.normal_group1,
                              group_id=links.normal_group1ID,
                              mode=True)

    def test_registration_off_chat_owner(self):
        self.pipeline_chat_from_owner(option_off, "REGISTRATION_OFF",
                                      bot_response="Регистрация отменена: бот будет игнорировать вас и ваши команды.")

        self.check_db_registration_off()

    def test_registration_off_user_owner(self):
        self.pipeline_user(option_off, 'USER_REG_ERROR',

                           bot_response=f"Команду {self.command} нельзя использовать в личной беседе с ботом.", )
        self.check_db(True)

    def test_registration_already_on(self):
        self.pipeline_chat_from_owner(option_on, "ALREADY_DONE",
                                      bot_response=f'Эта беседа уже зарегистрирована, ID вашей беседы {OwnerAndBotChatData.peer_id}')
