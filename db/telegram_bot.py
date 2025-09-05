import os, sys

activate_this = '/home/a1123675/venv/bin/activate_this.py'
with open(activate_this) as f:
     exec(f.read(), {'__file__': activate_this})


from aiogram.types import Message, FSInputFile, InputMediaPhoto, InputMediaVideo, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, PreCheckoutQuery, LabeledPrice, WebAppInfo
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums.parse_mode import ParseMode
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from async_controller import db
from dotenv import load_dotenv
from tabulate import tabulate
import datetime as dt
import asyncio
import logging
import random
import re


load_dotenv()  # Загружаем переменные окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
PAYMENT_TOKEN = os.getenv('PAYMENT_TOKEN')
IMG_DIR = "/home/a1123675/domains/astro-love.online/static/img/"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Хранилище для альбомов (медиа-групп)
album_storage = {}  # {media_group_id: {"media": [], "caption": str, "timer": asyncio.Task}}

# Хранилище для отправленных сообщений
sent_messages = {} # Формат: {user_id: [{"message_id": int, "type": "text"|"media"}, ...]}

class SendMedia(StatesGroup):
    waiting_media = State()
    confirm = State()

class EditState(StatesGroup):
    waiting_new_text = State()


def length_control(table, max_length):
    if (len(table) > max_length):
        start_pos = 0
        table_list = []

        while (len(table[start_pos:]) > max_length):
            end_pos = start_pos + [m.end() for m in re.finditer(r':\d{2}\n',table[start_pos:start_pos+max_length])][-1]
            table_list.append(table[start_pos:end_pos])
            start_pos = end_pos

        if (len(table[start_pos:]) <= max_length):
            table_list.append(table[start_pos:])
        
        return table_list
    else:
        return [table]


@dp.message(Command(commands="start"))
async def command_start(message: Message):
    tg_id =  message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    logging.info(f'{tg_id} - {username}')
    photo = FSInputFile(IMG_DIR +"header.jpg")
    
    text = f'<b>{first_name},\nдобро пожаловать в ASTRO-LOVE❤️‍🔥</b>\n'\
            'где звезды сводят сердца!\n\n'\
            'Твоя идеальная пара уже где-то рядом ✨\n'\
            'Осталось только зарегистрироваться в нашем приложении!\n\n'\
    
    menu_btns = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎟️ ПРОМОКОД 🎟️")],
            [KeyboardButton(text="💎 ТАРИФЫ 💎"), KeyboardButton(text="🐷 КОПИЛКА 🐽")],
            [KeyboardButton(text="📚 ИНСТРУКЦИИ 📚"), KeyboardButton(text="⚒️ ТЕХНИЧЕСКИЕ ПРОБЛЕМЫ ⚒️")],
            [KeyboardButton(text="📲 ОБРАТНАЯ СВЯЗЬ")],
            [KeyboardButton(text="⭐️ ПАРТНЁРСКАЯ ПРОГРАММА ⭐️")]
        ], 
        resize_keyboard=True
    )
            
    await bot.send_photo(chat_id=message.chat.id, photo=photo, caption=text, reply_markup=menu_btns, parse_mode=ParseMode.HTML)
    

    text = '<b>Жми кнопку «СТАРТ»,\nчтобы помочь Вселенной найти для тебя лучшего соулмейта 💫</b>'
    
    start_btn = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="СТАРТ", web_app=WebAppInfo(url='https://astro-love.online/form'))]])
    # tg://miniapp?app_id=Astro_Love_bot
    await message.answer(text, reply_markup=start_btn, parse_mode=ParseMode.HTML)
    
    if not username:
        username = '-'
    # Получаем информацию о пользователе из базы данных
    user = await db.check_user(tg_id)
    if user:
        saved_username = user.get('username')
        if username != saved_username:
            await db.update_user_info(tg_id, username)
    else:
        await db.add_new_user(tg_id, username)
    
    profile_details = await db.check_profile_details(tg_id)
    if not profile_details:
        await db.add_new_profile_details(tg_id)


@dp.message(Command(commands="test"))
async def command_start(message: Message):
    tg_id =  message.from_user.id
    admin = await db.check_admin(tg_id)
    if (admin):
        text = '<b>Модуль для тестирования страниц приложения</b>\n\nИспользуется режим изоляции, доступ предоставляется только по ссылке для администраторов и тестировщиков системы. Не предназначено для общего использования\n\n<b>Текущий шаблон:</b> love_test.html'
    
        open_btn = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Открыть страницу через Telegram App", web_app=WebAppInfo(url='https://astro-love.online/test'))]])
        
        text_form = '<b>Модуль для тестирования страниц приложения</b>\n\nДля личной информации в профиле\n\n<b>Шаблон:</b> about_me.html'
        form_btn = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Открыть страницу через Telegram App", web_app=WebAppInfo(url='https://astro-love.online/about_me'))]])
       
        # tg://miniapp?app_id=Astro_Love_bot
        await message.answer(text, reply_markup=open_btn, parse_mode=ParseMode.HTML)
        await message.answer(text_form, reply_markup=form_btn, parse_mode=ParseMode.HTML)


@dp.message(Command(commands="menu"))
async def command_open_menu(message: Message):
    menu_btns = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎟️ ПРОМОКОД 🎟️")],
            [KeyboardButton(text="💎 ТАРИФЫ 💎"), KeyboardButton(text="🐷 КОПИЛКА 🐽")],
            [KeyboardButton(text="📚 ИНСТРУКЦИИ 📚"), KeyboardButton(text="⚒️ ТЕХНИЧЕСКИЕ ПРОБЛЕМЫ ⚒️")],
            [KeyboardButton(text="📲 ОБРАТНАЯ СВЯЗЬ")],
            [KeyboardButton(text="⭐️ ПАРТНЁРСКАЯ ПРОГРАММА ⭐️")]
        ], 
        resize_keyboard=True
    )
    
    await message.answer("💟 <b>Системное уведомление</b> 💟\nВыберите пункт меню", reply_markup=menu_btns, parse_mode=ParseMode.HTML)

