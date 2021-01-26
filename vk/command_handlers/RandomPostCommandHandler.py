from vk.actions.RandomPostAction import RandomPostAction
from vk.command_handler import *

from vk.helpers import random_post


class RandomPostCommandHandler(CommandHandler):
    def __init__(self, text_instance, chat_db_object):

        super().__init__(text_instance, chat_db_object)
        self.command_word = random_post

    def valid_option(self):
        return super().common_group_valid_option(random_post)

    def process_chat(self):

        if len(self.wordlist) == 1:
            self.option = "post"
            bot_answer = self.command()
        else:
            if self.from_id == self.chat_db_object.owner_id:  # not using check_for_owner 'cause we don't want to send not-owner-message yet
                option = self.valid_option()
                if option[0]:
                    self.option = option[1]
                    bot_answer = self.command()

                else:
                    bot_answer = option[1]
            else:
                option = self.valid_option()
                if option[0]:
                    bot_answer = f"Для вас доступна команда {random_post} без дополнительных опций."
                else:
                    bot_answer = option[1]
                super().send_message(bot_answer)
        return bot_answer

    def process_user(self):

        proceed, bot_answer = super().process_user_part()
        if proceed:
            if len(self.wordlist) == 1:
                self.option = "post"
                bot_answer = self.command()
            else:
                option = self.valid_option()
                if option[0]:
                    self.option = option[1]
                    bot_answer = self.command()

                else:
                    bot_answer = option[1]

        return bot_answer

    def command(self):
        """
        Method "wall.get" is available only with personal tokens or with service tokens.
        Group tokens aren't allowed.

        """
        self.setting_db_object = models.RandomPostSetting.objects.get(chat_id=self.chat_db_object)
        if self.option == 'post':
            if self.setting_db_object.random_post_mode:
                return RandomPostAction(self.peer_id, self.setting_db_object, self.chat_db_object).process()
            else:
                if self.from_id == self.chat_db_object.owner_id:
                    bot_answer = f"Чтобы включить команду {random_post}, воспользуйтесь командой {random_post} on."
                    super().send_message(bot_answer)
                else:
                    bot_answer = "nothing will be sent"

        elif self.option == "delete":
            if self.setting_db_object.random_post_group_link:
                self.setting_db_object.random_post_mode = False
                self.setting_db_object.random_post_group_link = ""
                self.setting_db_object.random_post_group_id = None
                self.setting_db_object.save()
                bot_answer = f'Группа для команды {random_post} удалена из настроек. Команда {random_post} выключена.'
            else:
                bot_answer = f"У вас нет сохраненной группы для команды {random_post}."
            super().send_message(bot_answer)

        elif self.option == 'off':
            if self.setting_db_object.random_post_mode:
                self.setting_db_object.random_post_mode = False
                self.setting_db_object.save()
                bot_answer = f'Команда {random_post} выключена.'
            else:
                bot_answer = f'Команда {random_post} уже выключена.'
            super().send_message(bot_answer)

        elif self.option == 'on':
            proceed, bot_answer = self.check_for_personal_token()

            if proceed:
                if self.setting_db_object.random_post_group_link:
                    group = self.setting_db_object.random_post_group_link

                    if not self.setting_db_object.random_post_mode:
                        self.setting_db_object.random_post_mode = True
                        self.setting_db_object.save()
                        bot_answer = f'Команда {random_post} включена. По этой команде в чат будет приходить случайно выбранный пост из группы {group}.'
                    else:
                        bot_answer = f'Команда {random_post} уже включена. Группа в настройках: {group}.'
                else:
                    bot_answer = f"Чтобы пользоваться командой '{random_post} on', сохраните в настройках ссылку на группу. " \
                                 f"Сделать это можно командой {random_post} group," \
                                 f" например: {random_post} group https://vk.com/link_to_the_group"
            super().send_message(bot_answer)


        elif self.option == 'info':
            if self.setting_db_object.random_post_group_link:
                group = self.setting_db_object.random_post_group_link
                if self.setting_db_object.random_post_mode:
                    bot_answer = f'Команда {random_post} включена. Группа в настройках: {group}.'
                    super().send_message(bot_answer)
                else:
                    bot_answer = f'Для команды {random_post} у вас зарегистрирована группа {group}. Команда {random_post} выключена.'
                    super().send_message(bot_answer)
            else:
                bot_answer = f"У вас нет сохраненной группы для команды {random_post}."
                super().send_message(bot_answer)

        else:

            group_screen_name, group_id = self.option

            random_post_group_link = "https://vk.com/" + group_screen_name
            self.setting_db_object.random_post_group_link = random_post_group_link
            self.setting_db_object.random_post_group_id = group_id
            self.setting_db_object.save()

            if not self.setting_db_object.random_post_mode:

                bot_answer = f'Группа {random_post_group_link} сохранена в настройках.' \
                             f' Чтобы включить команду {random_post} , воспользуйтесь командой {random_post} on'
            else:
                bot_answer = f'Группа {random_post_group_link} сохранена в настройках.' \
                             f' Команда {random_post} включена.'
            super().send_message(bot_answer)
            return bot_answer
        return bot_answer

