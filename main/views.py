from django.shortcuts import render
from django.http import HttpResponse
import requests
from django.views.decorators.csrf import csrf_exempt
from .models import *
from .creditionals import *
import json


# Create your views here.
def index(request):
    return HttpResponse('hello')


# for login
@csrf_exempt
def login(request):
    if request.method == 'POST':
        print('salom')
        print(request)
    return HttpResponse('Botga qaytishingiz mumkin.')


# set webhook
def set_webhook(request):
    response = requests.post(BOT_URL + 'setwebhook?url=' + URL).json()
    return HttpResponse(f'{response}')


# function which take tg message
@csrf_exempt
def get_post(request):
    if request.method == 'POST':
        message = json.loads(request.body)
        # print(message)
        try:
            message = message['message']
            is_message(message)  # if user sent message
        except:
            try:
                message = message['callback_query']
                is_callback_query(message)  # if user callback a query
            except:
                try:
                    message = message['my_chat_member']  # when bot is added to channel
                    if message['new_chat_member']['status'] == 'administrator':  # if bot is administrator
                        channel_id = message['chat']['id']
                        try:
                            channel = Channels_info.objects.get(user_id=channel_id)
                        except:
                            channel = Channels_info.objects.create(title=message['chat']['title'], username=message['chat']['username'], user_id=channel_id, user_type=message['chat']['type'])
                        if message['new_chat_member']['can_post_messages']:
                            channel.can_post_messages  = 'True'
                        else:
                            channel.can_post_messages  = 'False'
                        channel.save()
                    elif message['new_chat_member']['status'] == 'kicked':
                        pass
                except:
                    pass  # sented message from channel
    return HttpResponse('It is working')


# if user sent a message to bot this function start
def is_message(message):
    user_id = message['from']['id']
    try:
        user = BotUser.objects.get(user_id=user_id)  # get user with user_id
    except:
        user = BotUser.objects.create(name=message['from']['first_name'], username=message['from']['username'], user_id=user_id, status='start')  # create user
    if user.status == 'start':
        text = f'Assalomu alaykum hush kelibsiz {user.name}.\nBu bot orqali siz instagram bizness accountingiz va telegram kanalizga bir vaqtda post qo\'ya olesiz.'
        add_account(user, message, text)
    elif user.status == 'sentpost':
        try:
            post_id = message['photo'][2]['file_id']
            user.response_id = '1'
            user.save()
            get_text(message, user, post_id)
        except:
            try:
                post_id = message['video']['file_id']
                get_text(message, user, post_id)
            except:
                pass
    elif user.status == 'sentpost2':
        try:
            text = message['text']
            user.smth_txt = text
            user.save()
            check_post(message, user, text)
        except:
            request_to_bot('sendMessage', {
                'chat_id': message['chat']['id'],
                'text': 'Faqat text kiriting: ',
            })
    elif user.status == 'add_tg':
        message_text = message['text']
        try:
            channel = Channels_info.objects.get(username=message_text)
            if channel.can_post_messages == 'False':
                request_to_bot('sendMessage', {
                    'chat_id': message['chat']['id'],
                    'text': 'Uzr!!!\nBotni admin qilishingiz va post qo\'yishga ruxsat berishingiz kerak.', 
                })
            else:
                user.channel_id = channel.user_id
                user.status = ''
                user.save()
                request_to_bot('sendMessage', {
                    'chat_id': message['chat']['id'],
                    'text': 'Kanal botga muovaqiyyatli qo\'shildi.', 
                })
                all_done(message, user)
        except:
            request_to_bot('sendMessage', {
                'chat_id': message['chat']['id'],
                'text': 'Uzr!!!\nBotni hali kanalga qo\'shmapsiz.\nBoshqatdan urinib ko\'ring.', 
            })
    elif user.status == 'add_insta':
        code = message['text']
        code2 = code[30: -50]
        access_code = requests.get(f'{FACEBOOK_URI}oauth/access_token?client_id={client_id}&redirect_uri={redirect_url}&client_secret={client_secret}&code={code2}').json()
        try:
            access_token = access_code['access_token']
            user.access_token = access_token
            user.save()
            response = requests.get(f'{FACEBOOK_URI}me/accounts?access_token={user.access_token}').json()
            page_list = []
            for i in response['data']:
                page_list.append([{'text': i['name'],'callback_data': i['id']}])
            reply_markup = json.dumps({'inline_keyboard': page_list})
            request_to_bot('sendMessage', {
                'chat_id': message['chat']['id'],
                'text': 'Facebook accountiz muofiqqiyatli ulandi.\nEndi Instagramiz ulangan Facebook pageingizni tanlang.',
                'reply_markup': reply_markup,
            })
            user.extra_status = 'select'
            user.status = 'start'
            user.save()
        except:
            text = access_code['error']['message']
            request_to_bot('sendMessage', {
                'chat_id': message['chat']['id'],
                'text': f'Ooops!\n{text}\nPlease try again.', 
            })        
    elif message['text'] == '🆕 Send Post':
        request_to_bot('sendPhoto', {
            'chat_id': user.user_id,
            'photo': 'AgACAgIAAxkBAAICfGJqib0-uXLXdMMx-BZqNEatIkK-AAIyuzEbFfFRS2x647t4NJNnAQADAgADeAADJAQ',
            'caption': user.smth_txt,
        })
        request_to_bot('sendMessage', {
            'chat_id': message['chat']['id'],
            'text': 'Marhamat postni yuboring:', 
        })
        user.status = 'sentpost'
        user.save()