@dp.message(F.text.in_(["🎟️ ПРОМОКОД 🎟️", "💎 ТАРИФЫ 💎", "🐷 КОПИЛКА 🐽", "📚 ИНСТРУКЦИИ 📚", "⚒️ ТЕХНИЧЕСКИЕ ПРОБЛЕМЫ ⚒️", "📲 ОБРАТНАЯ СВЯЗЬ", "⭐️ ПАРТНЁРСКАЯ ПРОГРАММА ⭐️", "⚜️ НАШИ ПАРТНЁРЫ ⚜️", "🔱 СТАТЬ НАШИМ ПАРТНЁРОМ 🔱"]))
async def menu_handler(message: Message):
    tg_id = message.from_user.id
    username = message.from_user.username
    
    if message.text == "🎟️ ПРОМОКОД 🎟️":
        photo = FSInputFile(IMG_DIR +"bot_menu/promocode.jpg")
        text = "Промокод в АСТРО-ЛЮБОВЬ — твой ключ к выгоде и заработку!💰❤️‍🔥\n\n"\
               "Что дает?\n"\
               "✨Делись своим персональным промокодом с друзьями и знакомыми! — они получают скидку\n"\
               "🪐 Зарабатывай деньги! — приглашай друзей и получай вознаграждение за их покупки\n"\
               "🔮 Вывод средств —  осуществляется от 1000₽ без комиссий\n\n"\
               "Для пользователей:\n"\
               "❗️Ваш личный промокод дает <b>5% скидки</b> Вашему другу и(или) знакомому при оплате любого тарифа\n"\
               "❗️Вы <b>зарабатываете 5%</b> от покупки вашим другом и(или) знакомым любого тарифа\n"\
               "❓Если вы хотите больший % - становитесь нашим «партнером»"
        await bot.send_photo(chat_id=message.chat.id, photo=photo, caption=text, parse_mode=ParseMode.HTML)
        
        if not username:
            username = "User"
        referral = await db.check_ref(tg_id)
        if referral:
            promocode = referral.get('promocode')
            await message.answer(f'Ваш персональный промокод: <code>{promocode}</code>', parse_mode=ParseMode.HTML)
        else:
            number = random.randint(10, 10000)
            promocode = f'AL{username}{number}'.upper()
            await db.add_new_ref(tg_id, promocode)
            await message.answer(f'Ваш персональный промокод был успешно сгенерирован!\nПромокод: <code>{promocode}</code>', parse_mode=ParseMode.HTML)
    
    elif message.text == "💎 ТАРИФЫ 💎":
        photo = FSInputFile(IMG_DIR +"bot_menu/tariff.jpg")
        text = "<b>🔮 Выберите подходящий тариф</b>\n\n"\
               "Хотите увеличить шансы найти свою идеальную пару? Выберите любой тариф из представленных ниже вариантов!\n\n"\
               "<i>💡 Чем выше тариф — тем больше возможностей для знакомства!</i>"
        
        await bot.send_photo(chat_id=message.chat.id, photo=photo, caption=text, parse_mode=ParseMode.HTML)
        
        tariff_btns = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="💡 Тариф «СТАРТ»")], 
                [KeyboardButton(text="🔮 Тариф «БАЗОВЫЙ»")],
                [KeyboardButton(text="💳 Тариф «VIP»")], 
                [KeyboardButton(text="💎 Тариф «SUPER VIP»")],
                [KeyboardButton(text="Назад ⏪")]
            ], 
            resize_keyboard=True
        )
        await message.answer("💟 <b>Системное уведомление</b> 💟\nВыберите тариф", reply_markup=tariff_btns, parse_mode=ParseMode.HTML)
    
    elif message.text ==  "🐷 КОПИЛКА 🐽":
        photo = FSInputFile(IMG_DIR +"bot_menu/wallet.jpg")
        text = "Копилка в АСТРО-ЛЮБОВЬ — твой звёздный финансовый помощник!❤️‍🔥🐷\n\n"\
               "В данном разделе отражен твой баланс!\n"\
               "Следующим сообщением⬇️\n\n"\
               "Как можно использовать баланс?\n"\
               "🌟 Выводить напрямую на свой счет от 1000₽ — просто пиши @heroineVM\n"\
               "💎Оплачивать свой тариф — прям внутри приложения\n"\
               "💡Использовать внутри приложения — скоро расскажем!\n"
        await bot.send_photo(chat_id=message.chat.id, photo=photo, caption=text, parse_mode=ParseMode.HTML)
    
        referral = await db.check_ref(tg_id)
        if referral:
            earned_money = referral.get('earned_money')
            await message.answer(f'<b>🐷 КОПИЛКА 🐽</b>\n\nБаланс: {earned_money} рублей', parse_mode=ParseMode.HTML)
        else:
            await message.answer(f'Для того чтобы у Вас появилась копилка необходимо сгенерировать свой персональный промокод.\nДля его создания воспользуйтесь разделом <b>🎟️ ПРОМОКОД 🎟</b>', parse_mode=ParseMode.HTML)
    
    elif message.text == "📚 ИНСТРУКЦИИ 📚":
        photo = FSInputFile(IMG_DIR +"bot_menu/instructions.jpg")
        help_btns = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="✍️ Создание анкеты")],
                [KeyboardButton(text="🎟️ Генерация промокода")],
                [KeyboardButton(text="🐽 Копилка"), KeyboardButton(text="💎 Тарифы и оплата")],
                [KeyboardButton(text="♻️ Восстановление доступа")],
                [KeyboardButton(text="Назад ⏪")]
            ],
            resize_keyboard=True
        )
        
        await bot.send_photo(chat_id=message.chat.id, photo=photo, caption="💟 <b>Системное уведомление</b> 💟\nВыберите раздел", reply_markup=help_btns, parse_mode=ParseMode.HTML)
    
    elif message.text == "⚒️ ТЕХНИЧЕСКИЕ ПРОБЛЕМЫ ⚒️":
        photo = FSInputFile(IMG_DIR +"bot_menu/tech_problems.jpg")
        
        cache_clear_btns = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📱 Очистка кэша - ANDROID")],
                [KeyboardButton(text="📱 Очистка кэша - IOS")],
                [KeyboardButton(text="Назад ⏪")]
            ], 
            resize_keyboard=True
        )
        
        await bot.send_photo(chat_id=message.chat.id, photo=photo, caption="Если у Вас возникла проблема при работе с Telegram-ботом или приложением и Вы не смогли найти решение в представленных инструкциях, пожалуйста, сообщите нам об этом!\n\nВ данном разделе рассмотрены возможные способы решения распространённых проблем, которые возникают при взаимодействии с Telegram-ботом и приложением.", parse_mode=ParseMode.HTML)
        await message.answer("💟 <b>Системное уведомление</b> 💟\nВыберите категорию", reply_markup=cache_clear_btns, parse_mode=ParseMode.HTML)
    
    elif message.text == "📲 ОБРАТНАЯ СВЯЗЬ":
        first_name = message.from_user.first_name
        photo = FSInputFile(IMG_DIR +"bot_menu/feedback.jpg")
        text = f"Здравствуйте, {first_name}! 🌟\n\n"\
                "Спасибо, что проявили интерес — приятно познакомиться! Все ли понравилось или есть моменты, которые можно улучшить?\n\n"\
                "Ваше мнение очень важно для нас — поможете сделать «АСТРО-ЛЮБОВЬ❤️‍🔥» еще лучше? 💫\n\n"\
                "Мы можем обсудить это лично или просто оставьте короткий отзыв здесь.\n"\
                "Будем рады услышать любые мысли!\n\n"\
                "С уважением,\n"\
                "Команда АСТРО-ЛЮБОВЬ❤️‍🔥"
            
        msg_btns = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📩 Написать сообщение", callback_data="leave_msg")],
                [InlineKeyboardButton(text="📲 Связаться напрямую", url="tg://resolve?domain=heroineVM")]
            ],
            resize_keyboard=True
        )
        await bot.send_photo(chat_id=message.chat.id, photo=photo, caption=text, reply_markup=msg_btns, parse_mode=ParseMode.HTML)
    
    elif message.text == "⭐️ ПАРТНЁРСКАЯ ПРОГРАММА ⭐️":
        photo = FSInputFile(IMG_DIR +"bot_menu/partners.jpg")
        part_btns = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="⚜️ НАШИ ПАРТНЁРЫ ⚜️")],
                [KeyboardButton(text="🥇 СПИСОК НАШИХ ПАРТНЕРОВ 🥇")],
                [KeyboardButton(text="🔱 СТАТЬ НАШИМ ПАРТНЁРОМ 🔱")],
                [KeyboardButton(text="Назад ⏪")]
            ],
            resize_keyboard=True
        )
        await bot.send_photo(chat_id=message.chat.id, photo=photo, caption="💟 <b>Системное уведомление</b> 💟\nВыберите категорию", reply_markup=part_btns, parse_mode=ParseMode.HTML)
    
    elif message.text == "⚜️ НАШИ ПАРТНЁРЫ ⚜️":
        text = "<b>⚜️ НАШИ ПАРТНЁРЫ ⚜️</b>\n\n"\
               "Наши партнёры — друзья, которые делают ASTRO-LOVE❤️‍🔥 ярче!\n\n"\
               "Вместе мы создаём магию любви и доверия💫\n"\
               "Благодаря нашим партнёрам тысячи людей найдут свою гармонию!\n\n"\
               "Пользователи, которые купили любой платный тариф «АСТРО-ЛЮБОВЬ»❤️‍🔥,\n"\
               "имеют доступ к привилегиями от наших партнеров🙌🏻\n"\
               "О том, как стать нашим партнером смотри в другом разделе меню:\n<b>🔱 СТАТЬ НАШИМ ПАРТНЁРОМ 🔱</b>"
        await message.answer(text, parse_mode=ParseMode.HTML)
    
    elif message.text == "🔱 СТАТЬ НАШИМ ПАРТНЁРОМ 🔱":
        text = "<b>🔱 СТАТЬ НАШИМ ПАРТНЁРОМ 🔱</b>\n\n"\
               "Стань партнёром в «АСТРО-ЛЮБОВЬ❤️‍🔥» — зарабатывай на любви и звёздах! 🌟💘\n\n"\
               "Хочешь получать доход, помогая людям находить любовь через астрологию? Присоединяйся к нашей партнёрской программе!\n\n"\
               "<b>Кому подходит? Кем нужно быть?</b>\n"\
               "📲 Медийной личностью, блогером, лидером мнений\n"\
               "🎤 Специалистом в своей сфере , которая может Быть интересна нашим пользователям (ведущий свадеб, фотограф и т.д.)\n"\
               "💒 Предпринимателем, владельцам бизнеса\n"\
               "(цветочные, кофейни, рестораны и т.д.)\n\n"\
               "<b>Почему это выгодно?</b>\n"\
               "🔥 Высокие проценты – твой доход растёт, обговариваем лично\n"\
               "✨ Готовые материалы – баннеры, посты, тексты для рекламы.\n"\
               "💬 Поддержка 24/7– помогаем на всех этапах\n"\
               "💯 Выплачиваем деньгами , а не баллами!\n\n"\
               "<b>Как это работает?</b>\n"\
               "1️⃣ Оставляешь заявку→ @heroineVM\n"\
               "2️⃣ Получаешь ссылку/промокод→ размещаешь в своих соц.сетях и(или) предприятии\n"\
               "3️⃣ Привлекаешь клиентов→ через соцсети, блог, знакомых.\n"\
               "4️⃣ Зарабатываешь→ с каждой продажи или лида!\n\n\n"\
               "Крути колесо фортуны в свою пользу — начни прямо сейчас!💫🚀"
            
        msg_btn = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📩 Пиши", url="tg://resolve?domain=heroineVM")]])
        await message.answer(text, reply_markup=msg_btn, parse_mode=ParseMode.HTML)


