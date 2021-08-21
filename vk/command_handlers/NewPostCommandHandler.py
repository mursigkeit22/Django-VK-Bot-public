from vk.bot_answer import BotAnswer
from vk.command_handler import *
from vk.helpers import newpost, option_off, option_on, option_info, option_delete
from vk.usertext import newpost_dict


@helpers.class_logger()
class NewPostCommandHandler(CommandHandler):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.command_word = newpost

    def process_user(self):
        return super().process_user_full()

    def get_option(self):
        return super().common_group_get_option()

    def command(self):

        self.setting_db_object = models.NewPostSetting.objects.get(chat_id=self.chat_db_object)
        if self.option == option_off:
            if self.setting_db_object.newpost_mode:
                self.setting_db_object.newpost_mode = False
                self.setting_db_object.save()
                return BotAnswer("NEWPOST_OFF", self.message, bot_response=newpost_dict["off"])
            else:
                raise AlreadyDoneError(self.message, bot_response=newpost_dict["off_already"])

        elif self.option == option_on:
            self.check_for_personal_token()

            if self.setting_db_object.newpost_group_link:
                group = self.setting_db_object.newpost_group_link
                if self.setting_db_object.newpost_mode:
                    bot_response = newpost_dict["on_already"].substitute(group_link=group)
                    raise AlreadyDoneError(self.message, bot_response=bot_response)
                else:
                    self.setting_db_object.newpost_mode = True
                    self.setting_db_object.save()
                    bot_response = newpost_dict["on"].substitute(group_link=group)
                    return BotAnswer("NEWPOST_ON", self.message, bot_response=bot_response)
            else:
                bot_response = newpost_dict["on_cannot"]
                raise PrerequisitesError(self.message, bot_response=bot_response)

        elif self.option == option_info:
            if self.setting_db_object.newpost_group_link:
                group = self.setting_db_object.newpost_group_link
                if self.setting_db_object.newpost_mode:
                    bot_response = newpost_dict["info_on"].substitute(group_link=group)
                else:
                    bot_response = newpost_dict["info_off"].substitute(group_link=group)
            else:
                bot_response = newpost_dict["info_no_group"]
            return BotAnswer("NEWPOST_INFO", self.message, bot_response=bot_response)

        elif self.option == option_delete:
            if self.setting_db_object.newpost_group_link:
                self.setting_db_object.newpost_mode = False
                self.setting_db_object.newpost_group_link = ""
                self.setting_db_object.newpost_group_id = None
                self.setting_db_object.latest_newpost_timestamp = 0
                self.setting_db_object.save()
                bot_response = newpost_dict["delete"]
                return BotAnswer("NEWPOST_DELETE", self.message, bot_response=bot_response)
            else:
                raise PrerequisitesError(self.message,
                                         bot_response=newpost_dict["delete_cannot"])

        else:
            group_screen_name, group_id = self.option

            newpost_group_link = "https://vk.com/" + group_screen_name
            self.setting_db_object.newpost_group_link = newpost_group_link
            self.setting_db_object.newpost_group_id = group_id
            self.setting_db_object.latest_newpost_timestamp = 0
            self.setting_db_object.save()
            if not self.setting_db_object.newpost_mode:
                bot_response = newpost_dict["group_saved_off"].substitute(group_link=newpost_group_link)
            else:
                bot_response = newpost_dict["group_saved_on"].substitute(group_link=newpost_group_link)
            return BotAnswer("NEWPOST_GROUP", self.message, bot_response=bot_response)