# if user callback a query from bot this function start
def is_callback_query(message):
    delete_post(message)
    user = BotUser.objects.get(user_id=message['from']['id'])
    if message['data'] == 'finish_post':
        request_to_bot('sendMessage', {
            'chat_id': message['message']['chat']['id'],
            'text': 'Post joylanyabdi...'
        })
        post_media(message, user)
    elif message['data'] == 'add_instagram':
        text = f'Okey!\nInstagram accountini ulash uchun bir-qancha facebookni talablari bor.\nBirinchi navbatda <a href="https://help.instagram.com/176235449218188/?helpref=search&query=connect%20instagram%20with%20facebook%20account&search_session_id=9f085cf6640c51afec7e820741a528f6&sr=0">instagram accountizni facebook accountiz</a>ga ulab olishingiz kerak.\nKeyin instagram accountiz<a href="https://help.instagram.com/502981923235522?fbclid=IwAR2PHyMVuy3NqAomXneNXGkck9JcH7nOWrQegMWkvqAtpTsuz6dLFgAOEi4"> business account</a> bo\'lishi kerak.\nOxirgi qadam <a href="https://help.instagram.com/399237934150902?fbclid=IwAR3186aGuQtZpwEBqP43VMsYOmI3WnubYWS-aD-8HBdV1G-xTYQxGvzlqQM">intagramni facebook page</a>ga ulashingiz kerak.\nVa siz bizga accountizga post qo\'yishga ruhsat berishiz kerak.'
        request_to_bot('sendMessage', {
            'chat_id': message['message']['chat']['id'],
            'text': text,
            'parse_mode': 'HTML',
        })
        text = GET_CODE
        request_to_bot('sendMessage', {
            'chat_id': message['message']['chat']['id'],
            'text': text,
        })
        raqam = message['message']['message_id'] + 2
        request_to_bot('sendMessage', {
            'chat_id': message['message']['chat']['id'],
            'text': 'Shu linkga o\'ting va accountizga post qo\'yishga ruxsat bering.Bu usul mutloqo hafsiz facebook accountizga to\'g\'ridan to\'g\'ri ulanadi.\nVa siz ruhsat berib bo\'lganizdan keyin sizni google sahifasiga to\'g\'ri yo\'naltirilasiz. Va shu linkni bizga yuborasiz.',
            'reply_to_message_id': raqam,
        })
        user.status = 'add_insta'
        user.save()
    elif message['data'] == 'add_telegram':
        text = 'Okey!\nBirinchi botni telegram kanalizga qo\'shing va admin qiling. So\'ngra botga qaytib kanal linkini menga jo\'nating.'
        request_to_bot('sendMessage', {
            'chat_id': message['message']['chat']['id'],
            'text': text,
        })
        user.status = 'add_tg'
        user.save()
    elif user.extra_status == 'select':
        page_id = message['data']
        response = requests.get(f'{FACEBOOK_URI}{page_id}?fields=instagram_business_account&access_token={user.access_token}').json()
        try:
            insta_id = response['instagram_business_account']['id']
            user.instagram_account_id = insta_id
            user.extra_status = ''
            user.save()
            request_to_bot('sendMessage', {
                'chat_id': message['message']['chat']['id'],
                'text': 'Instagram account ulandi.',
            })
            all_done(message['message'], user)
        except:
            request_to_bot('sendMessage', {
                'chat_id': message['message']['chat']['id'],
                'text': 'Bu facebook pagega hech qanday instagram account ulanmagan.\nIltimos yaxshilab tekshirib ko\'ring yoki boshqasini tanlang.',
            })
            request_to_bot('sendMessage', {
                'chat_id': message['message']['chat']['id'],
                'text': message['message']['text'],
                'reply_markup': json.dumps(message['message']['reply_markup'])
            })


# functions 


