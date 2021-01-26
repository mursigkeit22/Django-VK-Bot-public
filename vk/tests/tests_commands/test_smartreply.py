from django.test import TestCase, TransactionTestCase

from vk import models, helpers
from vk.helpers import smart_reply
from vk.tests.data_for_tests.big_texts_for_tests import smart_reply_two_sends, text_122_letters
from vk.tests.shared.pipelines_and_setups import PipelinesAndSetUps
from vk.tests.shared.shared_tests.user_specific_commands_test import UserSpecificCommandsMixinTest

from vk.tests.data_for_tests.message_data import OwnerAndBotChatData


class UserSpecificSmartReplyTest(TestCase, UserSpecificCommandsMixinTest):
    command = "/smartreply"


class SharedMethods(PipelinesAndSetUps):
    command = "/smartreply"

    def check_no_entries_left(self):
        entries_from_db = models.SmartReply.objects.filter(chat_id=self.chat_db_object)
        self.assertEqual(len(entries_from_db), 0)

    def check_replies_id_left(self, ids_left: set):
        entries_from_db = models.SmartReply.objects.filter(chat_id=self.chat_db_object)
        ids_from_db = {entry.id for entry in entries_from_db}
        self.assertEqual(ids_from_db, ids_left)

    def check_no_replies_left(self):
        entries_from_db = models.SmartReply.objects.filter(chat_id=self.chat_db_object)
        self.assertEqual(len(entries_from_db), 0)


class SmartReplyEmptyDBTest(TestCase, SharedMethods):

    def setUp(self):
        self.chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True)

    def test_without_option(self):
        expected_answer = "Пожалуйста, уточните опцию."
        self.pipeline_chat_from_owner("", expected_answer)
        self.pipeline_user("", expected_answer)

    def test_nonexisting_option(self):
        expected_answer = f"У команды {self.command} нет опции 'asdf'"
        self.pipeline_chat_from_owner("asdf", expected_answer)
        self.pipeline_user("asdf", expected_answer)

    def test_not_owner(self):
        expected_answer = 'Только владелец беседы может использовать эту команду.'
        self.pipeline_chat_not_owner("info", expected_answer)

    def test_remove_nothing(self):
        expected_answer = f"После команды {self.command} remove нужно написать ID smart-сообщений, которые вы хотите удалить, " \
                          f"например '{self.command} remove 35, 44, 28'. Узнать ID smart-сообщений можно командой {self.command} info."
        self.pipeline_chat_from_owner("remove", expected_answer)
        self.pipeline_user("remove", expected_answer)

    def test_remove_all_empty_bd(self):
        expected_answer = "Невозможно выполнить удаление: у вас не сохранено ни одного smart-сообщения."
        self.pipeline_chat_from_owner("remove all", expected_answer)
        self.pipeline_user("remove all", expected_answer)


class InfoSmartReplyTest(TransactionTestCase, SharedMethods):
    reset_sequences = True

    def setUp(self):
        self.chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True)

    def test_info_0_smart_messages(self):
        expected_answer = f"Сохраненных сообщений для режима /smart: 0.\n"
        self.pipeline_chat_from_owner("info", expected_answer)
        self.pipeline_user("info", expected_answer)

    def test_info_one_smart_message(self):
        models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger="hello", reply="hello")

        expected_answer = f'Сохраненных сообщений для режима /smart: 1.\nID: 1. Сообщение-триггер: hello . Smart-ответ: hello\n'
        self.pipeline_chat_from_owner("info", expected_answer)
        self.pipeline_user("info", expected_answer)

    def test_info_two_send(self):
        phrase_model_list = [models.SmartReply(chat_id=self.chat_db_object, trigger="hello", reply="hello")] * 80
        models.SmartReply.objects.bulk_create(phrase_model_list)
        expected_answer = smart_reply_two_sends
        self.pipeline_chat_from_owner("info", expected_answer)
        self.pipeline_user("info", expected_answer)


