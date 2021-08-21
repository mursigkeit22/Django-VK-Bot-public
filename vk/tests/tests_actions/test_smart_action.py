from django.test import TestCase

from vk import models
from vk.tests.data_for_tests.message_data import OwnerAndBotChatData, input_data
from vk.helpers import smart, option_add, option_regex
from vk.tests.shared.pipelines_and_setups import PipelinesAndSetUps

from vk.vkreceiver_event_handler import EventHandler


class SharedMethods(TestCase, PipelinesAndSetUps):
    @classmethod
    def setUpTestData(cls):
        cls.setup_chat(True, smart_mode=True)
        cls.create_settings_tables()


class ActionSmartTest(SharedMethods):
    @classmethod
    def setUpTestData(cls):
        cls.setup_chat(True, smart_mode=True)
        models.SmartReply.objects.create(chat_id=cls.chat_db_object, trigger="hello",
                                         reply="hello")
        models.SmartReply.objects.create(chat_id=cls.chat_db_object, trigger="hello murlo",
                                         reply="murlo")

    def test_no_such_trigger(self):
        self.core_pipeline(OwnerAndBotChatData.peer_id, OwnerAndBotChatData.owner_id,
                           "good morning", "SMART_NOT_TRIGGER")

    def test_some_match_words(self):
        self.core_pipeline(OwnerAndBotChatData.peer_id, OwnerAndBotChatData.owner_id,
                           "hello good morning murlo", "SMART_NOT_TRIGGER")

    def test_full_match(self):
        self.core_pipeline(OwnerAndBotChatData.peer_id, OwnerAndBotChatData.owner_id,
                           "hello murlo", "SMART_REPLY_SENT", bot_response="murlo")


class ActionSmartExtraSpacesTest(SharedMethods):
    @classmethod
    def setUpTestData(cls):
        cls.setup_chat(True, smart_mode=True)
        models.SmartReply.objects.create(chat_id=cls.chat_db_object, trigger="hello murlo",
                                         reply="end")
        models.SmartReply.objects.create(chat_id=cls.chat_db_object, trigger="hello murlo purlo",
                                         reply="shur")

    def test_extra_spaces(self):
        self.core_pipeline(OwnerAndBotChatData.peer_id, OwnerAndBotChatData.owner_id,
                           "hello    murlo", "SMART_REPLY_SENT", bot_response="end")

    def test_extra_spaces_line_break(self):
        self.core_pipeline(OwnerAndBotChatData.peer_id, OwnerAndBotChatData.owner_id,
                           "hello    murlo \n purlo", "SMART_REPLY_SENT", bot_response="shur")


class ActionSmartNameTest(SharedMethods):

    def test_only_name(self):
        models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger="hello murlo",
                                         reply="@имя@")
        self.core_pipeline(OwnerAndBotChatData.peer_id, OwnerAndBotChatData.owner_id,
                           "hello murlo", "SMART_REPLY_SENT", bot_response="Валерия")

    def test_name_in_the_middle(self):
        models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger="hello murlo",
                                         reply="Hello, @имя@, hello!")
        self.core_pipeline(OwnerAndBotChatData.peer_id, OwnerAndBotChatData.owner_id,
                           "hello murlo", "SMART_REPLY_SENT", bot_response="Hello, Валерия, hello!")

    def test_name_in_the_end(self):
        models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger="hello murlo",
                                         reply="Hello, @имя@!")
        self.core_pipeline(OwnerAndBotChatData.peer_id, OwnerAndBotChatData.owner_id,
                           "hello murlo", "SMART_REPLY_SENT", bot_response="Hello, Валерия!")

    def test_name_in_the_beginning(self):
        models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger="hello murlo",
                                         reply="@имя@, привет!")
        self.core_pipeline(OwnerAndBotChatData.peer_id, OwnerAndBotChatData.owner_id,
                           "hello murlo", "SMART_REPLY_SENT", bot_response="Валерия, привет!")

    def test_two_names(self):
        models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger="hello murlo",
                                         reply="@имя@, привет, @имя@!")
        self.core_pipeline(OwnerAndBotChatData.peer_id, OwnerAndBotChatData.owner_id,
                           "hello murlo", "SMART_REPLY_SENT", bot_response="Валерия, привет, Валерия!")

    def test_name_without_spaces(self):
        models.SmartReply.objects.create(chat_id=self.chat_db_object, trigger="hello murlo",
                                         reply="asdf@имя@ghjk")

        self.core_pipeline(OwnerAndBotChatData.peer_id, OwnerAndBotChatData.owner_id,
                           "hello murlo", "SMART_REPLY_SENT", bot_response="asdfВалерияghjk")