# if all account added
def all_done(message, user):
    if user.access_token != '' and user.channel_id != '':
        request_to_bot('sendMessage', {
            'chat_id': message['chat']['id'],
            'text': 'menyu tanlang',
            'reply_markup': json.dumps({
                'keyboard': [['🆕 Send Post']],
                'resize_keyboard': True
            })
        })
        user.status = ''
        user.save()
    else:
        text = 'Endi boshqa accountni ulang:'
        add_account(user, message, text)


# if user sent only media to bot rerequest for its caption 
def get_text(message, user, post_id):
    user.smth_url = post_id
    user.save()
    try:
        text = message['caption']
        user.smth_txt = text
        user.save()
        check_post(message, user, text)
    except:
        request_to_bot('sendMessage', {
            'chat_id': message['chat']['id'],
            'text': 'Iltimos media uchun sarlavha(caption or text) kiriting: '
        })
        user.status = 'sentpost2'
        user.save()


# sent message for asking add account
def add_account(user, message, text):
    if user.extra_status == '1':
        request_to_bot('sendMessage', {
            'chat_id': message['chat']['id'],
            'text': 'Iltimos birinchi accountingizni qo\'shing',
        })
    else:
        user.extra_status = '1'
        user.save()
    request_to_bot('sendMessage', {
            'chat_id': message['chat']['id'],
            'text': text,
            'reply_markup': json.dumps({'inline_keyboard': [[
                {
                    'text': '➕ Instagram',
                    'callback_data': 'add_instagram'
                }
            ],
            [
                {
                    'text': '➕ Telegram',
                    'callback_data': 'add_telegram'
                }
            ]]})
        })


# check post asking for user
def check_post(message, user, text):
    if user.response_id == '1':
        request_to_bot('sendPhoto', {
            'chat_id': message['chat']['id'],
            'photo': user.smth_url,
            'caption': f'{text}\n\n\nPost to\'g\'rimi?',
            'reply_markup': json.dumps({'inline_keyboard': [[
                {
                    'text': '✔️ Yes',
                    'callback_data': 'finish_post'
                }
            ]]})
        })
    else:
        request_to_bot('sendVideo', {
            'chat_id': message['chat']['id'],
            'video': user.smth_url,
            'caption': f'{text}\n\n\nPost to\'g\'rimi?',
            'reply_markup': json.dumps({'inline_keyboard': [[
                {
                    'text': '✔️ Yes',
                    'callback_data': 'finish_post'
                }
            ]]})
        })
    user.status = ''
    user.save()


# post media to instagram and telegram
def post_media(message, user):
    post_id = request_to_bot2('getFile', {
        'file_id': user.smth_url,
    })
    if user.response_id == '1':
        response = requests.post(
            f'{FACEBOOK_URI}{user.instagram_account_id}/media?image_url={download_url}{post_id}&caption={user.smth_txt}&access_token={user.access_token}').json()
    else:
        response = requests.post(
            f'{FACEBOOK_URI}{user.instagram_account_id}/media?media_type=VIDEO&video_url={download_url}{post_id}&caption={user.smth_txt}&access_token={user.access_token}').json()
    try:
        response = response['id']
        resp = True
    except:
        request_to_bot('sendMessage', {
            'chat_id': message['message']['chat']['id'],
            'text': response['error']['error_user_msg'],
        })
        resp = False
    if resp:
        smth = True
        while smth:
            response2 = requests.post(f'{FACEBOOK_URI}{user.instagram_account_id}/media_publish?creation_id={response}&access_token={user.access_token}').json()
            try:
                response2 = response2['id']
                request_to_bot('sendMessage', {
                    'chat_id': message['message']['chat']['id'],
                    'text': 'Past instagramga muofiqiyatli joylashtirildi.🎉'
                })
                smth = False
            except:
                pass
        if user.response_id == '1':
            print('salom')
            request_to_bot('sendPhoto', {
                'chat_id': user.channel_id,
                'photo': user.smth_url,
                'caption': user.smth_txt,
            })
        else:
            request_to_bot('sendVideo', {
                'chat_id': user.channel_id,
                'video': user.smth_url,
                'caption': user.smth_txt,
            })
        request_to_bot('sendMessage', {
            'chat_id': message['message']['chat']['id'],
            'text': 'Post telegramga qo\'yildi'
        })
    user.response_id = ''
    user.save()


def delete_post(message):
    request_to_bot('deleteMessage', {
        'chat_id': message['message']['chat']['id'],
        'message_id': message['message']['message_id'],
    })


# for request to telegram to sent something to bot
def request_to_bot(request_type, data):
    return requests.post(BOT_URL + request_type, data)


def request_to_bot2(request_type, data):
    response = requests.post(BOT_URL + request_type, data).json()
    response = response['result']['file_path']
    return response