@dp.message(F.text.in_(["💡 Тариф «СТАРТ»", "🔮 Тариф «БАЗОВЫЙ»", "💳 Тариф «VIP»", "💎 Тариф «SUPER VIP»"]))
async def tariff_handler(message: Message):
    if message.text == "💡 Тариф «СТАРТ»":
        description = "💡 <b>Тариф «СТАРТ»</b> — 599₽\n\n"\
                      "✨️ 5 мэтчей\n"\
                      "✨️ 5 прокруток «Сколько в тебе любви»\n"\
                      "✨️ 5 прокруток «Спидометра совместимости»\n"\
                      "✨️ Срок действия: 30 дней\n"\
                      "✨️ Подбор мэтчей в порядке очереди\n"\
                      "✨️ Совместимость по астрологии"
        buy_btn = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Купить сейчас", callback_data="buy_now_start")]])
    
    elif message.text == "🔮 Тариф «БАЗОВЫЙ»":
        description = "🔮 <b>Тариф «БАЗОВЫЙ»</b> — 999₽\n\n"\
                      "✨️ 10 мэтчей\n"\
                      "✨️ 10 прокруток «Сколько в тебе любви»\n"\
                      "✨️ 10 прокруток «Спидометра совместимости»\n"\
                      "✨️ Срок действия: 30 дней\n"\
                      "✨️ Подбор мэтчей в порядке очереди\n"\
                      "✨️ Совместимость по астрологии"
        buy_btn = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Купить сейчас", callback_data="buy_now_base")]])
        
    elif message.text == "💳 Тариф «VIP»":
        description = "💳 <b>Тариф «VIP»</b> — 2 999₽\n\n"\
                      "✨️ Неограниченное количество мэтчей\n"\
                      "✨️ Неограниченное количество прокруток «Сколько в тебе любви»\n"\
                      "✨️ Неограниченное прокруток «Спидометра совместимости»\n"\
                      "✨️ Срок действия: 30 дней\n"\
                      "✨️ Подбор мэтчей вне очереди\n"\
                      "✨️ Совместимость по всем программам"
        buy_btn = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Купить сейчас", callback_data="buy_now_vip")]])
    
    elif message.text == "💎 Тариф «SUPER VIP»":
        description = "💎 <b>Тариф «SUPER VIP»</b> — 9 999₽\n\n"\
                      "✨️ Неограниченное количество мэтчей\n"\
                      "✨️ Неограниченное количество прокруток «Сколько в тебе любви»\n"\
                      "✨️ Неограниченное прокруток «Спидометра совместимости»\n"\
                      "✨️ Срок действия:  1 год\n"\
                      "✨️ Подбор мэтчей вне очереди\n"\
                      "✨️ Совместимость по всем программам"
        buy_btn = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Купить сейчас", callback_data="buy_now_supervip")]])
    
    await message.answer(text=description, reply_markup=buy_btn, parse_mode=ParseMode.HTML)


