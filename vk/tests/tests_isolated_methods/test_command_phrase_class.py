from django.test import TestCase, TransactionTestCase

from vk import models
from vk.command_handlers.IntervalPhraseCommandHandler import IntervalPhraseCommandHandler
from vk.tests.data_for_tests.event_dicts import event_dict_simple_message
from vk.tests.data_for_tests.message_data import OwnerAndBotChatData
from vk.tests.data_for_tests.big_texts_for_tests import phrase_3999
from vk.text_parser import TextParser
from vk.vkreceiver_message_handler import MessageHandler


class ValidOptionTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True)

    def pipeline(self, wordlist: list, expected_answer: tuple):
        message_handler_object = MessageHandler(event_dict_simple_message)
        text_instance = TextParser(message_handler_object)
        handler_object = IntervalPhraseCommandHandler(text_instance, self.chat_db_object)
        handler_object.wordlist = ["/phrase"] + wordlist
        returned_value = handler_object.valid_option()
        self.assertEqual(returned_value, expected_answer)

    def test_option_info(self):
        self.pipeline(["info"], (True, "info"))

    def test_option_add_nothing(self):
        expected_answer = "Напишите фразы для бота после команды /phrase add. Используйте разделитель '|'," \
                          " если хотите добавить сразу несколько фраз."
        self.pipeline(["add"], (False, expected_answer))

    def test_option_add_phrase(self):
        self.pipeline(["add", "word|", "word", "|word", "|"], (True, "add"))

    def test_option_wrong(self):
        expected_answer = "У команды /phrase нет опции 'asdf'"
        self.pipeline(["asdf"], (False, expected_answer))

    def test_remove_nothing(self):
        expected_answer = "После команды /phrase remove нужно написать id фраз, которые вы хотите удалить, " \
                          "например '/phrase remove 35, 44, 28'. Узнать id фраз можно командой /phrase info."
        self.pipeline(["remove"], (False, expected_answer))

    def test_remove_one_phrase(self):
        self.pipeline(["remove", "22"], (True, 'remove'))

    def test_remove_not_digit(self):
        expected_answer = "После команды /phrase remove нужно написать id фраз, которые вы хотите удалить, " \
                          "например '/phrase remove 35, 44, 28'. Узнать id фраз можно командой /phrase info."
        self.pipeline(["remove", "asdf"], (False, expected_answer))

    def test_remove_digit_and_rubbish(self):
        self.pipeline(["remove", "asdf", "34", "dfg", ",", "1"], (True, 'remove'))

    def test_remove_comma_separated(self):
        self.pipeline(["remove", "34,", "11,", "467"], (True, 'remove'))

    def test_remove_whitespace_separated(self):
        self.pipeline(["remove", "34", "11", "467"], (True, 'remove'))

    def test_remove_point_separated(self):
        self.pipeline(["remove", "34.", "11.", "467"], (True, 'remove'))

    def test_remove_all(self):
        self.pipeline(["remove", "all"], (True, 'remove all'))

    def test_remove_all_and_rubbish(self):
        self.pipeline(["remove", "all", "asdffgg"], (True, 'remove all'))


class SharedMethods:

    def pipeline(self, ids_to_remove: set, expected_answer: str):
        message_handler_object = MessageHandler(event_dict_simple_message)
        text_instance = TextParser(message_handler_object)
        handler_object = IntervalPhraseCommandHandler(text_instance, self.chat_db_object)
        handler_object.ids_to_remove = ids_to_remove
        returned_value = handler_object.remove()
        self.assertEqual(returned_value, expected_answer)

    def check_db_interval_off(self):
        self.assertEqual(self.chat_db_object.interval_mode, False)
        self.assertEqual(self.chat_db_object.interval, None)
        self.assertEqual(self.chat_db_object.messages_till_endpoint, None)

    def check_no_phrases_left(self):
        phrases_from_db = models.IntervalPhrase.objects.filter(chat_id=self.chat_db_object)
        self.assertEqual(len(phrases_from_db), 0)

    def check_phrases_id_left(self, ids_left: set):
        phrases_from_db = models.IntervalPhrase.objects.filter(chat_id=self.chat_db_object)
        ids_from_db = {phrase.id for phrase in phrases_from_db}
        self.assertEqual(ids_from_db, ids_left)


class RemoveImpossibleTest(TransactionTestCase, SharedMethods):
    reset_sequences = True

    def setUp(self):
        self.chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True)

    def test_no_saved_phrases_in_db(self):
        self.pipeline({1, 2, 3}, "Невозможно выполнить удаление: у вас не сохранено ни одной фразы.")

    def test_only_absent_ids(self):
        models.IntervalPhrase.objects.create(chat_id=self.chat_db_object, phrase="phrase1")
        self.pipeline({2, 3}, "Невозможно выполнить удаление: у вас нет фраз с ID 2, 3.")


