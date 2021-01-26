from django.test import TestCase, TransactionTestCase

from vk import models
from vk.tests.data_for_tests.big_texts_for_tests import phrase_3999
from vk.tests.shared.pipelines_and_setups import PipelinesAndSetUps
from vk.tests.shared.shared_tests.user_specific_commands_test import UserSpecificCommandsMixinTest

from vk.tests.data_for_tests.message_data import OwnerAndBotChatData


class UserSpecificPhraseTest(TestCase, UserSpecificCommandsMixinTest):
    command = "/phrase"


class SharedMethods(PipelinesAndSetUps):
    command = "/phrase"

    def check_no_phrases_left(self):
        phrases_from_db = models.IntervalPhrase.objects.filter(chat_id=self.chat_db_object)
        self.assertEqual(len(phrases_from_db), 0)

    def check_phrases_id_left(self, ids_left: set):
        phrases_from_db = models.IntervalPhrase.objects.filter(chat_id=self.chat_db_object)
        ids_from_db = {phrase.id for phrase in phrases_from_db}
        self.assertEqual(ids_from_db, ids_left)


class PhraseTest(TransactionTestCase, SharedMethods):
    reset_sequences = True

    def setUp(self):
        self.chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True)

    def test_info_0_phrases(self):
        expected_answer = f"Сохраненных фраз для режима /interval: 0.\n"
        self.pipeline_chat_from_owner("info", expected_answer)
        self.pipeline_user("info", expected_answer)

    def test_info_2_phrases_and_1_big(self):
        models.IntervalPhrase.objects.create(chat_id=self.chat_db_object, phrase="phrase1" * 10)
        models.IntervalPhrase.objects.create(chat_id=self.chat_db_object, phrase=phrase_3999)
        models.IntervalPhrase.objects.create(chat_id=self.chat_db_object, phrase="phrase2")
        expected_answer = f"id: 2. Phrase: {phrase_3999}\nid: 3. Phrase: phrase2\n"
        self.pipeline_chat_from_owner("info", expected_answer)
        self.pipeline_user("info", expected_answer)

    def test_without_option(self):
        expected_answer = "Пожалуйста, уточните опцию."
        self.pipeline_chat_from_owner("", expected_answer)
        self.pipeline_user("", expected_answer)

    def test_nonexisting_option(self):
        expected_answer = "У команды /phrase нет опции 'asdf'"
        self.pipeline_chat_from_owner("asdf", expected_answer)
        self.pipeline_user("asdf", expected_answer)

    def test_not_owner(self):
        expected_answer = 'Только владелец беседы может использовать эту команду.'
        self.pipeline_chat_not_owner("info", expected_answer)

    def test_remove_nothing(self):
        expected_answer = "После команды /phrase remove нужно написать id фраз, которые вы хотите удалить, " \
                          "например '/phrase remove 35, 44, 28'. Узнать id фраз можно командой /phrase info."
        self.pipeline_chat_from_owner("remove", expected_answer)
        self.pipeline_user("remove", expected_answer)

    def test_remove_all_empty_bd(self):
        expected_answer = "Невозможно выполнить удаление: у вас не сохранено ни одной фразы."
        self.pipeline_chat_from_owner("remove all", expected_answer)
        self.pipeline_user("remove all", expected_answer)


class PhraseThreePhrasesInDBNoInterval(TransactionTestCase, SharedMethods):
    reset_sequences = True

    def setUp(self):
        self.chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True)
        models.IntervalPhrase.objects.create(chat_id=self.chat_db_object, phrase="phrase1")
        models.IntervalPhrase.objects.create(chat_id=self.chat_db_object, phrase="phrase2")
        models.IntervalPhrase.objects.create(chat_id=self.chat_db_object, phrase="phrase3")

    def test_info_2_phrases(self):
        expected_answer = f"Сохраненных фраз для режима /interval: 3.\nid: 1. Phrase: phrase1\nid: 2. Phrase: phrase2\nid: 3. Phrase: phrase3\n"
        self.pipeline_chat_from_owner("info", expected_answer)
        self.pipeline_user("info", expected_answer)

    def test_remove_all_chat(self):
        expected_answer = "Удалены все сохраненные фразы."
        self.pipeline_chat_from_owner("remove all", expected_answer)
        self.check_no_phrases_left()

    def test_remove_all_user(self):
        expected_answer = "Удалены все сохраненные фразы."
        self.pipeline_user("remove all", expected_answer)
        self.check_no_phrases_left()

    def test_remove_some_chat(self):
        expected_answer = "Фразы с ID 1, 2 удалены."
        self.pipeline_chat_from_owner("remove 1, 2", expected_answer)
        self.check_phrases_id_left({3})

    def test_remove_some_user(self):
        expected_answer = "Фразы с ID 1, 2 удалены."
        self.pipeline_user("remove 1, 2", expected_answer)
        self.check_phrases_id_left({3})

    def test_remove_some_nonexistent_chat(self):
        expected_answer = f"Фраз с ID 4, 5 у вас нет. Фразы с ID 3 удалены."
        self.pipeline_chat_from_owner("remove 3, 4, 5", expected_answer)
        self.check_phrases_id_left({1, 2})

    def test_remove_some_nonexistent_user(self):
        expected_answer = f"Фраз с ID 4, 5 у вас нет. Фразы с ID 3 удалены."
        self.pipeline_user("remove 3, 4, 5", expected_answer)
        self.check_phrases_id_left({1, 2})

    def test_remove_all_nonexistent_chat(self):
        expected_answer = "Фраз с ID 4 у вас нет. Удалены все сохраненные фразы."
        self.pipeline_chat_from_owner("remove 1, 2, 3, 4", expected_answer)
        self.check_no_phrases_left()

    def test_remove_all_nonexistent_user(self):
        expected_answer = "Фраз с ID 4 у вас нет. Удалены все сохраненные фразы."
        self.pipeline_user("remove 1, 2, 3, 4", expected_answer)
        self.check_no_phrases_left()


