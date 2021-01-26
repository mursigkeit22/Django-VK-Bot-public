from django.core.exceptions import ValidationError

from vk.command_handler import *
from vk.helpers import new_post



class NewPostCommandHandler(CommandHandler):

    def __init__(self, text_instance, chat_db_object):

        super().__init__(text_instance, chat_db_object)
        self.command_word = new_post

    def process_user(self):
        return super().process_user_full()

    def valid_option(self):
        return super().common_group_valid_option(new_post)

    def command(self):

        self.setting_db_object = models.NewPostSetting.objects.get(chat_id=self.chat_db_object)
        if self.option == 'off':
            if self.setting_db_object.newpost_mode:
                self.setting_db_object.newpost_mode = False
                self.setting_db_object.save()
                bot_answer = f'Режим {new_post} выключен, свежие посты присылаться не будут.'
            else:
                bot_answer = f'Команда {new_post} уже выключена.'
            super().send_message(bot_answer)

        elif self.option == 'on':
            proceed, bot_answer = self.check_for_personal_token()

            if proceed:
                if self.setting_db_object.newpost_group_link:
                    group = self.setting_db_object.newpost_group_link
                    if self.setting_db_object.newpost_mode:
                        bot_answer = f'Команда {new_post} уже включена. Группа в настройках: {group}.'
                        super().send_message(bot_answer)

                    else:
                        self.setting_db_object.newpost_mode = True
                        self.setting_db_object.save()

                        bot_answer = f'Режим {new_post} включен. Посты группы {group} будут приходить в ваш чат по мере их появления.'
                        super().send_message(bot_answer)
                else:
                    bot_answer = f"Чтобы пользоваться командой '{new_post} on', сохраните в настройках ссылку на группу. " \
                                 f"Сделать это можно командой {new_post} group," \
                                 f" например: {new_post} group https://vk.com/link_to_the_group"
                    super().send_message(bot_answer)
            else:
                super().send_message(bot_answer)

        elif self.option == 'info':
            if self.setting_db_object.newpost_group_link:
                group = self.setting_db_object.newpost_group_link
                if self.setting_db_object.newpost_mode:
                    bot_answer = f'Команда {new_post} включена. Группа в настройках: {group}.'
                    super().send_message(bot_answer)
                else:
                    bot_answer = f'Для команды {new_post} у вас зарегистрирована группа {group}. Команда {new_post} выключена.'
                    super().send_message(bot_answer)
            else:
                bot_answer = f"У вас нет сохраненной группы для команды {new_post}."
                super().send_message(bot_answer)

        elif self.option == 'delete':
            if self.setting_db_object.newpost_group_link:
                self.setting_db_object.newpost_mode = False
                self.setting_db_object.newpost_group_link = ""
                self.setting_db_object.newpost_group_id = None
                self.setting_db_object.latest_newpost_timestamp = 0
                self.setting_db_object.save()
                bot_answer = f'Группа для режима {new_post} удалена из настроек, свежие посты присылаться не будут.'
            else:
                bot_answer = f'У вас нет сохраненной группы для команды {new_post}.'
            super().send_message(bot_answer)

        else:
            group_screen_name, group_id = self.option

            newpost_group_link = "https://vk.com/" + group_screen_name
            self.setting_db_object.newpost_group_link = newpost_group_link
            self.setting_db_object.newpost_group_id = group_id
            self.setting_db_object.latest_newpost_timestamp = 0
            self.setting_db_object.save()
            if not self.setting_db_object.newpost_mode:

                bot_answer = f'Группа {newpost_group_link} сохранена в настройках.' \
                             f' Чтобы получать обновления из этой группы, воспользуйтесь командой {new_post} on'
            else:
                bot_answer = f'Группа {newpost_group_link} сохранена в настройках.' \
                             f' Посты этой группы будут приходить в ваш чат по мере их появления.'
            super().send_message(bot_answer)
        return bot_answer