class ActionSmartFullCycle(SharedMethods):

    def test(self):
        text = f'{smart} add regex' + r' \bкирил[ауе]?\b || olala'
        data = input_data(OwnerAndBotChatData.peer_id, text, OwnerAndBotChatData.owner_id)
        EventHandler(data).process()
        self.core_pipeline(OwnerAndBotChatData.peer_id, OwnerAndBotChatData.owner_id,
                           "вдупляй,кирил", "SMART_REPLY_SENT", bot_response="olala")
        self.core_pipeline(OwnerAndBotChatData.peer_id, OwnerAndBotChatData.owner_id,
                           "у кирила", "SMART_REPLY_SENT", bot_response="olala")

        self.core_pipeline(OwnerAndBotChatData.peer_id, OwnerAndBotChatData.owner_id,
                           "кириллица", "SMART_NOT_TRIGGER")


class ActionSmartUpperCaseFullCycle(SharedMethods):

    def test_no_regex(self):
        text = f"{smart} {option_add} Привет, кукушонок! || Сам привет!"
        data = input_data(OwnerAndBotChatData.peer_id, text, OwnerAndBotChatData.owner_id)
        EventHandler(data).process()
        self.core_pipeline(OwnerAndBotChatData.peer_id, OwnerAndBotChatData.owner_id,
                           "Привет, кукушонок!", "SMART_REPLY_SENT", bot_response="Сам привет!")
        self.core_pipeline(OwnerAndBotChatData.peer_id, OwnerAndBotChatData.owner_id,
                           "привет, кукушонок!", "SMART_REPLY_SENT", bot_response="Сам привет!")

        self.core_pipeline(OwnerAndBotChatData.peer_id, OwnerAndBotChatData.owner_id,
                           "Привет!", "SMART_NOT_TRIGGER")

    def test_regex1(self):
        text = rf"{smart} {option_add} {option_regex} \bСлов[оауе]*\b || Ответ "
        data = input_data(OwnerAndBotChatData.peer_id, text, OwnerAndBotChatData.owner_id)
        EventHandler(data).process()
        self.core_pipeline(OwnerAndBotChatData.peer_id, OwnerAndBotChatData.owner_id,
                           "Слово", "SMART_REPLY_SENT", bot_response="Ответ")
        self.core_pipeline(OwnerAndBotChatData.peer_id, OwnerAndBotChatData.owner_id,
                           "Слова", "SMART_REPLY_SENT", bot_response="Ответ")
        self.core_pipeline(OwnerAndBotChatData.peer_id, OwnerAndBotChatData.owner_id,
                           "нет Слов", "SMART_REPLY_SENT", bot_response="Ответ")

        self.core_pipeline(OwnerAndBotChatData.peer_id, OwnerAndBotChatData.owner_id,
                           "Словесный", "SMART_NOT_TRIGGER")
        self.core_pipeline(OwnerAndBotChatData.peer_id, OwnerAndBotChatData.owner_id,
                           "слово", "SMART_NOT_TRIGGER")
        self.core_pipeline(OwnerAndBotChatData.peer_id, OwnerAndBotChatData.owner_id,
                           "нет слов", "SMART_NOT_TRIGGER")
        self.core_pipeline(OwnerAndBotChatData.peer_id, OwnerAndBotChatData.owner_id,
                           "нет СЛОВ", "SMART_NOT_TRIGGER")

    def test_regex2(self):
        text = rf"{smart} {option_add} {option_regex} \bОлег[ауе] || Я знаю Олега! "
        data = input_data(OwnerAndBotChatData.peer_id, text, OwnerAndBotChatData.owner_id)
        EventHandler(data).process()
        self.core_pipeline(OwnerAndBotChatData.peer_id, OwnerAndBotChatData.owner_id,
                           "дай Олегу печеньку", "SMART_REPLY_SENT", bot_response="Я знаю Олега!")
        self.core_pipeline(OwnerAndBotChatData.peer_id, OwnerAndBotChatData.owner_id,
                           "Олега не было", "SMART_REPLY_SENT", bot_response="Я знаю Олега!")
        self.core_pipeline(OwnerAndBotChatData.peer_id, OwnerAndBotChatData.owner_id,
                           "об Олеге", "SMART_REPLY_SENT", bot_response="Я знаю Олега!")
        self.core_pipeline(OwnerAndBotChatData.peer_id, OwnerAndBotChatData.owner_id,
                           "Олегу", "SMART_REPLY_SENT", bot_response="Я знаю Олега!")

        self.core_pipeline(OwnerAndBotChatData.peer_id, OwnerAndBotChatData.owner_id,
                           "дай олегу печеньку", "SMART_NOT_TRIGGER")
        self.core_pipeline(OwnerAndBotChatData.peer_id, OwnerAndBotChatData.owner_id,
                           "Олег", "SMART_NOT_TRIGGER")
        self.core_pipeline(OwnerAndBotChatData.peer_id, OwnerAndBotChatData.owner_id,
                           "Олежка дурачок", "SMART_NOT_TRIGGER")