@dp.message(F.text.in_(["✍️ Создание анкеты", "🎟️ Генерация промокода", "🐽 Копилка", "💎 Тарифы и оплата", "Назад ⏪", "📱 Очистка кэша - ANDROID", "📱 Очистка кэша - IOS"]))
async def help_handler(message: Message):
    if message.text == "✍️ Создание анкеты":
        main_photo = FSInputFile(IMG_DIR +"instructions/create_form/create.png")
        
        step_1 = FSInputFile(IMG_DIR +"instructions/create_form/Шаг_1.png")
        step_2 = FSInputFile(IMG_DIR +"instructions/create_form/Шаг_2.png")
        step_3 = FSInputFile(IMG_DIR +"instructions/create_form/Шаг_3.png")
        step_4 = FSInputFile(IMG_DIR +"instructions/create_form/Шаг_4.png")
        step_5 = FSInputFile(IMG_DIR +"instructions/create_form/Шаг_5.png")
        step_6 = FSInputFile(IMG_DIR +"instructions/create_form/Шаг_6.png")
        
        media = [
            InputMediaPhoto(media=step_1),
            InputMediaPhoto(media=step_2),
            InputMediaPhoto(media=step_3),
            InputMediaPhoto(media=step_4),
            InputMediaPhoto(media=step_5),
            InputMediaPhoto(media=step_6)
        ]
        
        await bot.send_photo(chat_id=message.chat.id, photo=main_photo, parse_mode=ParseMode.HTML)
        await bot.send_media_group(chat_id=message.chat.id, media=media)
    
    elif message.text == "🎟️ Генерация промокода":
        main_photo = FSInputFile(IMG_DIR +"instructions/generate_promo/gen_promo.png")
        
        step_1 = FSInputFile(IMG_DIR +"instructions/generate_promo/Шаг_1.png")
        step_2 = FSInputFile(IMG_DIR +"instructions/generate_promo/Шаг_2.png")
        
        media = [InputMediaPhoto(media=step_1), InputMediaPhoto(media=step_2)]
        
        await bot.send_photo(chat_id=message.chat.id, photo=main_photo, parse_mode=ParseMode.HTML)
        await bot.send_media_group(chat_id=message.chat.id, media=media)
    
    elif message.text == "🐽 Копилка":
        main_photo = FSInputFile(IMG_DIR +"instructions/wallet/wallet.png")
        
        step_1 = FSInputFile(IMG_DIR +"instructions/wallet/Шаг_1.png")
        step_2 = FSInputFile(IMG_DIR +"instructions/wallet/Шаг_2.png")
        
        media = [InputMediaPhoto(media=step_1), InputMediaPhoto(media=step_2)]
        
        await bot.send_photo(chat_id=message.chat.id, photo=main_photo, parse_mode=ParseMode.HTML)
        await bot.send_media_group(chat_id=message.chat.id, media=media)
    
    elif message.text == "💎 Тарифы и оплата":
        main_photo = FSInputFile(IMG_DIR +"instructions/payment/payment.png")
        
        step_1 = FSInputFile(IMG_DIR +"instructions/payment/Шаг_1.png")
        step_2 = FSInputFile(IMG_DIR +"instructions/payment/Шаг_2.png")
        step_3 = FSInputFile(IMG_DIR +"instructions/payment/Шаг_3.png")
        step_4 = FSInputFile(IMG_DIR +"instructions/payment/Шаг_4.png")
        step_5 = FSInputFile(IMG_DIR +"instructions/payment/Шаг_5.png")
        
        media = [
            InputMediaPhoto(media=step_1),
            InputMediaPhoto(media=step_2),
            InputMediaPhoto(media=step_3),
            InputMediaPhoto(media=step_4),
            InputMediaPhoto(media=step_5)
        ]
        
        await bot.send_photo(chat_id=message.chat.id, photo=main_photo, parse_mode=ParseMode.HTML)
        await bot.send_media_group(chat_id=message.chat.id, media=media)
    
    elif message.text == "Назад ⏪":
        menu_btns = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🎟️ ПРОМОКОД 🎟️")],
                [KeyboardButton(text="💎 ТАРИФЫ 💎"), KeyboardButton(text="🐷 КОПИЛКА 🐽")],
                [KeyboardButton(text="📚 ИНСТРУКЦИИ 📚"), KeyboardButton(text="⚒️ ТЕХНИЧЕСКИЕ ПРОБЛЕМЫ ⚒️")],
                [KeyboardButton(text="📲 ОБРАТНАЯ СВЯЗЬ")],
                [KeyboardButton(text="⭐️ ПАРТНЁРСКАЯ ПРОГРАММА ⭐️")]
            ], 
            resize_keyboard=True
        )
    
        await message.answer("💟 <b>Системное уведомление</b> 💟\nВы вернулись в основное меню", reply_markup=menu_btns, parse_mode=ParseMode.HTML)
    
    elif message.text == "📱 Очистка кэша - ANDROID":
        step_1 = FSInputFile(IMG_DIR +"instructions/tech_problems/cache_clear_android/Шаг_1.png")
        step_2 = FSInputFile(IMG_DIR +"instructions/tech_problems/cache_clear_android/Шаг_2.png")
        step_3 = FSInputFile(IMG_DIR +"instructions/tech_problems/cache_clear_android/Шаг_3.png")
        step_4 = FSInputFile(IMG_DIR +"instructions/tech_problems/cache_clear_android/Шаг_4.png")
        step_5 = FSInputFile(IMG_DIR +"instructions/tech_problems/cache_clear_android/Шаг_5.png")
        step_6 = FSInputFile(IMG_DIR +"instructions/tech_problems/cache_clear_android/Шаг_6.png")
        step_7 = FSInputFile(IMG_DIR +"instructions/tech_problems/cache_clear_android/Шаг_7.png")
        step_8 = FSInputFile(IMG_DIR +"instructions/tech_problems/cache_clear_android/Шаг_8.png")
        step_9 = FSInputFile(IMG_DIR +"instructions/tech_problems/cache_clear_android/Шаг_9.png")
        step_10 = FSInputFile(IMG_DIR +"instructions/tech_problems/cache_clear_android/Шаг_10.png")
        
        media = [
            InputMediaPhoto(media=step_1),
            InputMediaPhoto(media=step_2),
            InputMediaPhoto(media=step_3),
            InputMediaPhoto(media=step_4),
            InputMediaPhoto(media=step_5),
            InputMediaPhoto(media=step_6),
            InputMediaPhoto(media=step_7),
            InputMediaPhoto(media=step_8),
            InputMediaPhoto(media=step_9),
            InputMediaPhoto(media=step_10)
        ]
        
        await bot.send_media_group(chat_id=message.chat.id, media=media)
        # await message.answer(text="При некорректной работе приложения Telegram (ограниченная функциональность, неработоспособность кнопок, отсутствие обновлений интерфейса)  может помочь очистка кэша на вашем устройстве.", reply_markup=None)
    elif message.text == "📱 Очистка кэша - IOS":
        step_1 = FSInputFile(IMG_DIR +"instructions/tech_problems/cache_clear_ios/Шаг_1.png")
        step_2 = FSInputFile(IMG_DIR +"instructions/tech_problems/cache_clear_ios/Шаг_2.png")
        step_3 = FSInputFile(IMG_DIR +"instructions/tech_problems/cache_clear_ios/Шаг_3.png")
        step_4 = FSInputFile(IMG_DIR +"instructions/tech_problems/cache_clear_ios/Шаг_4.png")
        step_5 = FSInputFile(IMG_DIR +"instructions/tech_problems/cache_clear_ios/Шаг_5.png")
        step_6 = FSInputFile(IMG_DIR +"instructions/tech_problems/cache_clear_ios/Шаг_6.png")
        step_7 = FSInputFile(IMG_DIR +"instructions/tech_problems/cache_clear_ios/Шаг_7.png")
        step_8 = FSInputFile(IMG_DIR +"instructions/tech_problems/cache_clear_ios/Шаг_8.png")
        step_9 = FSInputFile(IMG_DIR +"instructions/tech_problems/cache_clear_ios/Шаг_9.png")

        media = [
            InputMediaPhoto(media=step_1),
            InputMediaPhoto(media=step_2),
            InputMediaPhoto(media=step_3),
            InputMediaPhoto(media=step_4),
            InputMediaPhoto(media=step_5),
            InputMediaPhoto(media=step_6),
            InputMediaPhoto(media=step_7),
            InputMediaPhoto(media=step_8),
            InputMediaPhoto(media=step_9)
        ]
        
        await bot.send_media_group(chat_id=message.chat.id, media=media)


