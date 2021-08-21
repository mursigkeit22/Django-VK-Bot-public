import logging
import os
import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from vk import helpers
from vk.references import GroupReference

code_logger = logging.getLogger('code_process')
bot_groupid = int(os.environ['BOT_GROUPID'])


# example:
# def validate_even(value):
#     if value % 2 != 0:
#         raise ValidationError(
#             _('%(value)s is not an even number'),
#             params={'value': value},
#         )

def public_or_event(group_name):
    group_type = re.search(r'^(event|public)', group_name)[0]
    if group_type == "public":
        group_type = "page"
    group_id = re.search(r'\d{1,}$', group_name)[0]
    response_content = helpers.make_request_vk('groups.getById', group_id=group_id)
    code_logger.info(response_content)
    group = GroupReference(response_content)
    if group_type == group.type and group.is_closed == 0 and group.deactivated is None:
        return True, (group.screen_name, group.group_id)
    else:
        return False, group


def group_validator(value):

    """
    Works both for forms and code.
    If value in form is empty, it doesn't end up in validator.

    App and desktop link example:  https://vk.com/rgubru
    Mobile version link example:  https://m.vk.com/study_english_every_day?from=groups
    Valid are all kinds of working links, group screen name and group id.

    NB: vk group screen names like "public12345" or "event6789" are not actual vk screen names,
    so links like https://vk.com/public200069033 need some additional work (done below).
    Actual vk screen names are club12345 (with type = page) and club6789 (with type = event) respectively.

    NB: when using group token (not personal token), groups.getById request doesn't return an error
    in case of non-existent group name etc. Instead, when something goes wrong,
    it returns information of a group which token is used (so in this case - this bot's info).
    """

    code_logger.debug(f'In  validate_group: {value}')
    error_text = 'Группа %(value)s не может быть зарегистрирована для случайных постов.' \
                 ' Убедитесь, что ссылка правильная, и группа не является закрытой'
    if len(value.split()) > 1:
        code_logger.debug("In  validate_group. Supposed group link has spaces.")

        raise ValidationError(_(error_text),
                              params={'value': value},
                              )
    group_name = value.split('vk.com/')[-1]
    group_name = group_name.split('?')[0]  # in case of link from mobile version

    pattern = r'^(event|public)\d{1,}$'  # in case of links like https://vk.com/public200069033 or https://vk.com/event200069033
    if re.fullmatch(pattern, group_name):
        proceed, info = public_or_event(group_name)
        if proceed:
            screen_name, group_id = info[0], info[1]
            return screen_name, group_id
        else:
            group = info
    else:
        response_content = helpers.make_request_vk('groups.getById', group_id=group_name)
        code_logger.info(response_content)
        group = GroupReference(response_content)
        if group.is_closed == 0 and group.deactivated is None:
            if group.group_id != bot_groupid:  # normal case
                return group.screen_name, group.group_id
            else:
                if group.screen_name == group_name or str(
                        group.group_id) == group_name:  # if user really wanted bot group, else - an error has occured
                    return group.screen_name, group.group_id

    code_logger.debug(
        f'In group_validator. group.screen_name: {group.screen_name},  group_name (from user): {group_name}, '
        f' group.is_closed: {group.is_closed},  group.deactivated: {group.deactivated}')
    raise ValidationError(_(error_text),
                          params={'value': value},
                          )
