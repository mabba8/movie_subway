from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, PostbackEvent, FollowEvent
from .robot import Adam
from django.http import HttpResponse

# Create your views here.
line_bot_api = LineBotApi('b8c+EloUjPhs/nCv2PGkyI905gbBaZ+VYwbMkjN9Zuw8av/+tLZxprXNcaB7F8qNN4qrq08NYMSAHJszAlSFt5hhkmZyEp2o07onwaKaQW4XuHoEmQkINe+z4f587gqJkHAwWOh80K13dFAHhZxwjgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('ebc727b638a1c9c6aa8a2c804c7eb1df')
robot = Adam()

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')

        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()
        return HttpResponse()
    else:
        return HttpResponseBadRequest()


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    print(event)
    robot.eyes(event)
    print('robot see: {}'.format(robot.sees))
    robot.response(event)


@handler.add(PostbackEvent)
def handle_postback_message(event):
    print(event)
    robot.eyes(event)
    print('robot see: {}'.format(robot.sees))
    robot.response(event)


@handler.add(FollowEvent)
def handle_postback_message(event):
    print(event)
    robot.eyes(event)
    print('robot see: {}'.format(robot.sees))
    robot.response(event)
