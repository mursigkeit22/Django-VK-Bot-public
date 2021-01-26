from django.core.exceptions import ValidationError

from vk.command_handler import *
from vk.actions.RemoveAction import RemoveAction
from vk.helpers import remove
from vk.validators import group_validator


class RemoveCommandHandler(CommandHandler):

    def valid_option(self):
        if len(self.wordlist) == 1:
            return True, "remove"
        return super().common_group_valid_option(remove)

    def process_chat(self):

        is_owner, bot_answer = self.check_for_owner()
        if is_owner:
            option = self.valid_option()
            if option[0]:
                self.option = option[1]
                bot_answer = self.command()

            else:
                bot_answer = option[1]

        return bot_answer

    def process_user(self):
        proceed, bot_answer = self.process_user_part()
        if proceed:
            option = self.valid_option()
            if option[0]:
                self.option = option[1]
                bot_answer = self.command()

            else:
                bot_answer = option[1]
        return bot_answer

    def command(self):

        self.setting_db_object = models.KickNonMembersSetting.objects.get(chat_id=self.chat_db_object)

        if self.option == "remove":
            if self.setting_db_object.kick_nonmembers_mode:
                return RemoveAction(self.peer_id, self.setting_db_object, self.chat_db_object).command()

            bot_answer = f"Чтобы включить команду {remove}, воспользуйтесь командой {remove} on."
            super().send_message(bot_answer)

        elif self.option == 'off':
            if self.setting_db_object.kick_nonmembers_mode:
                self.setting_db_object.kick_nonmembers_mode = False
                self.setting_db_object.save()
                bot_answer = f'Команда {remove} выключена.'
            else:
                bot_answer = f'Команда {remove} уже выключена.'
            super().send_message(bot_answer)

        elif self.option == 'on':
            if self.setting_db_object.kick_nonmembers_group_link:
                group = self.setting_db_object.kick_nonmembers_group_link

                if self.setting_db_object.kick_nonmembers_mode:
                    bot_answer = f'Команда {remove} уже включена. Группа в настройках: {group}.'
                    super().send_message(bot_answer)

                else:
                    self.setting_db_object.kick_nonmembers_mode = True
                    self.setting_db_object.save()
                    bot_answer = f'Команда {remove} включена. С её помощью вы можете удалять из чата участников, которые не состоят в группе {group}.'
                    super().send_message(bot_answer)

            else:
                bot_answer = f"Чтобы пользоваться командой '{remove} on', сохраните в настройках ссылку на группу. " \
                             f"Сделать это можно командой {remove} group," \
                             f" например: {remove} group https://vk.com/link_to_the_group"
                super().send_message(bot_answer)

        elif self.option == 'info':
            if self.setting_db_object.kick_nonmembers_group_link:
                group = self.setting_db_object.kick_nonmembers_group_link
                if self.setting_db_object.kick_nonmembers_mode:
                    bot_answer = f'Команда {remove} включена. Группа в настройках: {group}.'
                    super().send_message(bot_answer)
                else:
                    bot_answer = f'Для команды {remove} у вас зарегистрирована группа {group}. Команда {remove} выключена.'
                    super().send_message(bot_answer)
            else:
                bot_answer = f"У вас нет сохраненной группы для команды {remove}."
                super().send_message(bot_answer)

        elif self.option == 'delete':
            if self.setting_db_object.kick_nonmembers_group_link:
                self.setting_db_object.kick_nonmembers_mode = False
                self.setting_db_object.kick_nonmembers_group_link = ""
                self.setting_db_object.kick_nonmembers_group_id = None
                self.setting_db_object.save()
                bot_answer = f'Группа для команды {remove} удалена из настроек. Команда {remove} выключена.'
            else:
                bot_answer = f'У вас нет сохраненной группы для команды {remove}.'
            super().send_message(bot_answer)

        else:
            group_screen_name, group_id = self.option

            kick_nonmembers_group_link = "https://vk.com/" + group_screen_name
            self.setting_db_object.kick_nonmembers_group_link = kick_nonmembers_group_link
            self.setting_db_object.kick_nonmembers_group_id = group_id
            self.setting_db_object.save()
            if not self.setting_db_object.kick_nonmembers_mode:

                bot_answer = f'Группа {kick_nonmembers_group_link} сохранена в настройках.' \
                             f' Чтобы включить команду {remove} , воспользуйтесь командой {remove} on'
            else:
                bot_answer = f'Группа {kick_nonmembers_group_link} сохранена в настройках. Команда {remove} включена.'

            super().send_message(bot_answer)
        return bot_answer
