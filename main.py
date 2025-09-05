from flask import Flask, render_template, request, redirect, url_for, g, jsonify, make_response
from requests.auth import HTTPBasicAuth
from db import sync_controller as dbs
from flask_caching import Cache
from dotenv import load_dotenv
from flask_cors import CORS
import datetime as dt
import urllib.parse
import functools
import requests
import logging
import hashlib
import base64
import json
import time
import hmac
import jwt
import os
import re

application = Flask(__name__)

application.config['CACHE_TYPE'] = 'FileSystemCache'  # Файловое кеширование
application.config['CACHE_DIR'] = '/cache/'  # Папка для хранения
application.config['CACHE_DEFAULT_TIMEOUT'] = 18000  # Время жизни кеша в секундах

cache = Cache(application)
CORS(application)


load_dotenv(dotenv_path='/dotenv/.env')
BOT_TOKEN = os.getenv('BOT_TOKEN')
PAYMENT_TOKEN = os.getenv('PAYMENT_TOKEN') 
SECRET_KEY = os.getenv('SECRET_KEY')
WEBDAV_URL = os.getenv('WEBDAV_URL') # Путь к директории
WEBDAV_USERNAME = os.getenv('WEBDAV_USERNAME')
WEBDAV_PASSWORD = os.getenv('WEBDAV_PASSWORD')


logging.basicConfig(
    filename='/logs/app.log',
    level=logging.DEBUG,  # Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def validate_init_data(init_data: str, bot_token: str):
    vals = {k: urllib.parse.unquote(v) for k, v in [s.split('=', 1) for s in init_data.split('&')]}
    data_check_string = '\n'.join(f"{k}={v}" for k, v in sorted(vals.items()) if k != 'hash')

    secret_key = hmac.new("WebAppData".encode(), bot_token.encode(), hashlib.sha256).digest()
    h = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256)
    if (h.hexdigest() == vals['hash']):
        user_str = vals.get('user')
        user = json.loads(user_str)
        return {'status': True, 'id': user.get('id'), 'username': user.get('username')}
    else:
        return {'status': False}


def create_folder(folder_name):
    folder_url = f'{WEBDAV_URL}/{folder_name}'
    response = requests.request("MKCOL", folder_url, auth=HTTPBasicAuth(WEBDAV_USERNAME, WEBDAV_PASSWORD))
    
    if not response.status_code in (201, 405):
        application.logger.info(f"Произошла ошибка при создании папки: {response.status_code} - {response.text}")


def load_photo(folder_name, filename, file):
    file_url = f'{WEBDAV_URL}/{folder_name}/{filename}'
    # Загрузка изображения в облако (если оно уже существует, то произойдёт его замена)
    load = requests.put(file_url, data=file.stream, auth=HTTPBasicAuth(WEBDAV_USERNAME, WEBDAV_PASSWORD))
    
    if load.status_code in (200, 201):
        return True
    else:
        return False


def delete_folder(folder_name):
    folder_url = f'{WEBDAV_URL}/{folder_name}'
    response = requests.request("DELETE", folder_url, auth=HTTPBasicAuth(WEBDAV_USERNAME, WEBDAV_PASSWORD))
    
    if not response.status_code in (200,204):
        application.logger.info(f"Произошла ошибка при удалении папки: {response.status_code} - {response.text}")