class RemoveSmartOnTest(TransactionTestCase, SharedMethods):
    reset_sequences = True
    all_removed_answer = "Удалены все сохраненные smart-сообщения. Режим /smart отключен."

    def setUp(self):
        self.chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True, smart_mode=True)
        models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger="hello", reply="hello1")
        models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger="hello", reply="hello2")
        models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger="hello", reply="hello3")

    def test_remove_all_chat(self):
        expected_answer = self.all_removed_answer
        self.pipeline_chat_from_owner("remove all", expected_answer)
        self.check_no_replies_left()

    def test_remove_all_user(self):
        expected_answer = self.all_removed_answer
        self.pipeline_user("remove all", expected_answer)
        self.check_no_replies_left()

    def test_remove_some_chat(self):
        expected_answer = "Smart-сообщения с ID 1, 2 удалены."
        self.pipeline_chat_from_owner("remove 1, 2", expected_answer)
        self.check_replies_id_left({3})

    def test_remove_some_user(self):
        expected_answer = "Smart-сообщения с ID 1, 2 удалены."
        self.pipeline_user("remove 1, 2", expected_answer)
        self.check_replies_id_left({3})

    def test_remove_some_nonexistent_chat(self):
        expected_answer = f"Smart-сообщений с ID 4, 5 у вас нет." \
                             f" Smart-сообщения с ID 3 удалены."

        self.pipeline_chat_from_owner("remove 3, 4, 5", expected_answer)
        self.check_replies_id_left({1, 2})

    def test_remove_some_nonexistent_user(self):
        expected_answer = f"Smart-сообщений с ID 4, 5 у вас нет." \
                             f" Smart-сообщения с ID 3 удалены."
        self.pipeline_user("remove 3, 4, 5", expected_answer)
        self.check_replies_id_left({1, 2})

    def test_remove_all_nonexistent_chat(self):
        expected_answer = f"Smart-сообщений с ID 4 у вас нет. {self.all_removed_answer}"
        self.pipeline_chat_from_owner("remove 1, 2, 3, 4", expected_answer)
        self.check_no_replies_left()

    def test_remove_all_nonexistent_user(self):
        expected_answer = f"Smart-сообщений с ID 4 у вас нет. {self.all_removed_answer}"
        self.pipeline_user("remove 1, 2, 3, 4", expected_answer)
        self.check_no_replies_left()


class RemoveSmartOffTest(TransactionTestCase, SharedMethods):
    reset_sequences = True
    all_removed_answer = "Удалены все сохраненные smart-сообщения."

    def setUp(self):
        self.chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True)
        models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger="hello", reply="hello1")
        models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger="hello", reply="hello2")
        models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger="hello", reply="hello3")

    def test_remove_all_chat(self):
        expected_answer = self.all_removed_answer
        self.pipeline_chat_from_owner("remove all", expected_answer)
        self.check_no_replies_left()

    def test_remove_all_user(self):
        expected_answer = self.all_removed_answer
        self.pipeline_user("remove all", expected_answer)
        self.check_no_replies_left()

    def test_remove_some_chat(self):
        expected_answer = "Smart-сообщения с ID 1, 2 удалены."
        self.pipeline_chat_from_owner("remove 1, 2", expected_answer)
        self.check_replies_id_left({3})

    def test_remove_some_user(self):
        expected_answer = "Smart-сообщения с ID 1, 2 удалены."
        self.pipeline_user("remove 1, 2", expected_answer)
        self.check_replies_id_left({3})

    def test_remove_some_nonexistent_chat(self):
        expected_answer = f"Smart-сообщений с ID 4, 5 у вас нет." \
                             f" Smart-сообщения с ID 3 удалены."

        self.pipeline_chat_from_owner("remove 3, 4, 5", expected_answer)
        self.check_replies_id_left({1, 2})

    def test_remove_some_nonexistent_user(self):
        expected_answer = f"Smart-сообщений с ID 4, 5 у вас нет." \
                             f" Smart-сообщения с ID 3 удалены."
        self.pipeline_user("remove 3, 4, 5", expected_answer)
        self.check_replies_id_left({1, 2})

    def test_remove_all_nonexistent_chat(self):
        expected_answer = f"Smart-сообщений с ID 4 у вас нет. {self.all_removed_answer}"
        self.pipeline_chat_from_owner("remove 1, 2, 3, 4", expected_answer)
        self.check_no_replies_left()

    def test_remove_all_nonexistent_user(self):
        expected_answer = f"Smart-сообщений с ID 4 у вас нет. {self.all_removed_answer}"
        self.pipeline_user("remove 1, 2, 3, 4", expected_answer)
        self.check_no_replies_left()