@dp.message(Command(commands="cancel"))
async def command_start_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("♻️ Действие было успешно отменено ")    


@dp.message(Command(commands="admin"))
async def command_admin(message: Message, state: FSMContext):
        tg_id =  message.from_user.id
        first_name = message.from_user.first_name
        
        admin = await db.check_admin(tg_id)
        if (admin):
            key_btns = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🟢 [ВКЛ] Режим рассылки", callback_data="admin_send")],
            [InlineKeyboardButton(text="👤 Пользователи", callback_data="admin_user_list"),
             InlineKeyboardButton(text="🪙 Платежи", callback_data="admin_payments")],
            [InlineKeyboardButton(text="🔑 Управление реферальной системой", callback_data="admin_referrals")],
            [InlineKeyboardButton(text="🔖 Информация о тарифах", callback_data="admin_tariffs")],
            [InlineKeyboardButton(text="🎲 Администраторы", callback_data="admin_list"),
            InlineKeyboardButton(text="🚫 Черный список", callback_data="admin_black_list")]], resize_keyboard=True)
            # [InlineKeyboardButton(text="Добавить в ЧС", callback_data="admin_ban_user"), 
            #  InlineKeyboardButton(text="Удалить из ЧС", callback_data="admin_unban_user")]
            
            await message.answer(f'🥷 {first_name}, добро пожаловать в панель администратора! 🥷', reply_markup=key_btns)


