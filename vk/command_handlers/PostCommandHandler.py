from vk.command_handler import *
import random
#TODO: переименовать всё в рандом пост

class PostCommandHandler(CommandHandler):
    def __init__(self, text_instance, chatconversation_db_object):
        super().__init__(text_instance, chatconversation_db_object)

    def process(self):
        code_logger.debug(f'PostCommandHandler. process function.')
        if self.conversation_type == 'user':
            if not super().get_chatconversation_db_object():
                return
            if not super().check_for_owner():
                return
            self.wordlist = self.wordlist[0:1] + self.wordlist[2:]
        if super().check_for_admin() and super().check_for_registration() and super().limit_length(1):
            if not self.chatconversation_db_object.random_post_mode:
                self.send_message('Cannot send random post. '
                                  'First you should register the group like this: /grouppost https://vk.com/link_to_the_group')
                return
            self.command_post()

    def command_post(self):
        code_logger.debug('PostCommandHandler. command_post function.')
        workgroup = '-' + models.ChatSetting.objects.get(
            peer_id=self.chatconversation_db_object).random_post_group
        code_logger.debug(f'PostCommandHandler. command_post function. ID of the workgroup: {workgroup}')
        post_quantity = helpers.make_request_vk('wall.get', personal=True, count=1, owner_id=workgroup)['response'][
            'count']
        code_logger.debug(
            f'PostCommandHandler. command_post function. Number of posts on the workgroup wall: {post_quantity}')
        if post_quantity == 0:
            super().send_message("The wall is empty.")
            return
        max_offset = post_quantity - 1
        code_logger.debug(f'PostCommandHandler. command_post function. Max offset: {max_offset}')
        random_offset = random.randint(0, max_offset)
        code_logger.debug(f'PostCommandHandler. command_post function. Random offset: {random_offset}')
        one_post = helpers.make_request_vk('wall.get', personal=True, count=1,
                                           offset=random_offset, owner_id=workgroup)['response']['items'][0]
        one_post_id = one_post['id']
        code_logger.debug(f'ID of the post that will be sent: {one_post_id}')
        attachment = 'wall' + workgroup + '_' + str(one_post_id)
        helpers.make_request_vk(
            'messages.send', random_id=helpers.randomid(),
            attachment=attachment, peer_id=self.chatconversation_db_object.peer_id)