class PhraseThreePhrasesInDBIntervalOn(TransactionTestCase, SharedMethods):
    reset_sequences = True

    def setUp(self):
        self.chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id,
            conversation_is_registered=True, interval=4, interval_mode=True, messages_till_endpoint=2)

        models.IntervalPhrase.objects.create(chat_id=self.chat_db_object, phrase="phrase1")
        models.IntervalPhrase.objects.create(chat_id=self.chat_db_object, phrase="phrase2")
        models.IntervalPhrase.objects.create(chat_id=self.chat_db_object, phrase="phrase3")

    def check_db_for_interval(self, mode: bool):
        self.chat_db_object.refresh_from_db()
        self.assertEqual(self.chat_db_object.interval_mode, mode)

    def test_remove_all_chat(self):
        expected_answer = "Удалены все сохраненные фразы. Режим /interval отключен."
        self.pipeline_chat_from_owner("remove all", expected_answer)
        self.check_no_phrases_left()
        self.check_db_for_interval(False)

    def test_remove_all_user(self):
        expected_answer = "Удалены все сохраненные фразы. Режим /interval отключен."
        self.pipeline_user("remove all", expected_answer)
        self.check_no_phrases_left()
        self.check_db_for_interval(False)

    def test_remove_all_nonexistent_chat(self):
        expected_answer = "Фраз с ID 4 у вас нет. Удалены все сохраненные фразы. Режим /interval отключен."
        self.pipeline_chat_from_owner("remove 1, 2, 3, 4", expected_answer)
        self.check_no_phrases_left()
        self.check_db_for_interval(False)

    def test_remove_all_nonexistent_user(self):
        expected_answer = "Фраз с ID 4 у вас нет. Удалены все сохраненные фразы. Режим /interval отключен."
        self.pipeline_user("remove 1, 2, 3, 4", expected_answer)
        self.check_no_phrases_left()
        self.check_db_for_interval(False)

    def test_remove_some_nonexistent_user(self):
        expected_answer = f"Фраз с ID 4, 5 у вас нет. Фразы с ID 3 удалены."
        self.pipeline_user("remove 3, 4, 5", expected_answer)
        self.check_phrases_id_left({1, 2})
        self.check_db_for_interval(True)


class PhraseAddTest(TransactionTestCase, SharedMethods):
    reset_sequences = True

    def setUp(self):
        self.chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id,
            conversation_is_registered=True)

    def test_add_nothing(self):
        expected_answer = "Напишите фразы для бота после команды /phrase add. Используйте разделитель '|'," \
                          " если хотите добавить сразу несколько фраз."
        self.pipeline_chat_from_owner("add", expected_answer)
        self.pipeline_user("add", expected_answer)

    def test_add_too_big_phrase_chat(self):
        text = "add " + phrase_3999 + "hop"
        expected_answer = "Сохраненных фраз для режима /interval: 0.\n"
        self.pipeline_chat_from_owner(text, expected_answer)
        self.pipeline_user(text, expected_answer)
        self.check_no_phrases_left()

    def test_add_one_too_big_and_two_normal_phrases_chat(self):
        text = "add " + phrase_3999 + "hop" + "|phrase1 | second phrase|"
        expected_answer = f"Сохраненных фраз для режима /interval: 2.\nid: 1. Phrase: phrase1\nid: 2. Phrase: second phrase\n"
        self.pipeline_chat_from_owner(text, expected_answer)
        phrases_from_db = models.IntervalPhrase.objects.filter(chat_id=self.chat_db_object).order_by('id')
        self.assertEqual(phrases_from_db[0].id, 1)
        self.assertEqual(phrases_from_db[0].phrase, "phrase1")
        self.assertEqual(phrases_from_db[1].id, 2)
        self.assertEqual(phrases_from_db[1].phrase, "second phrase")

    def test_add_one_too_big_and_two_normal_phrases_user(self):
        text = "add " + phrase_3999 + "hop" + "|phrase1 | second phrase|"
        expected_answer = f"Сохраненных фраз для режима /interval: 2.\nid: 1. Phrase: phrase1\nid: 2. Phrase: second phrase\n"
        self.pipeline_user(text, expected_answer)
        phrases_from_db = models.IntervalPhrase.objects.filter(chat_id=self.chat_db_object).order_by('id')
        self.assertEqual(phrases_from_db[0].id, 1)
        self.assertEqual(phrases_from_db[0].phrase, "phrase1")
        self.assertEqual(phrases_from_db[1].id, 2)
        self.assertEqual(phrases_from_db[1].phrase, "second phrase")

    def test_one_exists_add_too_big_user(self):
        models.IntervalPhrase.objects.create(chat_id=self.chat_db_object, phrase="phrase1")
        text = "add " + phrase_3999 + "hop"
        expected_answer = "Сохраненных фраз для режима /interval: 1.\nid: 1. Phrase: phrase1\n"
        self.pipeline_user(text, expected_answer)
        phrases_from_db = models.IntervalPhrase.objects.filter(chat_id=self.chat_db_object).order_by('id')
        self.assertEqual(len(phrases_from_db), 1)
        self.assertEqual(phrases_from_db[0].id, 1)
        self.assertEqual(phrases_from_db[0].phrase, "phrase1")