@dp.callback_query(F.data.startswith("admin_"))
async def admin_query(query: CallbackQuery, state: FSMContext):
    if (query.data == 'admin_send'):
        await query.message.answer("Для рассылки воспользуйтесь командой /send")
    elif (query.data == 'admin_user_list'): 
        user_list = await db.user_list()
        for user in user_list:
            user['Добавлен'] = user['Добавлен'].replace(' ', '\n', 1)
        table = tabulate(user_list, headers='keys', tablefmt="simple")

        table_message = length_control(table, 4096)
        for table in table_message:
            await query.message.answer(f'```Пользователи\n{table}```', parse_mode=ParseMode.MARKDOWN_V2)

    elif (query.data == 'admin_payments'):
        payments_list = await db.payment_list()
        for payment in payments_list:
            payment['Дата\nплатежа'] = payment['Дата\nплатежа'].replace(' ', '\n', 1)
        table = tabulate(payments_list, headers='keys', tablefmt="simple")
        await query.message.answer(f'```Платежи\n{table}```', parse_mode=ParseMode.MARKDOWN_V2)
        
    elif (query.data == 'admin_list'): 
        admin_list = await db.admin_send_list()
        for admin in admin_list:
            admin['Добавлен'] = admin['Добавлен'].replace(' ', '\n', 1)
        table = tabulate(admin_list, headers='keys', tablefmt="simple")
        await query.message.answer(f'```Администраторы\n{table}```', parse_mode=ParseMode.MARKDOWN_V2)
        
    elif (query.data == 'admin_referrals'): 
        key_btns = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Участники реферальной программы", callback_data="admin_ref_list")],
            [InlineKeyboardButton(text="Поиск информации об участнике по ID", callback_data="admin_ref_search")],
            [InlineKeyboardButton(text="Список партнёров программы", callback_data="admin_part_list")],
            [InlineKeyboardButton(text="Добавить нового партнёра", callback_data="admin_add_part")]])
        await query.message.answer("⚙️ <b>Параметры реферальной системы</b>", reply_markup=key_btns, parse_mode=ParseMode.HTML)
        
    elif (query.data == 'admin_ref_list'):
        ref_list =  await db.ref_list()
        table = tabulate(ref_list, headers='keys', tablefmt="simple")
        await query.message.answer(f'```Рефералы\n{table}```', parse_mode=ParseMode.MARKDOWN_V2)
    elif (query.data == 'admin_tariffs'):
        tariff_list = await db.tariff_list()
        table = tabulate(tariff_list, headers='keys', tablefmt="simple")
        await query.message.answer(f'```Тарифы\n{table}```', parse_mode=ParseMode.MARKDOWN_V2)

    elif (query.data == 'admin_black_list'):
        black_list = await db.black_list()
        if black_list:
            table = tabulate(black_list, headers='keys', tablefmt="simple")
            await query.message.answer(f'```Заблокированные\n{table}```', parse_mode=ParseMode.MARKDOWN_V2)
        else:
            await query.message.answer(f'```Заблокированные\nЧёрный список пуст```', parse_mode=ParseMode.MARKDOWN_V2)


