from django.core.management.base import BaseCommand, CommandError
import vk.models as models
from vk import helpers


class Command(BaseCommand):
    help = 'Gets the latest post from the chosen wall and sends it to chat.'

    def add_arguments(self, parser):
        parser.add_argument('peer_id', nargs=1, type=int)

    def handle(self, *args, **options):
        self.stdout.write('Newpost script starts working')
        peer_id = options['peer_id'][0]
        self.stdout.write(f'peer_id: {peer_id}')

        chatconversation_db_object = models.ChatConversation.objects.get(peer_id=peer_id)
        if not chatconversation_db_object.newpost_mode:
            self.stdout.write(f'newpost_mode if off for chat {peer_id}.')
            return
        setting_object = models.ChatSetting.objects.get(peer_id=chatconversation_db_object)
        workgroup = '-' + setting_object.newpost_group
        previous_timestamp = setting_object.latest_newpost_timestamp

        two_upper_posts = helpers.make_request_vk('wall.get', personal=True, count=2,
                                                  owner_id=workgroup)['response']['items']  # только записи сообщества или нет?
        if len(two_upper_posts) == 0:
            self.stdout.write(f'Newpost script. Wall of group with ID {workgroup} is empty')
            return
        self.stdout.write(f'previous_timestamp: {previous_timestamp}')

        temp_latest_timestamp = previous_timestamp
        for post in two_upper_posts:
            if post['date'] > temp_latest_timestamp:
                temp_latest_timestamp = post['date']
                latest_post = post
                self.stdout.write(f'type of "post": {type(latest_post)}')
        if temp_latest_timestamp > previous_timestamp:
            setting_object.latest_newpost_timestamp = temp_latest_timestamp
            setting_object.save()
            newest_post_id = str(latest_post['id'])
            self.stdout.write(f'ID of the post that will be sent: {newest_post_id}')
            attachment = 'wall' + workgroup + '_' + newest_post_id
            helpers.make_request_vk(
                'messages.send', random_id=helpers.randomid(),
                attachment=attachment, peer_id=peer_id)