class AddGoodSmartReply(TransactionTestCase, SharedMethods):
    reset_sequences = True

    def setUp(self):
        self.chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True)

    def test_add_normal_first_chat(self):
        expected_answer = f'Сохраненных сообщений для режима /smart: 1.\nID: 1. Сообщение-триггер: hello . Smart-ответ: hello\n'
        text = "add hello || hello"
        self.pipeline_chat_from_owner(text, expected_answer)

    def test_add_normal_first_user(self):
        expected_answer = f'Сохраненных сообщений для режима /smart: 1.\nID: 1. Сообщение-триггер: hello . Smart-ответ: hello\n'
        text = "add hello || hello"
        self.pipeline_user(text, expected_answer)

    def test_add_normal_second_chat(self):
        models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger="hello",
                                         reply="hello")
        expected_answer = f'Сохраненных сообщений для режима /smart: 2.\nID: 1. Сообщение-триггер: hello . Smart-ответ: hello\n' \
                          f'ID: 2. Сообщение-триггер: second message . Smart-ответ: second hello\n'
        text = "add second message || second hello"
        self.pipeline_chat_from_owner(text, expected_answer)

    def test_add_normal_second_user(self):
        models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger="hello",
                                         reply="hello")
        expected_answer = f'Сохраненных сообщений для режима /smart: 2.\nID: 1. Сообщение-триггер: hello . Smart-ответ: hello\n' \
                          f'ID: 2. Сообщение-триггер: second message . Smart-ответ: second hello\n'
        text = "add second message || second hello"
        self.pipeline_user(text, expected_answer)

    def test_101_chat(self):
        phrase_model_list = [models.SmartReply(chat_id=self.chat_db_object, trigger="hello", reply="hello")] * 100
        models.SmartReply.objects.bulk_create(phrase_model_list)
        expected_answer = "У вас уже сохранено 100 smart-сообщений. Это максимально возможное количество."
        text = "add 101 message || 101 hello"
        self.pipeline_chat_from_owner(text, expected_answer)


class AddWrongSmartReplyText(TestCase, SharedMethods):
    answer_wrong_delimetor = f"После команды {smart_reply} add нужно написать сообщение, на которое будет реагировать бот, " \
                             f"затем, через разделитель ||, ответ бота. " \
                             f"Например: '{smart_reply} add Привет || Сам привет'"

    @classmethod
    def setUpTestData(cls):
        cls.chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True)

    def test_add_extra_delimetor1(self):
        expected_answer = self.answer_wrong_delimetor
        text = "add ||hello || hello"
        self.pipeline_chat_from_owner(text, expected_answer)
        self.pipeline_user(text, expected_answer)

    def test_add_extra_delimetor2(self):
        expected_answer = self.answer_wrong_delimetor
        text = "add hello || hello ||"
        self.pipeline_chat_from_owner(text, expected_answer)
        self.pipeline_user(text, expected_answer)

    def test_add_extra_delimetor3(self):
        expected_answer = self.answer_wrong_delimetor
        text = "add || hello || hello ||"
        self.pipeline_chat_from_owner(text, expected_answer)
        self.pipeline_user(text, expected_answer)

    def test_add_lack_delimetor(self):
        expected_answer = self.answer_wrong_delimetor
        text = "add hello"
        self.pipeline_chat_from_owner(text, expected_answer)
        self.pipeline_user(text, expected_answer)

    def test_add_empty_trigger(self):
        expected_answer = "Нельзя сохранить пустое сообщение."
        text = "add ||hello"
        self.pipeline_chat_from_owner(text, expected_answer)
        self.pipeline_user(text, expected_answer)

    def test_add_empty_reply(self):
        expected_answer = "Нельзя сохранить пустое сообщение."
        text = "add incoming||"
        self.pipeline_chat_from_owner(text, expected_answer)
        self.pipeline_user(text, expected_answer)

    def test_separated_delimeter(self):
        expected_answer = self.answer_wrong_delimetor
        text = "add incoming | | reply reply reply"
        self.pipeline_chat_from_owner(text, expected_answer)
        self.pipeline_user(text, expected_answer)

    def test_too_long_reply(self):
        expected_answer = f"Сообщения не могут быть длинее {helpers.SMART_MAX_LEN} знаков."
        text = f"add hello || {text_122_letters}"
        self.pipeline_chat_from_owner(text, expected_answer)
        self.pipeline_user(text, expected_answer)

    def test_too_long_trigger(self):
        expected_answer = f"Сообщения не могут быть длинее {helpers.SMART_MAX_LEN} знаков."
        text = f"add {text_122_letters} || hello"
        self.pipeline_chat_from_owner(text, expected_answer)
        self.pipeline_user(text, expected_answer)

    #TODO: test change
