from vk.actions.RandomPostAction import RandomPostAction
from vk.bot_answer import BotAnswer
from vk.command_handler import *

from vk.helpers import random_post, option_info, option_delete, option_on, option_group, option_off
from vk.usertext import random_post_dict
from vk.vkbot_exceptions import PrerequisitesError, AlreadyDoneError


@helpers.class_logger()
class RandomPostCommandHandler(CommandHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.command_word = random_post

    def get_option(self):
        self.setting_db_object = models.RandomPostSetting.objects.get(
            chat_id=self.chat_db_object)
        if not self.setting_db_object.random_post_mode:
            self.check_for_owner_silent_option(
                error_description="random_post_mode is false. Nothing will be sent.")
        if len(self.wordlist) == 1:
            self.option = "post"
            return
        self.check_for_owner_silent_option(
            bot_response=f"Для вас доступна команда {self.command_word} без дополнительных опций.")
        super().common_group_get_option()

    def process_chat(self):
        self.get_option()
        return self.command()

    def process_user(self):
        super().process_user_part()
        self.get_option()
        return self.command()

    def command(self):
        """
        Method "wall.get" is available only with personal tokens or with service tokens.
        Group tokens aren't allowed.

        """

        if self.option == 'post':
            if self.setting_db_object.random_post_mode:
                return RandomPostAction(self.setting_db_object, self.chat_db_object, self.message).process()
            else:
                raise PrerequisitesError(self.message,
                                         bot_response=f"Чтобы включить команду {self.command_word}, воспользуйтесь командой {random_post} {option_on}.")

        elif self.option == option_delete:
            if self.setting_db_object.random_post_group_link:
                self.setting_db_object.random_post_mode = False
                self.setting_db_object.random_post_group_link = ""
                self.setting_db_object.random_post_group_id = None
                self.setting_db_object.save()
                bot_response = random_post_dict['delete']
                return BotAnswer("RANDOM_POST_DELETE", self.message, bot_response=bot_response)
            else:
                raise PrerequisitesError(self.message,
                                         bot_response=random_post_dict['delete_cannot'])

        elif self.option == option_off:
            if self.setting_db_object.random_post_mode:
                self.setting_db_object.random_post_mode = False
                self.setting_db_object.save()
                return BotAnswer("RANDOM_POST_OFF", self.message, bot_response=random_post_dict['off'])
            else:
                raise AlreadyDoneError(self.message, bot_response=random_post_dict['off_already'])

        elif self.option == option_on:
            self.check_for_personal_token()

            if self.setting_db_object.random_post_group_link:
                group = self.setting_db_object.random_post_group_link

                if not self.setting_db_object.random_post_mode:
                    self.setting_db_object.random_post_mode = True
                    self.setting_db_object.save()
                    bot_response = random_post_dict['on'].substitute(group_link=group)
                    return BotAnswer("RANDOM_POST_ON", self.message, bot_response=bot_response)
                else:
                    bot_response = random_post_dict['on_already'].substitute(group_link=group)
                    raise AlreadyDoneError(self.message, bot_response=bot_response)
            else:
                bot_response = random_post_dict['on_cannot']
                raise PrerequisitesError(self.message, bot_response=bot_response)

        elif self.option == option_info:
            if self.setting_db_object.random_post_group_link:
                group = self.setting_db_object.random_post_group_link
                if self.setting_db_object.random_post_mode:
                    bot_response = random_post_dict['info_on'].substitute(group_link=group)
                else:
                    bot_response = random_post_dict['info_off'].substitute(group_link=group)
            else:
                bot_response = random_post_dict['info_no_group']
            return BotAnswer("RANDOM_POST_INFO", self.message, bot_response=bot_response)

        else:
            group_screen_name, group_id = self.option

            random_post_group_link = "https://vk.com/" + group_screen_name
            self.setting_db_object.random_post_group_link = random_post_group_link
            self.setting_db_object.random_post_group_id = group_id
            self.setting_db_object.save()

            if not self.setting_db_object.random_post_mode:
                bot_response = random_post_dict['group_saved_off'].substitute(group_link=random_post_group_link)
            else:
                bot_response = random_post_dict['group_saved_on'].substitute(group_link=random_post_group_link)
            return BotAnswer("RANDOM_POST_GROUP", self.message, bot_response=bot_response)
