from vk import models
from vk.helpers import option_info, option_group, option_delete, option_on, option_off
from vk.tests.data_for_tests.message_data import OwnerAndBotChatData
from vk.tests.shared.pipelines_and_setups import PipelinesAndSetUps
import vk.tests.data_for_tests.group_links as links
from vk.usertext import common_dict


class NOGROUPTestMixin(PipelinesAndSetUps):

    def test_info(self):
        bot_response = self.text_dict['info_no_group']
        self.pipeline_chat_from_owner(option_info, f"{self.command_code}_INFO", bot_response=bot_response)
        self.pipeline_user(option_info, f"{self.command_code}_INFO", bot_response=bot_response)

    def test_delete_chat(self):
        bot_response = self.text_dict['info_no_group']
        self.pipeline_chat_from_owner(f"{option_group} {option_delete}", "PREREQUISITES_ERROR",
                                      bot_response=bot_response)
        self.pipeline_user(f"{option_group} {option_delete}", "PREREQUISITES_ERROR", bot_response=bot_response)

    def test_on_chat(self):
        bot_response = self.text_dict['on_cannot']
        self.pipeline_chat_from_owner(option_on, "PREREQUISITES_ERROR", bot_response=bot_response)
        self.pipeline_user(option_on, "PREREQUISITES_ERROR", bot_response=bot_response)

    def test_off_chat(self):
        bot_response = self.text_dict['off_already']
        self.pipeline_chat_from_owner(option_off, "ALREADY_DONE", bot_response=bot_response)
        self.pipeline_user(option_off, "ALREADY_DONE", bot_response=bot_response)

    def test_not_valid_option_chat(self):
        bot_response = f"У команды {self.command} нет опции 'asdf'."
        self.pipeline_chat_from_owner("asdf", 'WRONG_OPTION', bot_response=bot_response)
        self.pipeline_user("asdf", 'WRONG_OPTION', bot_response=bot_response)

    def test_chat_not_owner(self):
        bot_response = f'Только владелец беседы может использовать команду {self.command}.'
        self.pipeline_chat_not_owner(option_info, 'NOT_OWNER', bot_response=bot_response)


class THEREISGROUPOffTestMixin(PipelinesAndSetUps):

    def test_info(self):
        bot_response = self.text_dict['info_off'].substitute(group_link=links.normal_group1, )
        self.pipeline_chat_from_owner(option_info, f"{self.command_code}_INFO", bot_response=bot_response)
        self.pipeline_user(option_info, f"{self.command_code}_INFO", bot_response=bot_response)

    def test_off(self):
        bot_response = self.text_dict['off_already']
        self.pipeline_chat_from_owner(option_off, "ALREADY_DONE", bot_response=bot_response)
        self.pipeline_user(option_off, "ALREADY_DONE", bot_response=bot_response)

    def test_chat_not_owner(self):
        bot_response = f'Только владелец беседы может использовать команду {self.command}.'
        self.pipeline_chat_not_owner(option_info, 'NOT_OWNER', bot_response=bot_response)


class THEREISGROUPOnTestMixin(PipelinesAndSetUps):

    def test_info(self):
        bot_response = self.text_dict['info_on'].substitute(group_link=links.normal_group1, )
        self.pipeline_chat_from_owner(option_info, f"{self.command_code}_INFO", bot_response=bot_response)
        self.pipeline_user(option_info, f"{self.command_code}_INFO", bot_response=bot_response)

    def test_on(self):
        bot_response = self.text_dict['on_already'].substitute(group_link=links.normal_group1, )
        self.pipeline_chat_from_owner(option_on, "ALREADY_DONE", bot_response=bot_response)
        self.pipeline_user(option_on, "ALREADY_DONE", bot_response=bot_response)

    def test_chat_not_owner(self):
        bot_response = f'Только владелец беседы может использовать команду {self.command}.'
        self.pipeline_chat_not_owner(option_on, 'NOT_OWNER', bot_response=bot_response)


class TurnOffDeleteChangeONMixin(PipelinesAndSetUps):

    def test_off_chat(self):
        bot_response = self.text_dict['off']
        self.pipeline_chat_from_owner(option_off, f"{self.command_code}_OFF", bot_response=bot_response)
        self.check_db(False, links.normal_group1, links.normal_group1ID)

    def test_off_user(self):
        bot_response = self.text_dict['off']
        self.pipeline_user(option_off, f"{self.command_code}_OFF", bot_response=bot_response)
        self.check_db(False, links.normal_group1, links.normal_group1ID)

    def test_delete_chat(self):
        bot_response = self.text_dict['delete']
        self.pipeline_chat_from_owner(f"{option_group} {option_delete}",
                                      f"{self.command_code}_DELETE", bot_response=bot_response)
        self.check_db(False, "", None)

    def test_delete_user(self):
        bot_response = self.text_dict['delete']
        self.pipeline_user(f"{option_group} {option_delete}",
                           f"{self.command_code}_DELETE", bot_response=bot_response)
        self.check_db(False, "", None)

    def test_change_group_chat(self):
        bot_response = self.text_dict['group_saved_on'].substitute(group_link=links.normal_group2)
        self.pipeline_chat_from_owner(f"{option_group} {links.normal_group2}",
                                      f"{self.command_code}_GROUP", bot_response=bot_response)
        self.check_db(True, links.normal_group2, links.normal_group2ID)

    def test_change_group_user(self):
        bot_response = self.text_dict['group_saved_on'].substitute(group_link=links.normal_group2)
        self.pipeline_user(f"{option_group} {links.normal_group2}",
                           f"{self.command_code}_GROUP", bot_response=bot_response)
        self.check_db(True, links.normal_group2, links.normal_group2ID)

    def test_chat_not_owner(self):
        bot_response = f'Только владелец беседы может использовать команду {self.command}.'
        self.pipeline_chat_not_owner(f'{option_group} {option_delete}', 'NOT_OWNER', bot_response=bot_response)