@dp.message(Command("send"))
async def start_send(message: Message, state: FSMContext):
    tg_id =  message.from_user.id
    admin = await db.check_admin(tg_id)
    if (admin):
        await message.answer(
            "Режим рассылки активирован ✅\n\n"
            "Отправьте сообщение, фото или видео с подписью или без для рассылки всем пользователям ASTRO-LOVE❤️‍🔥"
        )
        await state.set_state(SendMedia.waiting_media)


# --- Альбом ---
@dp.message(SendMedia.waiting_media, F.media_group_id)
async def handle_album(message: Message, state: FSMContext):
    mg_id = message.media_group_id
    if mg_id not in album_storage:
        album_storage[mg_id] = {"media": [], "caption": None}
        album_storage[mg_id]["timer"] = asyncio.create_task(finalize_album(mg_id, message, state))

    if message.photo:
        album_storage[mg_id]["media"].append({"type": "photo", "file_id": message.photo[-1].file_id})
    elif message.video:
        album_storage[mg_id]["media"].append({"type": "video", "file_id": message.video.file_id})

    if not album_storage[mg_id]["caption"] and message.caption:
        album_storage[mg_id]["caption"] = message.caption


async def finalize_album(media_group_id: str, message: Message, state: FSMContext):
    await asyncio.sleep(1.0)
    data = album_storage.pop(media_group_id, None)
    if not data:
        return

    await state.update_data(media=data["media"], caption=data["caption"], type="media")
    await send_preview(message, state)


# --- Одиночное фото/видео ---
@dp.message(SendMedia.waiting_media, F.photo | F.video)
async def handle_single_media(message: Message, state: FSMContext):
    media_list = []
    caption = message.caption
    if message.photo:
        media_list.append({"type": "photo", "file_id": message.photo[-1].file_id})
    elif message.video:
        media_list.append({"type": "video", "file_id": message.video.file_id})

    await state.update_data(media=media_list, caption=caption, type="media")
    await send_preview(message, state)


# --- Только текст ---
@dp.message(SendMedia.waiting_media, F.text)
async def handle_text(message: Message, state: FSMContext):
    text = message.text
    await state.update_data(text=text, type="text")
    await send_preview(message, state)


# --- Предпросмотр ---
async def send_preview(message: Message, state: FSMContext):
    data = await state.get_data()
    tg_id = message.from_user.id

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Отправить", callback_data="send_all")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel")]
    ])

    if data.get("type") == "media":
        media_list = data["media"]
        caption = data.get("caption")
        media_group = []
        for idx, item in enumerate(media_list):
            if item["type"] == "photo":
                media = InputMediaPhoto(media=item["file_id"])
            else:
                media = InputMediaVideo(media=item["file_id"])
            if idx == 0 and caption:
                media.caption = caption
            media_group.append(media)

        await bot.send_media_group(chat_id=tg_id, media=media_group)
        await bot.send_message(
            chat_id=tg_id,
            text="⬆️ Предпросмотр содержимого для рассылки ⬆️\n\nОтправить всем пользователям ASTRO-LOVE❤️‍🔥?",
            reply_markup=kb
        )

    elif data.get("type") == "text":
        text = data.get("text")
        await bot.send_message(chat_id=tg_id, text=f"Предпросмотр текста для рассылки:\n\n{text}")
        await bot.send_message(chat_id=tg_id, text="Отправить всем пользователям ASTRO-LOVE❤️‍🔥?", reply_markup=kb)

    await state.set_state(SendMedia.confirm)


# --- Подтверждение отправки ---
@dp.callback_query(SendMedia.confirm, F.data == "send_all")
async def confirm_send(callback: CallbackQuery, state: FSMContext):
    progress_msg = await callback.message.edit_text("Подождите, идёт отправка сообщений...")
    data = await state.get_data()
    
    user_list = await db.user_send_list()
    user_ids = [user['tg_id'] for user in user_list] 
    admin_id = callback.from_user.id  # id администратора, который запустил рассылку

    success, fail = 0, 0

    for user_id in user_ids: 
        if user_id == admin_id:
            continue  # пропускаем отправку самому себе

        if data.get("type") == "media":
            media_list = data["media"]
            caption = data.get("caption")
            media_group = []
            for idx, item in enumerate(media_list):
                if item["type"] == "photo":
                    media = InputMediaPhoto(media=item["file_id"])
                else:
                    media = InputMediaVideo(media=item["file_id"])
                if idx == 0 and caption:
                    media.caption = caption
                media_group.append(media)
            try:
                msgs = await bot.send_media_group(chat_id=user_id, media=media_group)
                sent_messages.setdefault(user_id, []).extend(
                    [{"message_id": m.message_id, "type": "media"} for m in msgs]
                )
                success += 1
            except Exception as e:
                fail += 1
                logging.warning(f"Ошибка для {user_id}: {e}")
            await asyncio.sleep(0.05)

        elif data.get("type") == "text":
            text = data.get("text")
            try:
                msg = await bot.send_message(chat_id=user_id, text=text)
                sent_messages.setdefault(user_id, []).append({"message_id": msg.message_id, "type": "text"})
                success += 1
            except Exception as e:
                fail += 1
                logging.warning(f"Ошибка для {user_id}: {e}")
            await asyncio.sleep(0.05)
    
    edit_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Редактировать текст", callback_data="edit_all")],
        [InlineKeyboardButton(text="🗑 Удалить рассылку", callback_data="delete_all")]
    ])
    
    # Отправляем администратору уведомление:
    await progress_msg.edit_text(
        f"Рассылка отправлена ✅\n\n"
        f"Кол-во пользователей, которые успешно получили сообщения: {success}\n"
        f"Кол-во недоставленных сообщений: {fail}", 
        reply_markup=edit_kb
    )

    await state.clear()


