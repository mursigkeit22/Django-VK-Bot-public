from django.core.management.base import BaseCommand, CommandError
import vk.models as models
from vk import helpers
import datetime
import uuid

from vk.helpers import PersonalTokenException


class Command(BaseCommand):
    help = 'Gets the latest post from the chosen wall and sends it to chat.'

    def add_arguments(self, parser):
        parser.add_argument('peer_id', nargs=1, type=int)

    def handle(self, *args, **options):
        unique_string = uuid.uuid4().hex[:10].upper()
        peer_id = options['peer_id'][0]
        self.stdout.write(
            f'{unique_string} [{datetime.datetime.now()}] Newpost script starts working for peer_id = {peer_id}')

        chatconversation_db_object = models.Chat.objects.get(chat_id=peer_id)
        chat_owner = chatconversation_db_object.owner_id
        setting_object = models.NewPostSetting.objects.get(chat_id=chatconversation_db_object)
        if not setting_object.newpost_mode:
            self.stdout.write(f'{unique_string} [{datetime.datetime.now()}] Newpost_mode is off for chat {peer_id}.')
            return
        self.stdout.write(f'{unique_string} [{datetime.datetime.now()}] Setting_object from database is received.')
        workgroup = '-' + str(setting_object.newpost_group_id)
        previous_timestamp = setting_object.latest_newpost_timestamp
        self.stdout.write(f'{unique_string} [{datetime.datetime.now()}] Ready to get two upper posts from the wall.')
        try:
            two_upper_posts = helpers.make_request_vk('wall.get', personal=True, chat_owner=chat_owner, count=2,
                                                      owner_id=workgroup)
        except PersonalTokenException as e:
            self.stdout.write(
                f'{unique_string} [{datetime.datetime.now()}] {e}')
            return
        try:
            two_upper_posts = two_upper_posts['response']['items']
        except KeyError:
            self.stdout.write(f'{unique_string} [{datetime.datetime.now()}] KeyError while getting two upper posts: {two_upper_posts["error"]["error_msg"]} Workgroup {workgroup}')
            return



        self.stdout.write(
            f'{unique_string} [{datetime.datetime.now()}] Two upper posts are received.')
        if len(two_upper_posts) == 0:
            self.stdout.write(f'{unique_string} [{datetime.datetime.now()}] Newpost script. Group {setting_object.newpost_group_link}. Wall is empty.')
            return
        self.stdout.write(f'{unique_string} [{datetime.datetime.now()}] previous_timestamp: {previous_timestamp}')

        temp_latest_timestamp = previous_timestamp
        for post in two_upper_posts:
            if post['date'] > temp_latest_timestamp:
                temp_latest_timestamp = post['date']
                latest_post = post


        if temp_latest_timestamp > previous_timestamp:
            setting_object.latest_newpost_timestamp = temp_latest_timestamp
            setting_object.save()
            self.stdout.write(
                f'{unique_string} [{datetime.datetime.now()}] New latest_timestamp = {temp_latest_timestamp} is saved to database.')
            newest_post_id = str(latest_post['id'])
            self.stdout.write(
                f'{unique_string} [{datetime.datetime.now()}] New post with ID {newest_post_id} will be sent.')
            attachment = 'wall' + workgroup + '_' + newest_post_id
            helpers.make_request_vk(
                'messages.send', random_id=helpers.randomid(),
                attachment=attachment, peer_id=peer_id)
            self.stdout.write(
                f'{unique_string} [{datetime.datetime.now()}] Message with new post (ID {newest_post_id}) is sent.')
        else:
            self.stdout.write(f'{unique_string} [{datetime.datetime.now()}] No new posts to send.')