def create_token(tg_id, token_type='access'):
    if token_type not in ('access', 'refresh'):
        return "Указан неверный token_type! Должен быть 'access' или 'refresh'"
    
    created_at = dt.datetime.now(dt.timezone.utc).isoformat()
    expired_at = None
    expired_time = None
    
    if token_type == 'access':
        expired_at = int((dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=3)).timestamp())
        expired_dt = dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=12)
    elif token_type == 'refresh':
        expired_at = int((dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=90)).timestamp())
        expired_dt = dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=90)
        
    payload = {
        'tg_id': tg_id,
        'token_type': token_type,
        'created_at': created_at,
        'exp': expired_at
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token, expired_dt


def verify_token(token, expected_type='access'):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        # Проверяем соответствие типа
        if decoded.get('token_type') != expected_type:
            return None, "TOKEN TYPE ERROR"
        
        return decoded, "VALID TOKEN"
    except jwt.ExpiredSignatureError:
        # Токен просрочен
        return None, "TOKEN TIME IS UP"
    except jwt.InvalidTokenError:
        # Недействительный токен
        return None, "INVALID TOKEN"


def get_payload(token):
    try:
        # Разделяем токен на части
        parts = token.split('.')
        if len(parts) != 3:
            return None  # Неверный формат токена

        header_b64, payload_b64, signature_b64 = parts

        # Добавляем недостающие '=' для корректного декодирования
        def add_padding(b64_string):
            return b64_string + '=' * (-len(b64_string) % 4)

        payload_b64_padded = add_padding(payload_b64)

        # Декодируем payload
        decoded_bytes = base64.urlsafe_b64decode(payload_b64_padded)
        payload_json = decoded_bytes.decode('utf-8')
        payload = json.loads(payload_json)
        return payload
    except Exception as e:
        return None

def get_sign_path(sign):
    sign_path = ""
    if sign == "Овен":
        sign_path = "/static/img/signs/icon_aries.png"
    if sign == "Телец":
        sign_path = "/static/img/signs/icon_taurus.png"
    if sign == "Близнецы":
        sign_path = "/static/img/signs/icon_gemini.png"
    if sign == "Рак ":
        sign_path = "/static/img/signs/icon_cancer.png"
    if sign == "Лев":
        sign_path = "/static/img/signs/icon_leo.png"
    if sign == "Дева":
        sign_path = "/static/img/signs/icon_virgo.png"
    if sign == "Весы":
        sign_path = "/static/img/signs/icon_libra.png"
    if sign == "Скорпион":
        sign_path = "/static/img/signs/icon_scorpio.png"
    if sign == "Стрелец":
        sign_path = "/static/img/signs/icon_sagittarius.png"
    if sign == "Козерог":
        sign_path = "/static/img/signs/icon_capri.png"
    if sign == "Водолей":
        sign_path = "/static/img/signs/icon_aquarius.png"
    if sign == "Рыбы":
        sign_path = "/static/img/signs/icon_pisces.png"
        
    return sign_path
    

def get_match_sign_path(sign):
    sign_path = ""
    if sign == "Овен":
        sign_path = "/static/img/matches/icon_aries_match.png"
    if sign == "Телец":
        sign_path = "/static/img/matches/icon_taurus_match.png"
    if sign == "Близнецы":
        sign_path = "/static/img//matches/icon_gemini_match.png"
    if sign == "Рак ":
        sign_path = "/static/img//matches/icon_cancer_match.png"
    if sign == "Лев":
        sign_path = "/static/img//matches/icon_leo_match.png"
    if sign == "Дева":
        sign_path = "/static/img//matches/icon_virgo_match.png"
    if sign == "Весы":
        sign_path = "/static/img//matches/icon_libra_match.png"
    if sign == "Скорпион":
        sign_path = "/static/img//matches/icon_scorpio_match.png"
    if sign == "Стрелец":
        sign_path = "/static/img//matches/icon_sagittarius_match.png"
    if sign == "Козерог":
        sign_path = "/static/img//matches/icon_capricorn_match.png"
    if sign == "Водолей":
        sign_path = "/static/img//matches/icon_aquarius_match.png"
    if sign == "Рыбы":
        sign_path = "/static/img//matches/icon_pisces_match.png"
        
    return sign_path

def get_sign_description(sign):
    sign_description = ""
    if sign == "Овен":
        sign_description = "Овен ♈️\nСамоуверенный, упрямый, решительный и легкий на подъем человек, который стремится везде быть первым. Он прямолинейный, импульсивный, властный, любит выделиться, поспорить, показать свое превосходство, высказать свое мнение, быть в центре внимания, поэтому его могут считать эгоистом.."
    if sign == "Телец":
        sign_description = "Телец ♉️\nНеторопливый, упрямый и упорный человек, которому важны земные удовольствия (покушать, поспать, секс). Он сосредоточен на материальном мире, на деньгах. Как бы тактильное восприятие мира, верит больше в то, что можно потрогать, в то, что доказано, а какие-то абстрактные вещи могут быть наоборот непонятны. Такому человеку трудно начать что-то делать, сделать первый шаг, но уж если начал что-то делать, то будет упорно идти к своей цели и его уже не остановить"
    if sign == "Близнецы":
        sign_description = "Близнецы ♊️\nЛегкий на подьем, позитивный и дружелюбный человек, для которого важно общение, подпитка новой информацией. Часто он сам является инициатором новых знакомств, может первый начать разговор в компании друзей, потому что не любит скуку и молчание. Характерно любопытство во многих областях, стремление получить как можно больше информации, но до истины не докапывается из-за быстрой смены интересов"
    if sign == "Рак ":
        sign_description = "Рак ♋️\nМягкий, эмоциональный, ранимый и чувствительный человек, которого легко обидеть. Такой человек часто о чем-то переживает, беспокоится. Характерна неуверенность «шаг вперед, два назад», любит возвращаться в прошлое, сильная привязка к корням. Важны семейные ценности, обожает свой дом, вкусно готовить, играть с детьми. Свою семью считает своей защитой. Обладает отличной интуицией и умением чувствовать близких людей"
    if sign == "Лев":
        sign_description = "Лев ♌️\nЯркий, демонстративный и энергичный человек. Но в отличие от Овна, энергию тратит на то дело, которому он предан, от которого получает удовольствие и неважно, сколько на это времени потребуется (Овну же интересно сиюминутное увлечение). Это благородный и щедрый человек, но взамен ему важна похвала, аплодисменты, он хочет быть замеченным, быть в центре внимания"
    if sign == "Дева":
        sign_description = "Дева ♍️\nНадежный человек, который обращает внимание на мелкие детали, умеет концентрироваться на мелочах, от этого его могут считать занудливым, придирчивым и мелочным. Работоспособный. Часто выполняет свою работу самостоятельно, не поручает ее другим, так как считает, что только он может выполнить ее идеально. Про него говорят «в чужом глазу соринку увидит, а в своем бревна не заметит»"
    if sign == "Весы":
        sign_description = "Весы ♎️\nМиролюбивый, деликатный человек, который стремится к гармонии, красоте. В обществе не хамит, не грубит, ведет себя достойно. Несмотря на способность сглаживать углы, у такого человека есть внутренний стержень, и он не будет прогибаться там, где ему не выгодно, он подстроит ситуацию в свою сторону. Может быть зависимым от мнения людей, нерешительным, но только в ежедневных несерьезных вопросах"
    if sign == "Скорпион":
        sign_description = "Скорпион ♏️\nЧувствительный человек, который все эмоции переживает глубоко внутри себя. Умеет продавливать ситуацию в свою сторону, при этом не стесняясь в колких высказываниях. Отлично развита интуиция, человек насквозь чувствует людей и окружающую обстановку. Обладает каким-то магнетизмом, поэтому в его присутствии люди могут открываться как психологу. Не прощает предательство. Такой человек может подолгу вынашивать план мести и нанести удар в самый неподходящий для оппонента момент"
    if sign == "Стрелец":
        sign_description = "Стрелец ♐️\nОптимистичный, дружелюбный и щедрый человек. Выделяется из окружения, любит командовать, учить других людей распространять свои идеи, давать советы. И сам учится постоянно, его легко увлечь чем-то новым. Всегда расширяет свой кругозор, любит путешествовать, изучать чужие культуры и все иностранное. Всегда строит большие планы, не зацикливается на мелочах"
    if sign == "Козерог":
        sign_description = "Козерог ♑️\nОтветственный, дисциплинированный, упрямый человек, который любит порядок во всем, ценит время. Четко знает, чего хочет. Смотрит на ситуацию трезво и хладнокровно, умеет медленно, но верно идти напролом к своей цели. Есть чувство уверенности, настрой на социальный рост"
    if sign == "Водолей":
        sign_description = "Водолей ♒️\nДружелюбный, оптимистичный, демократичный, мечтательный и свободолюбивый человек, часто перекладывает ответственность на других. У него всегда много оригинальных идей. Он больше любит путешествовать, получать из всего максимум информации, преподносить неожиданные сюрпризы и поворачиваться к людям неожиданной стороной"
    if sign == "Рыбы":
        sign_description = "Рыбы ♓️\nСвою чувствительность и ранимость такой человек часто скрывает под маской. Им движут собственные эмоции и порой из-за «розовых очков» он не замечает, что делает что-то не так, ошибается. Ему проще уйти в мир иллюзий и мечтаний, чем взглянуть в глаза реальности. Поэтому есть опасность, что его могут обмануть, он может быть"
        
    return sign_description


def get_type_description(relation_type):
    relation_type_description = ""
    if relation_type == "Я и моё зеркало":
        relation_type_description = "Отличная совместимость только на уровне двух проработанных знаков зодиака. В остальных случаях, слишком похожи и разбивают друг друга, как зеркало.\nИсключение: Рак ♋️ + Рак ♋️, Скорпион ♏️ + Скорпион ♏️.\nДве гармоничные и приятные пары"
    if relation_type == "Лучший враг и лучший друг":
        relation_type_description = "Эта совместимость всегда с химией! Но какой? — вопрос хороший.\nЗдесь все зависит в какой вы позиции: лучшего врага или лучшего друга. В позиции лучшего врага вы всегда будете больше требовать, а в позиции лучшего друга будете ощущать некую зависть"
    if relation_type == "Лучший друг и лучший враг":
        relation_type_description = "Эта совместимость всегда с химией! Но какой? — вопрос хороший.\nЗдесь все зависит в какой вы позиции: лучшего врага или лучшего друга. В позиции лучшего врага вы всегда будете больше требовать, а в позиции лучшего друга будете ощущать некую зависть"
    if relation_type == "Старший брат и младший брат ":
        relation_type_description = "Совместимость хороша для дружбы, бизнеса и путешествий. Но для отношений между мужчиной и женщиной может быть слегка проблематичной, особенно, если женщина — старший брат"
    if relation_type == "Младший брат и старший брат":
        relation_type_description = "Совместимость хороша для дружбы, бизнеса и путешествий. Но для отношений между мужчиной и женщиной может быть слегка проблематичной, особенно, если женщина — старший брат"
    if relation_type == "Советник и покровитель":
        relation_type_description = "Совместимость суперская для бизнеса, совместных дел и партнерских сделок. Особенно, когда вы «покровитель» и нанимаете «советника». Вам будет комфортно работать вместе"
    if relation_type == "Покровитель и советник":
        relation_type_description = "Совместимость суперская для бизнеса, совместных дел и партнерских сделок. Особенно, когда вы «покровитель» и нанимаете «советника». Вам будет комфортно работать вместе"
    if relation_type == "Родитель и ребёнок":
        relation_type_description = "Прекрасная совместимость для длительных и серьезных отношений, особенно для семьи. Но будьте бдительны, «женщина» в этих отношениях будет себя чувствовать отлично на позиции «ребенка», а «мужчина» в позиции «родителя»"
    if relation_type == "Ребёнок и родитель":
        relation_type_description = "Прекрасная совместимость для длительных и серьезных отношений, особенно для семьи. Но будьте бдительны, «женщина» в этих отношениях будет себя чувствовать отлично на позиции «ребенка», а «мужчина» в позиции «родителя»"
    if relation_type == "Удав и кролик":
        relation_type_description = "Смесь гремучая эта совместимость, яркая, токсичная - и она годится для 18+ , интрижек и тд. Для всего остального обратите внимание на остальные совместимости!!!\nСтроить длительные отношения с этой совместимостью себе дороже"
    if relation_type == "Кролик и удав":
        relation_type_description = "Смесь гремучая эта совместимость, яркая, токсичная - и она годится для 18+ , интрижек и тд. Для всего остального обратите внимание на остальные совместимости!!!\nСтроить длительные отношения с этой совместимостью себе дороже"
    if relation_type == "Противоположности притягиваются":
        relation_type_description = "Эта яркая и полная бурлящей энергии совместимость не для юных неокрепших партнеров. Хотя именно в юности их так непреодолимо тянет друг к другу!!! Совместимость одна из самых удачных,но самая сложная в проработке"
        
    return relation_type_description


def get_compatibility_description(result_compatibility):
    compatibility_description = ""
    if result_compatibility >= 10 and result_compatibility <= 30:
        compatibility_description = f"{result_compatibility}% — очень низкая совместимость\nПартнёры как будто говорят на разных языках. Им трудно понять друг друга, даже при наличии влечения. Отношения могут быть бурными, но нестабильными. Рекомендуется избегать союза, если нет особых причин идти на жертвы"
    if result_compatibility >= 31 and result_compatibility <= 40:
        compatibility_description = f"{result_compatibility}% — низкая совместимость\nТакой союз потребует много усилий. Часто возникают конфликты из-за разных темпераментов и жизненных целей. Необходимо серьёзное желание быть вместе, чтобы сохранить отношения"
    if result_compatibility >= 41 and result_compatibility <= 60:
        compatibility_description = f"{result_compatibility}% — средняя совместимость\nОтношения могут быть нестабильными: сегодня всё отлично, завтра — ссоры. Важно учиться слышать партнёра и уважать отличия. Сильные чувства помогут преодолеть сложности"
    if result_compatibility >= 61 and result_compatibility <= 70:
        compatibility_description = f"{result_compatibility}% — умеренно хорошая совместимость\nУ партнёров есть точки соприкосновения, но могут проявляться различия в характерах или приоритетах. Чтобы отношения были крепкими, нужно работать над взаимопониманием и компромиссами"
    if result_compatibility >= 71 and result_compatibility <= 80:
        compatibility_description = f"{result_compatibility}% — очень хорошая совместимость\nПара может прекрасно уживаться, при этом сохраняя индивидуальность. Возможны небольшие разногласия, но они легко решаются. Это надёжный и перспективный союз"
    if result_compatibility >= 81 and result_compatibility <= 100:
        compatibility_description = f"{result_compatibility}% — идеальное совпадение\nЭти пары легко находят общий язык, у них сильное взаимопонимание и схожие взгляды на жизнь. В таких союзах много страсти, доверия и поддержки. Отношения строятся почти без усилий — партнёры как будто дополняют друг друга"
    
    return compatibility_description


def get_age(birth_str):
    age = None
    birth = dt.datetime.strptime(birth_str, "%d.%m.%Y %H:%M").date()
    today = dt.date.today()

    # Вычисляем возраст
    age = today.year - birth.year
    # Проверяем, если день рождения еще не был в этом году, уменьшаем возраст на 1
    if (today.month, today.day) < (birth.month, birth.day):
        age -= 1
    
    if 11 <= age <= 19:
        return age, f'{age} лет'  # Для чисел от 11 до 19
    else:
        last_digit = age % 10  # Последняя цифра числа
        
        if last_digit == 1:
            return age, f'{age} год'  # Если последняя цифра 1
        elif 2 <= last_digit <= 4:
            return age, f'{age} года'  # Если последняя цифра 2, 3, 4
        else:
            return age, f'{age} лет'  # Для всех остальных
        

def get_profile_image(tg_id, url_photo):
    image_data = cache.get(f'photo_{tg_id}')
    if image_data:
        application.logger.debug('cache image exist')
        return image_data
    
    application.logger.info('no cache image')
    try:
        response_img = requests.get(url_photo, auth=(WEBDAV_USERNAME, WEBDAV_PASSWORD), timeout=7)
        if response_img.status_code == 200:
            encoded_image = base64.b64encode(response_img.content).decode('utf-8')
            image_data = f'data:image/png;base64,{encoded_image}'
            cache.set(f'photo_{tg_id}', image_data, timeout=7200)
            return image_data
        else:
            application.logger.info(f"Failed Load image. Status: {response_img.status_code}")
            return ""
    except Exception as e:
        application.logger.info(f"Failed Load image. Get error: {e}")
        return ""

def get_tariff_description(name):
    description = "Покупка тарифа"
    if name == 'СТАРТ':
        description = "💡 <b>Тариф «СТАРТ»</b> — 599₽\n\n"\
                      "✨️ 5 мэтчей\n"\
                      "✨️ 5 прокруток «Сколько в тебе любви»\n"\
                      "✨️ 5 прокруток «Спидометра совместимости»\n"\
                      "✨️ Срок действия: 30 дней\n"\
                      "✨️ Подбор мэтчей в порядке очереди\n"\
                      "✨️ Совместимость по астрологии"
    elif name == 'БАЗОВЫЙ':
        description = "🔮 <b>Тариф «БАЗОВЫЙ»</b> — 999₽\n\n"\
                      "✨️ 10 мэтчей\n"\
                      "✨️ 10 прокруток «Сколько в тебе любви»\n"\
                      "✨️ 10 прокруток «Спидометра совместимости»\n"\
                      "✨️ Срок действия: 30 дней\n"\
                      "✨️ Подбор мэтчей в порядке очереди\n"\
                      "✨️ Совместимость по астрологии"
    elif name == 'VIP':
        description = "💳 <b>Тариф «VIP»</b> — 2 999₽\n\n"\
                      "✨️ Неограниченное количество мэтчей\n"\
                      "✨️ Неограниченное количество прокруток «Сколько в тебе любви»\n"\
                      "✨️ Неограниченное прокруток «Спидометра совместимости»\n"\
                      "✨️ Срок действия: 30 дней\n"\
                      "✨️ Подбор мэтчей вне очереди\n"\
                      "✨️ Совместимость по всем программам"
    elif name == 'SUPER VIP':
        description = "💎 <b>Тариф «SUPER VIP»</b> — 9 999₽\n\n"\
                      "✨️ Неограниченное количество мэтчей\n"\
                      "✨️ Неограниченное количество прокруток «Сколько в тебе любви»\n"\
                      "✨️ Неограниченное количество прокруток «Спидометра совместимости»\n"\
                      "✨️ Срок действия:  1 год\n"\
                      "✨️ Подбор мэтчей вне очереди\n"\
                      "✨️ Совместимость по всем программам"

    return description


def auth_required(view_func):
    @functools.wraps(view_func)
    def wrapped_view(*args, **kwargs):
        # Атомарно получаем все нужные данные из запроса
        cookies = {
            'access_token': request.cookies.get('access_token'),
            'refresh_token': request.cookies.get('refresh_token')
        }
        
        # Если нет refresh токена - сразу редирект
        if not cookies['refresh_token']:
            return redirect(url_for('form'))
        
        # Проверяем access токен
        if cookies['access_token']:
            checked_access, _ = verify_token(cookies['access_token'], 'access')
            if checked_access:
                g.tg_id = checked_access.get('tg_id')
                return view_func(*args, **kwargs)
        
        # Проверяем refresh токен
        checked_refresh, _ = verify_token(cookies['refresh_token'], 'refresh')
        if not checked_refresh:
            return redirect(url_for('form'))
        
        # Создаем новые токены
        g.tg_id = checked_refresh.get('tg_id')
        new_access_token, exp_at = create_token(g.tg_id, token_type='access')
        new_refresh_token, exp_rt = create_token(g.tg_id, token_type='refresh')
        response = view_func(*args, **kwargs)
        
        if isinstance(response, str):
            response = make_response(response)
            
        # Устанавливаем новые токены в куки
        response.set_cookie('access_token', new_access_token, httponly=True, secure=True, expires=exp_at)
        response.set_cookie('refresh_token', new_refresh_token, httponly=True, secure=True, expires=exp_rt)
        dbs.save_refresh_token(g.tg_id, new_refresh_token)
        
        return response
    
    return wrapped_view


@application.route("/")
def start():
    return 'Start Page'


@application.route("/form")
def form():
    init_data = request.args.get('auth')

    if not init_data:
        return render_template('form.html', timestamp=int(time.time()))
    
    check_data = validate_init_data(init_data, BOT_TOKEN)
    check_status = check_data.get("status")
    
    if not check_status:
        return render_template('form.html', timestamp=int(time.time()))
    
    tg_id = check_data.get("id")
    form_data = dbs.check_form(tg_id)
        
    if form_data:
        access_token = request.cookies.get('access_token')
        refresh_token = request.cookies.get('refresh_token')
        
        new_access_token = None
        new_refresh_token = None
        exp_at = None
        exp_rt = None
        
        if refresh_token:
            checked_refresh, refresh_status = verify_token(refresh_token, 'refresh')
            if not checked_refresh:
                # не забыть сделать запись в бд о неудачной проверке, можно удалять анкету
                return render_template('form.html', timestamp=int(time.time()))
        else:
            # либо новый пользователь, либо старый, который заходил очень давно
            # чтобы избежать восстановления, нужно сделать проверку на дату
            new_refresh_token, exp_rt = create_token(tg_id, token_type='refresh')
            dbs.save_refresh_token(tg_id, new_refresh_token)
            
        if access_token:
            checked_access, access_status = verify_token(access_token, 'access')
            application.logger.info(f"access token exist, try check - {access_status}")
            if not checked_access:
                new_access_token, exp_at = create_token(tg_id, token_type='access')
        else:
            new_access_token, exp_at = create_token(tg_id, token_type='access')
            if not new_refresh_token:
                new_refresh_token, exp_rt = create_token(tg_id, token_type='refresh')
        
        response = redirect(url_for('profile'))
        
        if new_access_token:
            application.logger.info(f"{tg_id} update access token")
            response.set_cookie('access_token', new_access_token, httponly=True, secure=True, expires=exp_at)
            
        if new_refresh_token:
            application.logger.info(f"{tg_id} update refresh token")
            dbs.save_refresh_token(tg_id, new_refresh_token)
            response.set_cookie('refresh_token', new_refresh_token, httponly=True, secure=True, expires=exp_rt)
        
        return response

    else:
        return render_template('form.html', timestamp=int(time.time()), check=False)


@application.route('/save_form', methods=['POST'])
def save_form():
    if request.method == 'POST':
        # init_data = request.form.get("init")
        # data = request.form.get("data")
        # file = request.files['file']
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Ошибка получения данных!'}), 400
        
        init_data = data.get('init')
        
        # if not data and file:
        #     return jsonify({'success': False, 'message': 'Ошибка получения данных!'}), 400
        
        check_data = validate_init_data(init_data, BOT_TOKEN)
        check_status = check_data.get("status")
        
        if not check_status:
            return jsonify({'success': False, 'message': 'Проверка данных инициализации завершилась неудачей!'}), 400
        
        tg_id = check_data.get("id")
        username = check_data.get("username")
        
        user = dbs.check_user(tg_id)
        if not user:
            if not username:
                username = '-'
            dbs.add_new_user(tg_id, username)
        
        load_data = data.get('form')
        application.logger.info(f'Сохраняем анкету: telegram id - {tg_id}, username - {username}, анкета:')
        application.logger.info(load_data)
        
        # filename = None
        # folder_name = str(tg_id)
        # create_folder(folder_name)
        
        # if file.filename.lower().endswith('.png'):
        #     filename = 'photo1.png'
        # elif file.filename.lower().endswith('.jpg'):
        #     filename = 'photo1.jpg'
        # elif file.filename.lower().endswith('.jpeg'):
        #     filename = 'photo1.jpeg'
        
        # load_status = load_photo(folder_name, filename, file)
        
        # if not load_status:
        #     return jsonify({'success': False, 'message': 'В процессе загрузки изображения произошла ошибка!'})
        
        dbs.add_form(tg_id, load_data)
        
        profile_details = dbs.check_user_profile_details(tg_id)
        if not profile_details:
            dbs.add_user_details(tg_id, 1) # устанавливаем тариф знакомство
        
        tariff_id = profile_details.get('tariff_id')
        if tariff_id == 6:
            dbs.update_user_tariff(tg_id, 1)
        
        access_token, exp_at = create_token(tg_id, token_type='access')
        refresh_token, exp_rt= create_token(tg_id, token_type='refresh')
        dbs.save_refresh_token(tg_id, refresh_token)
        
        response = jsonify({'success': True, 'message': 'Анкета успешно сохранена!'})
        response.set_cookie('access_token', access_token, httponly=True, secure=True, expires=exp_at)
        response.set_cookie('refresh_token', refresh_token, httponly=True, secure=True, expires=exp_rt)
        return response, 200


@application.route('/delete_form')
@auth_required
def delete_form():
    tg_id = g.tg_id
    
    dbs.delete_match_status(tg_id)
    dbs.delete_form(tg_id)
    dbs.delete_refresh_token(tg_id)
    
    folder_name = str(tg_id)
    delete_folder(folder_name)
    
    response = jsonify({'success': True, 'message': 'Анкета успешно удалена!'})
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    cache.clear()
    
    return response


@application.route("/profile")
@auth_required
def profile():
    tg_id = g.tg_id

    form_data = dbs.check_form(tg_id)
    
    if not form_data:
        response = redirect(url_for('form'))
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response
    
    birth_dt = form_data.get('birth_dt')
    digit_age, your_age = get_age(birth_dt)
    location = form_data.get('location').split(' (')[0];
    form_data['location'] = location
    
    sign = form_data.get('sign')
    sign_path = get_sign_path(sign)
        
    details = dbs.check_user_profile_details(tg_id)
    if not details:
        dbs.add_user_details(tg_id, 1)
        details = dbs.check_user_profile_details(tg_id)
    
    amount_matches = details.get('amount_matches')
    tariff_id = details.get('tariff_id')
    tariff = dbs.check_tariff(tariff_id)
    tariff_name = tariff.get('name')
    
    image_data = None
    filename = form_data.get('photo_link')
    if filename != 'Нет фото':
        url_photo = f"{WEBDAV_URL}/{tg_id}/{filename}"
        image_data = get_profile_image(tg_id, url_photo)
    
    return render_template('profile.html', form=form_data, sign_path=sign_path, age=your_age, tariff=tariff_name, amount_matches=amount_matches, image=image_data)


@application.route("/about_me")
@auth_required
def about_me():
    tg_id = g.tg_id
    form_data = dbs.check_form(tg_id)
    
    gives = form_data.get('gives').split(", ")
    my_appearance = form_data.get('my_appearance').split(", ")
    my_character = form_data.get('my_character').split(", ")
    
    gets = form_data.get('gets').split(", ")
    partner_appearance = form_data.get('partner_appearance').split(", ")
    partner_character = form_data.get('partner_character').split(", ")
    interests = form_data.get('interests').split(", ")
    
    headers = ['height', 'physique', 'hair_color', 'hair_type', 'eye_color', 'skin_color', 'face_type', 'tattoos']
    my_app_dict = None
    if len(my_appearance) == 8:
        my_app_dict = dict(zip(headers, my_appearance))
    part_app_dict = None
    if len(partner_appearance) == 8:
        part_app_dict = dict(zip(headers, partner_appearance))
        
    return render_template('about_me.html', form=form_data, gives=gives, my_appearance=my_app_dict, my_character=my_character, gets=gets, partner_appearance=part_app_dict, partner_character=partner_character, interests=interests)



@application.route("/tariffs")
@auth_required
def tariffs():
    return render_template('tariffs.html')


@application.route('/buy', methods=['POST'])
def buy():
    if request.method == 'POST':
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': 'Ошибка получения данных!'}), 400
        
        init_data = data.get('init')
        
        check_data = validate_init_data(init_data, BOT_TOKEN)
        check_status = check_data.get("status")
        
        if not check_status:
            return jsonify({'success': False, 'message': 'Проверка данных завершилась неудачей!'}), 400
        
        tg_id = check_data.get("id")
        username = check_data.get("username")
        application.logger.info(f'{tg_id} - {username}')
        
        tariff_name = data.get('tariff')
        price = data.get('price')
        payload = data.get('payload')
        promocode = data.get('promocode')
        
        discount = False
        referral = dbs.check_promocode(promocode)
        current_user_promo = dbs.check_ref(tg_id)

        if referral:
            ref_tg_id = referral.get('tg_id')
            discount_percent = referral.get('discount_percent')
            if tg_id != ref_tg_id:
                discount = True
                payload = payload + "_" + promocode
                application.logger.info(f'{payload}')
        message = get_tariff_description(tariff_name)
        message_data = {
            'chat_id': tg_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        response = requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage', data=message_data)
        
        if discount:
            price = round(price - price * (discount_percent / 100))
            # dbs.add_new_promo_apply(tg_id, ref_tg_id)
            message = f'Промокод успешно применён! ✅\n\nВаша скидка по промокоду на покупку тарифа составляет — {discount_percent}%'
            message_discount = {
                'chat_id': tg_id,
                'text': message
            }
            response = requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage', data=message_discount)
        
        date_invoice = f'{dt.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}'
        
        invoice_data = {
            'chat_id': tg_id,
            'title': f'Покупка тарифа {tariff_name}',
            'description': f'Создано ------ {date_invoice} ------ Счёт на оплату сформирован. Оплата осуществляется через Telegram.',
            'payload': payload,
            'provider_token': PAYMENT_TOKEN,
            'currency': 'RUB',
            'prices': [{'label': 'Стоимость выбранного тарифа', 'amount': price * 100}],  # price в копейках
        }
        response = requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendInvoice', json=invoice_data)
    
        if response.status_code != 200:
            return jsonify({'success': False, 'message': response.text}), response.status_code
            
        return jsonify({'success': True , 'message': 'Сообщение успешно отправлено в бот'}), 200


@application.route("/change_form")
def change_form():
    return render_template('change_form.html')


@application.route("/match")
@auth_required
def match():
    tg_id = g.tg_id
    form_data = dbs.check_form(tg_id)
    matches = dbs.match_list(tg_id)

    for match in matches:
        partner_sign = match.get('partner_sign')
        partner_sign_path = get_match_sign_path(partner_sign)
        match['partner_sign_path'] = partner_sign_path
    
    return render_template('match.html', matches=matches)
  
  
@application.route("/match/<int:select_id>")
@auth_required
def show_match(select_id):
    tg_id = g.tg_id
    matches = dbs.match_list(tg_id)
    
    selected_match = next(filter(lambda match: match.get('tg_id') == select_id, matches), None)
    
    if not selected_match:
        abort(404)
    
    match_status = dbs.check_match_status(tg_id, select_id)
    
    if not match_status or match_status not in ('просмотрено', 'ожидание ответа', 'мэтч', 'нет мэтча'):
        status = "просмотрено"
        dbs.update_match_status(tg_id, select_id, status)
        match_status = status
    selected_match['status'] = match_status
    
    partner_sign = selected_match.get('partner_sign')
    relation_type = selected_match.get('relation_type')
    result_compatibility = selected_match.get('result_compatibility')
    partner_sign_path = get_match_sign_path(partner_sign)
    partner_sign_description = get_sign_description(partner_sign)
    relation_type_description = get_type_description(relation_type)
    compatibility_description = get_compatibility_description(result_compatibility)
    
    selected_match['partner_sign_path'] = partner_sign_path
    selected_match['partner_sign_description'] = partner_sign_description
    selected_match['relation_type_description'] = relation_type_description
    selected_match['compatibility_description'] = compatibility_description
    
    
    partner_gives = selected_match.get('partner_gives').split(", ")
    partner_character = selected_match.get('partner_character').split(", ")
    part_headers = ['height', 'physique', 'hair_color', 'hair_type', 'eye_color', 'skin_color', 'face_type', 'tattoos']
    part_appearance = selected_match.get('partner_appearance').split(", ")
    partner_appearance = dict(zip(part_headers, part_appearance))
    partner_interests = selected_match.get('partner_interests').split(", ")
    
    return render_template('match_open.html', selected_match=selected_match, partner_gives=partner_gives, partner_character=partner_character, partner_appearance=partner_appearance, partner_interests=partner_interests)


@application.route("/deny/<int:select_id>", methods=['POST'])
@auth_required
def deny_match(select_id):
    tg_id = g.tg_id
    
    user_details = dbs.check_user_profile_details(tg_id) 
    tariff_id = user_details.get('tariff_id')
    amount_matches = user_details.get('amount_matches')
    
    if amount_matches == 0 and tariff_id in (1, 2, 3):
        return jsonify({"status": False , "message": "На вашем балансе недостаточно мэтчей для проведения операции"})
        
    status = "нет мэтча"
    dbs.update_match_status(tg_id, select_id, status)
    dbs.update_match_status(select_id, tg_id, status)
    
    return jsonify({"status": True , "message": "Данный мэтч был успешно отклонён"})


@application.route("/agree/<int:select_id>", methods=['POST'])
@auth_required
def agree_match(select_id):
    tg_id = g.tg_id
    
    match_status = dbs.check_match_status(tg_id, select_id)
    partner_match_status = dbs.check_match_status(select_id, tg_id)
    
    user_details = dbs.check_user_profile_details(tg_id)
    partner_details = dbs.check_user_profile_details(select_id) 
    
    tariff_id = user_details.get('tariff_id')
    partner_tariff_id = partner_details.get('tariff_id')
    
    amount_matches = user_details.get('amount_matches')
    partner_amount_matches = partner_details.get('amount_matches')
    
    if amount_matches == 0 and tariff_id in (1, 2, 3):
        return jsonify({"status": False , "message": "На вашем балансе недостаточно мэтчей для проведения операции"})
    
    
    if match_status in (None, 'просмотрено') and partner_match_status in (None, 'просмотрено'):
        # Устанавливаем статус "ожидание ответа" для текущего пользователя
        dbs.update_match_status(tg_id, select_id, "ожидание ответа")
        
        keyboard = {
            "inline_keyboard": [
                [
                    {
                        "text": "Посмотреть",
                        "web_app": {
                            "url": f'https://astro-love.online/match/{tg_id}'
                        }
                    }
                ]
            ]
        }
        
        # Отправляем уведомление второму пользователю
        message = "Вам пришёл мэтч!✨️\nКто-то проявил к вам интерес!"
        message_data = {
            'chat_id': select_id,
            'text': message,
            'reply_markup': json.dumps(keyboard)
        }
        requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage', data=message_data)
        
        return jsonify({"status": True , "message": "Ожидаем ответа от пользователя"})
    
    # Если второй пользователь уже ожидает нашего ответа
    elif partner_match_status == "ожидание ответа":
        # Устанавливаем мэтч для обоих пользователей
        if partner_amount_matches == 0 and partner_tariff_id in (1, 2, 3):
            keyboard = {
                "inline_keyboard": [
                    [
                        {
                            "text": "Купить тариф",
                            "web_app": {
                                "url": f'https://astro-love.online/tariffs'
                            }
                        }
                    ]
                ]
            }
            
            message = "У вас взаимный мэтч!✨️\nПополните свой баланс!"
            message_data = {
                'chat_id': select_id,
                'text': message,
                'reply_markup': json.dumps(keyboard)
            }
            requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage', data=message_data)
            
            return jsonify({"status": False , "message": "На балансе предполагаемого партнёра недостаточно мэтчей для проведения операции"})
    
        if tariff_id in (1, 2, 3):
            dbs.update_amount_matches(tg_id, 1)
        if partner_tariff_id in (1, 2, 3):
            dbs.update_amount_matches(select_id, 1)
        
        dbs.update_match_status(tg_id, select_id, "мэтч")
        dbs.update_match_status(select_id, tg_id, "мэтч")
    
        # Отправляем уведомления обоим пользователям
        success_message = "У вас случился взаимный мэтч! 🎉\nТеперь вы можете общаться!"
        
        # Пары user_id и соответствующих профилей для кнопок
        users_id = {
            tg_id: select_id,
            select_id: tg_id
        }
        
        for user_id, profile_id in users_id.items():
            message_data = {
                'chat_id': user_id,
                'text': success_message,
                'reply_markup': json.dumps({
                    "inline_keyboard": [[{
                        "text": "Открыть профиль",
                        "url": f"tg://user?id={profile_id}"
                    }]]
                })
            }
            requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage', data=message_data)
        
        return jsonify({"status": True, "message": "Поздравляем! У вас произошел взаимный мэтч!"})
            
    # Если мэтч уже существует
    elif match_status == "мэтч" or partner_match_status == "мэтч":
        dbs.update_match_status(tg_id, select_id, "мэтч")
        dbs.update_match_status(select_id, tg_id, "мэтч")
        return jsonify({"status": "already_matched", "message": "Мэтч уже существует"})
    
    # Если текущий пользователь уже ожидает ответа
    elif match_status == "ожидание ответа":
        return jsonify({"status": False, "message": "Вы уже ожидаете ответа от этого пользователя"})
    
    return jsonify({"status": False , "message": "Произошла ошибка! Перезагрузите страницу и попробуйте снова"})
        
 
@application.route("/speed")
def speed():
    return render_template('speedometr.html')


@application.route("/love")
def love():
    return render_template('love_in_me.html')    


@application.route("/test")
def test_mode():
    return render_template('love_test.html')


@application.route("/test_form")
def test_form():
    return render_template('test.html')   

# @application.route("/save", methods=['POST'])
# @cache.cached(timeout=10, unless=True)
# def save():
#     if request.method == 'POST':
#         # dict_data = request.get_json()
#         file = request.files['file']
#         data = request.form.get('data')

#         if file and data:
#             data_dict = json.loads(str(data))
#             try:
#                 filename = f'photo_{data_dict.get("tg_id")}.png'  # filename = file.filename
#                 dbs.add_form(filename, data_dict)
#                 file.save(UPLOAD_FOLDER + filename)
#                 return jsonify({'msg': 'OK'}), 200
#             except Exception as e:
#                 return jsonify({'error': e}), 404

if __name__ == "__main__":
    application.run(host='0.0.0.0', debug=True, threaded=True)