class RemoveIntervalOffTest(TransactionTestCase, SharedMethods):
    reset_sequences = True

    def setUp(self):
        self.chat_db_object = models.Chat.objects.create(
                    chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True)
        models.IntervalPhrase.objects.create(chat_id=self.chat_db_object, phrase="phrase1")
        models.IntervalPhrase.objects.create(chat_id=self.chat_db_object, phrase="phrase2")
        models.IntervalPhrase.objects.create(chat_id=self.chat_db_object, phrase="phrase3")


    def test_remove_all_some_absent(self):
        self.pipeline({1, 2, 3, 4, 5}, "Фраз с ID 4, 5 у вас нет. Удалены все сохраненные фразы.")
        self.check_no_phrases_left()

    def test_remove_all_all_present(self):
        self.pipeline({1, 2, 3}, "Удалены все сохраненные фразы.")
        self.check_no_phrases_left()

    def test_remove_some_some_absent(self):
        self.pipeline({1, 2, 4}, f"Фраз с ID 4 у вас нет. Фразы с ID 1, 2 удалены.")
        self.check_phrases_id_left({3})

    def test_remove_some_all_present(self):
        self.pipeline({1, 3}, f"Фразы с ID 1, 3 удалены.")
        self.check_phrases_id_left({2})


class RemoveIntervalOn(TransactionTestCase, SharedMethods):
    reset_sequences = True

    def setUp(self):
        self.chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True,
            interval=4, interval_mode=True, messages_till_endpoint=2)
        models.IntervalPhrase.objects.create(chat_id=self.chat_db_object, phrase="phrase1")

    def test_remove_all_some_absent(self):
        self.pipeline({1, 2, 3}, "Фраз с ID 2, 3 у вас нет. Удалены все сохраненные фразы. Режим /interval отключен.")
        self.check_db_interval_off()
        self.check_no_phrases_left()

    def test_remove_all_all_present(self):
        self.pipeline({1}, "Удалены все сохраненные фразы. Режим /interval отключен.")
        self.check_db_interval_off()
        self.check_no_phrases_left()


class RemoveAllTest(TestCase, SharedMethods):


    def pipeline_remove_all(self, expected_answer: str):
        message_handler_object = MessageHandler(event_dict_simple_message)
        text_instance = TextParser(message_handler_object)
        handler_object = IntervalPhraseCommandHandler(text_instance, self.chat_db_object)
        handler_object.option = "remove all"
        returned_value = handler_object.command()
        self.assertEqual(returned_value, expected_answer)

    def setUp(self):
        self.chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True)

    def test_no_saved_phrases_in_db(self):
        self.pipeline_remove_all("Невозможно выполнить удаление: у вас не сохранено ни одной фразы.")

    def test_interval_off(self):
        models.IntervalPhrase.objects.create(chat_id=self.chat_db_object, phrase="phrase1")
        self.pipeline_remove_all("Удалены все сохраненные фразы.")
        self.check_no_phrases_left()

    def test_interval_on(self):
        models.IntervalPhrase.objects.create(chat_id=self.chat_db_object, phrase="phrase1")
        self.chat_db_object.interval_mode = True
        self.chat_db_object.interval = 4
        self.chat_db_object.messages_till_endpoint = 2
        self.chat_db_object.save()
        self.pipeline_remove_all("Удалены все сохраненные фразы. Режим /interval отключен.")
        self.check_db_interval_off()
        self.check_no_phrases_left()


