import os
import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import logging
import vk.helpers
import time

from vk.vkreceiver_event_handler import EventHandler
from web_vk.constants import CONFIRMATION_RESPONSE, VK_SECRET

logger_vk = logging.getLogger('vkreceiver')



def capacity_test(request):
    logger_vk.info('==================== capacity1 ====================')
    my_dict = {}
    count = 1000
    offset = 0
    flag = True
    while flag:
        logger_vk.info(f"offset:  {offset}")
        a = time.time()
        users = vk.helpers.make_request_vk("groups.getMembers", personal=True, count=count, offset=offset,
                                           group_id='the4gkz', fields='sex')['response']['items']
        logger_vk.info(f"request duration: {time.time() - a:.10f}")
        if len(users) == 0:
            flag = False
        b = time.time()
        for user in users:
            if 'deactivated' in user:
                my_dict[user['id']] = user['deactivated']
        logger_vk.info(f"update dict duration: {time.time() - b:.10f}")
        offset += count
    return HttpResponse(len(my_dict))


def capacity_test2(request):
    logger_vk.info('==================== capacity2 ====================')
    time.sleep(11)

    return HttpResponse("capacity2")


@csrf_exempt
def vkreceiver(request):
    if request.method == 'POST':
        vkreceiver_object = json.loads(request.body)

        logger_vk.info('====================')
        logger_vk.info(vkreceiver_object)

        event_object = EventHandler(vkreceiver_object)
        if event_object.event_type == "confirmation":
            return HttpResponse(CONFIRMATION_RESPONSE)
        if event_object.vk_secret_key != VK_SECRET:
            return HttpResponse('wrong VK secret key')

        event_object.process()
        return HttpResponse('ok')

    else:
        return HttpResponse('it was get')