# --- Отмена ---
@dp.callback_query(SendMedia.confirm, F.data == "cancel")
async def cancel_send(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Рассылка была отменена ❌")
    await state.clear()


# --- Удаление всех отправленных сообщений ---
@dp.callback_query(F.data == "delete_all")
async def delete_all_messages(callback: CallbackQuery):
    del_msg = await callback.message.edit_text("Подождите, идёт удаление сообщений...")
    deleted, failed = 0, 0

    for user_id, messages in sent_messages.items():
        deleted += 1
        for msg in messages:
            try:
                await bot.delete_message(chat_id=user_id, message_id=msg["message_id"]) 
            except Exception as e:
                failed += 1
                logging.warning(f"Ошибка удаления {msg['message_id']} для {user_id}: {e}")
    
    await del_msg.edit_text(
        f"Процесс удаления завершен ❎\n\nКол-во удаленных сообщений: {deleted}"
    )

    sent_messages.clear()


# --- Запрос нового текста для редактирования ---
@dp.callback_query(F.data == "edit_all")
async def ask_new_text(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Отправьте новый текст для изменения содержимого рассылки")
    await state.set_state(EditState.waiting_new_text)


# --- Применение редактирования ---
@dp.message(EditState.waiting_new_text)
async def apply_edit(message: Message, state: FSMContext):
    new_text = message.text
    edited_msgs, failed_msgs = 0, 0

    for user_id, messages in sent_messages.items():
        for idx, msg in enumerate(messages):
            try:
                if msg["type"] == "text":
                    await bot.edit_message_text(chat_id=user_id, message_id=msg["message_id"], text=new_text)
                    edited_msgs += 1
                elif msg["type"] == "media":
                    # Редактируем подпись только у первого сообщения медиагруппы
                    if idx == 0:
                        await bot.edit_message_caption(chat_id=user_id, message_id=msg["message_id"], caption=new_text)
                        edited_msgs += 1
                    # Для остальных сообщений медиагруппы пропускаем редактирование caption
            except Exception as e:
                failed_msgs += 1
                logging.warning(f"Ошибка редактирования {msg['message_id']} для {user_id}: {e}")

    await message.answer(
        f"Процесс редактирования завершен ✳️\n\n"
        f"Кол-во измененных сообщений: {edited_msgs}"
    )
    await state.clear()

# --- Покупка тарифов ---
@dp.callback_query(F.data.startswith("buy_now_"))
async def tariff_buy_query(query: CallbackQuery):
    date_invoice = f'{dt.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}'
    
    tariffs = {
        'buy_now_start': (599, 'СТАРТ', 'tariff_start'),
        'buy_now_base': (999, 'БАЗОВЫЙ', 'tariff_base'),
        'buy_now_vip': (2999, 'VIP', 'tariff_vip'),
        'buy_now_supervip': (9999, 'SUPER VIP', 'tariff_supervip')
    }

    if query.data in tariffs:
        price, tariff_name, payload_str = tariffs[query.data]
        
        await bot.send_invoice(
            chat_id=query.message.chat.id, 
            title=f'Покупка тарифа {tariff_name}',
            description=f'Создано ------ {date_invoice} ------ Счёт на оплату сформирован. Оплата осуществляется через Telegram.',
            payload=payload_str,
            provider_token=PAYMENT_TOKEN,
            currency='RUB',
            prices=[LabeledPrice(label='Стоимость выбранного тарифа', amount=price * 100)]
        )
        

# --- Процедура оплаты ---
@dp.pre_checkout_query(lambda query: True)
async def pre_checkout_query(pre_checkout: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout.id, ok=True)

# --- Успешный платёж ---
@dp.message(F.successful_payment)
async def successful_payment(message: Message, state: FSMContext):
    tg_id = message.from_user.id
    username = message.from_user.username
    total_amount = message.successful_payment.total_amount // 100
    logging.info(f'Успешный платёж на сумму {total_amount}: {tg_id} - {username}')
    
    profile_details = await db.check_profile_details(tg_id)
    if not profile_details:
        await db.add_new_profile_details(tg_id)
        
    currency = message.successful_payment.currency
    description = message.successful_payment.invoice_payload
    
    payload = description.split('_')
    selected_tariff = payload[1]
    promocode = payload[2] if len(payload) == 3 else None
    
    tariffs = {
        "start": (2, 599, "СТАРТ"),
        "base": (3, 999, "БАЗОВЫЙ"),
        "vip": (4, 2999, "VIP"),
        "supervip": (5, 9999, "SUPER VIP")
    }
    
    tariff_id, price, name = tariffs[selected_tariff]

    if promocode:
        ref_id = await db.check_ref_by_promo(promocode)
        earned_money = price - total_amount
        await db.update_earned_money(ref_id, earned_money)
        
    await db.update_user_details(tg_id, tariff_id)
    await db.add_new_payment(tg_id, description, total_amount, tariff_id)
    await message.answer(f'Оплата тарифа «{name}» на сумму {total_amount} {currency} прошла успешно!\nВаш тарифный план был изменён. Благодарим за покупку! ')



async def main():
    # Подключаемся к бд
    await db.connect()
    
    try:
        # Запускаем бота
        await dp.start_polling(bot)
    finally:
        # Закрываем соединение с бд при завершении
        await db.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