class InfoTest(TransactionTestCase, SharedMethods):

    reset_sequences = True

    def setUp(self):
        self.chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True)

    def pipeline(self, expected_answer: str):
        message_handler_object = MessageHandler(event_dict_simple_message)
        text_instance = TextParser(message_handler_object)
        handler_object = IntervalPhraseCommandHandler(text_instance, self.chat_db_object)
        returned_value = handler_object.info()
        self.assertEqual(returned_value, expected_answer)

    def test_no_phrases(self):
        self.pipeline("Сохраненных фраз для режима /interval: 0.\n")

    def test_one_phrase(self):
        models.IntervalPhrase.objects.create(chat_id=self.chat_db_object, phrase="phrase1")
        self.pipeline("Сохраненных фраз для режима /interval: 1.\nid: 1. Phrase: phrase1\n")

    def test_two_phrases(self):
        models.IntervalPhrase.objects.create(chat_id=self.chat_db_object, phrase="phrase1")
        models.IntervalPhrase.objects.create(chat_id=self.chat_db_object, phrase="phrase2")
        self.pipeline("Сохраненных фраз для режима /interval: 2.\nid: 1. Phrase: phrase1\nid: 2. Phrase: phrase2\n")

    def test_one_big_phrase(self):
        models.IntervalPhrase.objects.create(chat_id=self.chat_db_object, phrase=phrase_3999)
        self.pipeline(f"Сохраненных фраз для режима /interval: 1.\nid: 1. Phrase: {phrase_3999}\n")

    def test_several_phrases_one_big(self):
        models.IntervalPhrase.objects.create(chat_id=self.chat_db_object, phrase="phrase1")
        models.IntervalPhrase.objects.create(chat_id=self.chat_db_object, phrase="phrase2")
        models.IntervalPhrase.objects.create(chat_id=self.chat_db_object, phrase=phrase_3999)
        models.IntervalPhrase.objects.create(chat_id=self.chat_db_object, phrase="phrase4")
        self.pipeline(f"id: 3. Phrase: {phrase_3999}\nid: 4. Phrase: phrase4\n")


class AddTest(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.chat_db_object = models.Chat.objects.create(
            chat_id=OwnerAndBotChatData.peer_id, owner_id=OwnerAndBotChatData.owner_id, conversation_is_registered=True)

    def pipeline(self, text: str, expected_answer: str):
        message_handler_object = MessageHandler(event_dict_simple_message)
        text_instance = TextParser(message_handler_object)
        handler_object = IntervalPhraseCommandHandler(text_instance, self.chat_db_object)
        handler_object.text = "/phrase add " + text
        returned_value = handler_object.add()
        self.assertEqual(returned_value, expected_answer)

    def test_add_one_phrase(self):
        text = "one small phrase"
        expected_answer = f"Сохраненных фраз для режима /interval: 1.\nid: 1. Phrase: one small phrase\n"
        self.pipeline(text, expected_answer)
        phrases_from_db = models.IntervalPhrase.objects.filter(chat_id=self.chat_db_object)
        self.assertEqual(phrases_from_db[0].id, 1)
        self.assertEqual(phrases_from_db[0].phrase, "one small phrase")

    def test_add_several_phrases(self):
        text = "phrase1 | second phrase|third phrase|"
        expected_answer = f"Сохраненных фраз для режима /interval: 3.\nid: 1. Phrase: phrase1\nid: 2. Phrase: second phrase\nid: 3. Phrase: third phrase\n"
        self.pipeline(text, expected_answer)
        phrases_from_db = models.IntervalPhrase.objects.filter(chat_id=self.chat_db_object).order_by('id')
        self.assertEqual(phrases_from_db[0].id, 1)
        self.assertEqual(phrases_from_db[0].phrase, "phrase1")
        self.assertEqual(phrases_from_db[1].id, 2)
        self.assertEqual(phrases_from_db[1].phrase, "second phrase")
        self.assertEqual(phrases_from_db[2].id, 3)
        self.assertEqual(phrases_from_db[2].phrase, "third phrase")

    def test_add_big_phrase(self):
        text = phrase_3999
        expected_answer = f"Сохраненных фраз для режима /interval: 1.\nid: 1. Phrase: {phrase_3999}\n"
        self.pipeline(text, expected_answer)
        phrases_from_db = models.IntervalPhrase.objects.filter(chat_id=self.chat_db_object)
        self.assertEqual(phrases_from_db[0].id, 1)
        self.assertEqual(phrases_from_db[0].phrase, phrase_3999)

    def test_add_too_big_phrase(self):
        text = phrase_3999 + "hop"
        expected_answer = "Сохраненных фраз для режима /interval: 0.\n"
        self.pipeline(text, expected_answer)
        phrases_from_db = models.IntervalPhrase.objects.filter(chat_id=self.chat_db_object)
        self.assertEqual(len(phrases_from_db), 0)

    def test_add_one_too_big_and_two_normal_phrases(self):
        text = phrase_3999 + "hop" + "|phrase1 | second phrase|"
        expected_answer = f"Сохраненных фраз для режима /interval: 2.\nid: 1. Phrase: phrase1\nid: 2. Phrase: second phrase\n"
        self.pipeline(text, expected_answer)
        phrases_from_db = models.IntervalPhrase.objects.filter(chat_id=self.chat_db_object).order_by('id')
        self.assertEqual(phrases_from_db[0].id, 1)
        self.assertEqual(phrases_from_db[0].phrase, "phrase1")
        self.assertEqual(phrases_from_db[1].id, 2)
        self.assertEqual(phrases_from_db[1].phrase, "second phrase")