class TurnOnDeleteChangeOFFMixin(PipelinesAndSetUps):

    def test_change_group_chat(self):
        bot_response = self.text_dict['group_saved_off'].substitute(group_link=links.normal_group2)
        self.pipeline_chat_from_owner(f"{option_group} {links.normal_group2}", f"{self.command_code}_GROUP",
                                      bot_response=bot_response)
        self.check_db(False, links.normal_group2, links.normal_group2ID)

    def test_change_group_user(self):
        bot_response = self.text_dict['group_saved_off'].substitute(group_link=links.normal_group2)
        self.pipeline_user(f"{option_group} {links.normal_group2}", f"{self.command_code}_GROUP",
                           bot_response=bot_response)
        self.check_db(False, links.normal_group2, links.normal_group2ID)

    def test_on_group_chat(self):
        bot_response = self.text_dict['on'].substitute(group_link=links.normal_group1, )
        self.pipeline_chat_from_owner(option_on, f"{self.command_code}_ON", bot_response=bot_response)
        self.check_db(True, links.normal_group1, links.normal_group1ID)

    def test_on_group_user(self):
        bot_response = self.text_dict['on'].substitute(group_link=links.normal_group1, )
        self.pipeline_user(option_on, f"{self.command_code}_ON", bot_response=bot_response)
        self.check_db(True, links.normal_group1, links.normal_group1ID)

    def test_delete_chat(self):
        bot_response = self.text_dict['delete']
        self.pipeline_chat_from_owner(f"{option_group} {option_delete}", f"{self.command_code}_DELETE",
                                      bot_response=bot_response)
        self.check_db(False, "", None)

    def test_delete_user(self):
        bot_response = self.text_dict['delete']
        self.pipeline_user(f"{option_group} {option_delete}", f"{self.command_code}_DELETE", bot_response=bot_response)
        self.check_db(False, "", None)


class AddGroupMixin(PipelinesAndSetUps):

    def test_add_group_chat(self):
        bot_response = self.text_dict['group_saved_off'].substitute(group_link=links.normal_group2, )
        self.pipeline_chat_from_owner(f"group {links.normal_group2}", f"{self.command_code}_GROUP",
                                      bot_response=bot_response)
        self.check_db(False, links.normal_group2, links.normal_group2ID)

    def test_add_group_user(self):
        bot_response = self.text_dict['group_saved_off'].substitute(group_link=links.normal_group2, )
        self.pipeline_user(f"group {links.normal_group2}", f"{self.command_code}_GROUP", bot_response=bot_response)
        self.check_db(False, links.normal_group2, links.normal_group2ID)

    def test_add_bad_group_chat(self):
        bot_response = common_dict['bad_group'].substitute(group_link=links.nonexisting_group, command=self.command)
        self.pipeline_chat_from_owner(f"group {links.nonexisting_group}", "WRONG_GROUP", bot_response=bot_response)
        self.check_db(False, "", None)

    def test_add_bad_group_user(self):
        bot_response = common_dict['bad_group'].substitute(group_link=links.nonexisting_group, command=self.command)
        self.pipeline_user(f"group {links.nonexisting_group}", "WRONG_GROUP", bot_response=bot_response)
        self.check_db(False, "", None)


class NoProfileModeOFFMixin(PipelinesAndSetUps):
    def get_bot_response(self):
        bot_response = common_dict['not_login'].substitute(command=f"{self.command} {option_on}")
        return bot_response

    def test_on_group_user(self):
        self.pipeline_user(option_on, "USER_PROFILE_ERROR", bot_response=self.get_bot_response())

    def test_on_group_chat(self):
        self.pipeline_chat_from_owner(option_on, "USER_PROFILE_ERROR", bot_response=self.get_bot_response())


class ExpiredTokenModeOFFMixin(PipelinesAndSetUps):
    def get_bot_response(self):
        bot_response = common_dict['refresh_token'].substitute(command=f"{self.command} {option_on}")
        return bot_response

    def test_on_group_user(self):
        self.pipeline_user(option_on, "USER_PROFILE_ERROR", bot_response=self.get_bot_response())

    def test_on_group_chat(self):
        self.pipeline_chat_from_owner(option_on, "USER_PROFILE_ERROR", bot_response=self.get_bot_response())
