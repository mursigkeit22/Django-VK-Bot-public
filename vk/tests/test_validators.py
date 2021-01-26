from django.core.exceptions import ValidationError
from django.test import SimpleTestCase
from vk.validators import group_validator
import vk.tests.data_for_tests.group_links as links
import re


class ValidatorsTest(SimpleTestCase):
    def test_split_longer_than_one(self):
        value = "firstword secondword"
        self.assertRaises(ValidationError, group_validator, value)

    def test_wrong_screenname0(self):
        value = "gkx"
        self.assertRaises(ValidationError, group_validator, value)

    def test_group_is_deactivated(self):
        value = links.deactivated_group
        self.assertRaises(ValidationError, group_validator, value)

    def test_wrong_screenname1(self):
        value = "https://vk.com/wrongscreenname"
        self.assertRaises(ValidationError, group_validator, value)

    def test_wrong_screenname2(self):
        value = "http://vk.com/wrongscreenname"
        self.assertRaises(ValidationError, group_validator, value)

    def test_id_instead_of_screenname(self):
        value = str(links.normal_group1ID)
        self.assertEqual(group_validator(value), ('study_english_every_day', links.normal_group1ID))

    def test_mobile_link(self):
        value = "https://m.vk.com/study_english_every_day?from=groups"
        self.assertEqual(group_validator(value), ('study_english_every_day', 162171215))

    def test_app_and_desktop_address(self):
        value = links.normal_group2
        self.assertEqual(group_validator(value), ("rgubru", links.normal_group2ID))

    def test_mobile_cut_link(self):
        value = "study_english_every_day?from=groups"
        self.assertEqual(group_validator(value), ('study_english_every_day', 162171215))

    def test_wrong_pattern(self):
        value = re.sub('public', 'rublic', links.public_name)
        self.assertRaises(ValidationError, group_validator, value)

    def test_right_pattern_wrong_id(self):
        value = links.public_name[:-1]
        self.assertRaises(ValidationError, group_validator, value)

    def test_event(self):
        value = links.event_name
        self.assertEqual(group_validator(value), (f'club{links.event_nameID}', links.event_nameID))

    def test_public(self):
        value = links.public_name
        self.assertEqual(group_validator(value), (f'club{links.public_nameID}', links.public_nameID))

    def test_event_closed(self):
        value = links.closed_event_name
        self.assertRaises(ValidationError, group_validator, value)

    def test_user_really_wants_botgroup(self): # for Varya only
        value = str(links.this_bot_id)
        self.assertEqual(group_validator(value), (f'club{links.this_bot_id}', links.this_bot_id))
