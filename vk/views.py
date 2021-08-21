import json

from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import logging
import vk.helpers
import time

from vk.vkreceiver_event_handler import EventHandler
from web_vk.constants import CONFIRMATION_RESPONSE, VK_SECRET

from vk.tasks import wait_period_of_time, wait_period_of_time2, vkreceiver_task, test_retry_task

logger_vkreceiver = logging.getLogger('vkreceiver')
site_logger = logging.getLogger('site')


@csrf_exempt
def celery_test(request):
    if request.method == 'POST':
        post_body = json.loads(request.body)
        wait_period_of_time.apply_async(args=(int(post_body), request.id),
                                        priority=1)  # request.id will be used by log_request_id library
        return HttpResponse("done waiting!")
    else:

        test_retry_task.apply_async(args=(request.get_host(), request.id), priority=2)

        return HttpResponse('it was get')


@csrf_exempt
def celery_test2(request):
    if request.method == 'POST':
        post_body = json.loads(request.body)
        wait_period_of_time2.apply_async(args=(int(post_body),
                                               request.id),
                                         priority=7)  # request.id will be used by log_request_id library

        return HttpResponse("Task 2. done waiting!")
    else:
        time.sleep(3)
        return HttpResponse('it was get from celery_test2')


def capacity_test(request):
    logger_vkreceiver.info('==================== capacity1 ====================')
    my_dict = {}
    count = 1000
    offset = 0
    flag = True
    while flag:
        logger_vkreceiver.info(f"offset:  {offset}")
        a = time.time()
        users = vk.helpers.make_request_vk("groups.getMembers", personal=True, count=count, offset=offset,
                                           group_id='the4gkz', fields='sex')['response']['items']
        logger_vkreceiver.info(f"request duration: {time.time() - a:.10f}")
        if len(users) == 0:
            flag = False
        b = time.time()
        for user in users:
            if 'deactivated' in user:
                my_dict[user['id']] = user['deactivated']
        logger_vkreceiver.info(f"update dict duration: {time.time() - b:.10f}")
        offset += count
    return HttpResponse(len(my_dict))


@csrf_exempt
def capacity_test2(request):
    if request.method == 'POST':
        post_body = json.loads(request.body)
        time.sleep(int(post_body))

        return HttpResponse("done waiting!")
    else:
        return HttpResponse('it was get in capacity2')


@csrf_exempt
def vkreceiver(request):
    logger_vkreceiver.info(request)
    if request.method == 'POST':
        try:
            vkreceiver_object = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            return HttpResponseBadRequest("BAD JSON")

        logger_vkreceiver.info('====================')
        logger_vkreceiver.info(vkreceiver_object)

        event_object = EventHandler(vkreceiver_object)
        if event_object.event_type == "confirmation":
            return HttpResponse(CONFIRMATION_RESPONSE)
        if event_object.vk_secret_key != VK_SECRET:
            return HttpResponseForbidden('AUTHENTICATION ERROR')

        vkreceiver_task.delay(event_object.__dict__, request.id)

        return HttpResponse('ok')

    else:
        return HttpResponse('it was get')
