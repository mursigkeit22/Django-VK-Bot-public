import os
import json
import vk.handlers as handlers
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import logging
logger_vk = logging.getLogger('vkreceiver')

confirmation_response = os.environ['CONFIRMATION_RESPONSE']


def home(request):
    return HttpResponse('main page, only get')


@csrf_exempt
def vkreceiver(request):
    if request.method == 'POST':
        logger_vk.info('====================')
        logger_vk.info(json.loads(request.body))
        answer = handlers.PostRequestHandler(request).process()
        if answer == 'confirmation':
            return HttpResponse(confirmation_response)
        return HttpResponse('ok')      # два потока?

    else:
        return HttpResponse('it was get')
