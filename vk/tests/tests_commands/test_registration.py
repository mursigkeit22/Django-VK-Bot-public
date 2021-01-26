from django.test import TestCase
from vk.vkreceiver_event_handler import EventHandler
import vk.models as models
from vk.tests.data_for_tests.message_data import input_data, OwnerAndBotChatData


class RegistrationTests(TestCase):
    """
        Bot must have admin rights in chats for tests to work.

        """

    def registration_on_chat_owner(self):
        data = input_data(OwnerAndBotChatData.peer_id, '/reg on', OwnerAndBotChatData.owner_id)
        answer = EventHandler(data).process()
        expected_answer = f'Беседа успешно зарегистрирована, ID вашей беседы: {OwnerAndBotChatData.peer_id}'
        self.assertEqual(answer, expected_answer)
        chat_object = models.Chat.objects.filter(chat_id=OwnerAndBotChatData.peer_id)
        new_post_setting_object_exists = models.NewPostSetting.objects.filter(chat_id=chat_object[0]).exists()
        random_post_setting_object_exists = models.RandomPostSetting.objects.filter(chat_id=chat_object[0]).exists()
        kick_non_members_setting_object_exists = models.KickNonMembersSetting.objects.filter(
            chat_id=chat_object[0]).exists()
        chat_is_registered = chat_object[0].conversation_is_registered
        self.assertTrue(chat_is_registered)
        self.assertTrue(new_post_setting_object_exists)
        self.assertTrue(random_post_setting_object_exists)
        self.assertTrue(kick_non_members_setting_object_exists)

    def registration_on_chat_not_owner(self):
        data = input_data(OwnerAndBotChatData.peer_id, '/reg on', OwnerAndBotChatData.not_owner_id)
        answer = EventHandler(data).process()
        expected_answer = "Conversation isn't registered. Nothing will be sent."
        self.assertEqual(answer, expected_answer)
        chat_object = models.Chat.objects.filter(chat_id=OwnerAndBotChatData.peer_id)
        chat_is_registered = chat_object[0].conversation_is_registered
        self.assertFalse(chat_is_registered)

    def registration_info_chat_owner(self):
        data = input_data(OwnerAndBotChatData.peer_id, '/reg info', OwnerAndBotChatData.owner_id)
        answer = EventHandler(data).process()
        expected_answer = "Conversation isn't registered. Nothing will be sent."
        self.assertEqual(answer, expected_answer)


class RegistrationFirstTimeTests(RegistrationTests):

    def test_registration_on_chat_owner(self):
        self.registration_on_chat_owner()

    def test_registration_on_chat_not_owner(self):
        self.registration_on_chat_not_owner()

    def test_registration_info_chat_owner(self):
        self.registration_info_chat_owner()


class RegistrationWithExistingDBEntryTests(RegistrationTests):
    def setUp(self):
        models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id,
            conversation_is_registered=False)

    def test_registration_on_chat_owner(self):
        self.registration_on_chat_owner()

    def test_registration_on_chat_not_owner(self):
        self.registration_on_chat_not_owner()

    def test_registration_info_chat_owner(self):
        self.registration_info_chat_owner()

    def test_registration_on_user_owner(self):
        data = input_data(peer_id=OwnerAndBotChatData.owner_id, text=f'/reg {OwnerAndBotChatData.peer_id} on',
                          from_id=OwnerAndBotChatData.owner_id)
        answer = EventHandler(data).process()
        expected_answer = "Команду /reg нельзя использовать в личной беседе с ботом."
        self.assertEqual(answer, expected_answer)


class RegistrationInfoRegisteredTrueTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True)

    def test_info(self):
        data = input_data(OwnerAndBotChatData.peer_id, '/reg info', OwnerAndBotChatData.owner_id)
        answer = EventHandler(data).process()
        expected_answer = f'ID вашей беседы {OwnerAndBotChatData.peer_id}'
        self.assertEqual(answer, expected_answer)

    def test_info_not_owner(self):
        data = input_data(OwnerAndBotChatData.peer_id, '/reg info', OwnerAndBotChatData.not_owner_id)
        answer = EventHandler(data).process()
        expected_answer = 'Только владелец беседы может использовать эту команду.'
        self.assertEqual(answer, expected_answer)

    def test_info_wrong_command(self):
        data = input_data(OwnerAndBotChatData.peer_id, '/reg inf', OwnerAndBotChatData.owner_id)
        answer = EventHandler(data).process()
        expected_answer = f'У команды /reg нет опции inf'
        self.assertEqual(answer, expected_answer)

    def test_info_extra_word(self):
        data = input_data(OwnerAndBotChatData.peer_id, '/reg info extra', OwnerAndBotChatData.owner_id)
        answer = EventHandler(data).process()
        expected_answer = f'ID вашей беседы {OwnerAndBotChatData.peer_id}'
        self.assertEqual(answer, expected_answer)

    def test_registration_info_user_owner(self):
        data = input_data(peer_id=OwnerAndBotChatData.owner_id, text=f'/reg {OwnerAndBotChatData.peer_id} info',
                          from_id=OwnerAndBotChatData.owner_id)
        answer = EventHandler(data).process()
        expected_answer = "Команду /reg нельзя использовать в личной беседе с ботом."
        self.assertEqual(answer, expected_answer)


class RegistrationOffRegisteredTrueTests(TestCase):

    def setUp(self):

        chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True)
        models.RandomPostSetting.objects.update_or_create(chat_id=chat_db_object)
        models.NewPostSetting.objects.update_or_create(chat_id=chat_db_object)
        models.KickNonMembersSetting.objects.update_or_create(chat_id=chat_db_object)

    def test_registration_off_chat_owner(self):
        data = input_data(peer_id=OwnerAndBotChatData.peer_id, text=f'/reg off',
                          from_id=OwnerAndBotChatData.owner_id)
        answer = EventHandler(data).process()
        expected_answer = "Регистрация отменена: бот будет игнорировать вас и ваши команды."
        self.assertEqual(answer, expected_answer)
        chat_object = models.Chat.objects.filter(chat_id=OwnerAndBotChatData.peer_id)
        new_post_setting_mode = models.NewPostSetting.objects.filter(chat_id=chat_object[0])[0].newpost_mode
        random_post_setting_mode = models.RandomPostSetting.objects.filter(chat_id=chat_object[0])[0].random_post_mode
        kick_non_members_setting_mode = models.KickNonMembersSetting.objects.filter(
            chat_id=chat_object[0])[0].kick_nonmembers_mode
        chat_is_registered = chat_object[0].conversation_is_registered
        self.assertFalse(chat_is_registered)
        self.assertFalse(new_post_setting_mode)
        self.assertFalse(random_post_setting_mode)
        self.assertFalse(kick_non_members_setting_mode)

    def test_registration_off_user_owner(self):
        data = input_data(peer_id=OwnerAndBotChatData.owner_id, text=f'/reg {OwnerAndBotChatData.peer_id} off',
                          from_id=OwnerAndBotChatData.owner_id)
        answer = EventHandler(data).process()
        expected_answer = "Команду /reg нельзя использовать в личной беседе с ботом."
        self.assertEqual(answer, expected_answer)
