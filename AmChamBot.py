#!/usr/bin/env python
# coding: utf-8


import telebot
import sqlite3
from telebot import types
from datetime import datetime
from config import ADMINS, AMCHAM_BOT

botAmCham = telebot.TeleBot(AMCHAM_BOT)

def log_user_action(message, action):
    """Логирует действия пользователей"""
    conn = sqlite3.connect('bot_usage.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        last_action TEXT,
                        last_action_time TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS button_presses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        button_name TEXT,
                        press_time TEXT)''')

    cursor.execute('SELECT * FROM users WHERE user_id = ?', (message.from_user.id,))
    user_data = cursor.fetchone()

    if not user_data:
        cursor.execute('INSERT INTO users (user_id, username, last_action, last_action_time) VALUES (?, ?, ?, ?)',
                       (message.from_user.id, message.from_user.username, action, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    else:
        cursor.execute('UPDATE users SET last_action = ?, last_action_time = ? WHERE user_id = ?',
                       (action, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), message.from_user.id))

    cursor.execute('INSERT INTO button_presses (user_id, button_name, press_time) VALUES (?, ?, ?)',
                   (message.from_user.id, action, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

    conn.commit()
    conn.close()

@botAmCham.message_handler(commands=['track_users'])
def track_users(message):
    """Позволяет администраторам видеть, кто и когда выполнял действия"""
    if message.from_user.id not in ADMINS:
        botAmCham.send_message(message.chat.id, "❌ У вас нет прав для использования этой команды.")
        return

    conn = sqlite3.connect('bot_usage.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT user_id, username, last_action, last_action_time FROM users ORDER BY last_action_time DESC LIMIT 10')
    users = cursor.fetchall()

    conn.close()

    if users:
        response = "📊 *Последние действия пользователей:*\n\n"
        for user in users:
            user_id, username, last_action, last_action_time = user
            username_display = f"@{username}" if username else "Неизвестный пользователь"
            response += f"👤 {username_display} (ID: `{user_id}`)\n📝 Действие: *{last_action}*\n⏳ Время: `{last_action_time}`\n\n"
    else:
        response = "ℹ️ В базе данных пока нет записей о действиях пользователей."

    botAmCham.send_message(message.chat.id, response, parse_mode="Markdown")

@botAmCham.message_handler(commands=['start'])
def welcome(message):
    """Приветственное сообщение и выбор языка"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('🇷🇺 Русский')
    btn2 = types.KeyboardButton('🇺🇸 English')
    markup.row(btn1)
    markup.row(btn2)

    botAmCham.send_message(message.from_user.id, 'Добро пожаловать в AmCham Russia!', reply_markup=markup)
    botAmCham.send_message(message.from_user.id, 'Выберите язык ⬇️ Choose your language', reply_markup=markup)

    log_user_action(message, 'start')

@botAmCham.message_handler(content_types=['text'])
def body(message):

    if message.text == '🇷🇺 Русский':
    
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn3 = types.KeyboardButton('📚 О нас')
        btn4 = types.KeyboardButton('🤝 Как стать членом Палаты?')
        btn5 = types.KeyboardButton('🎬 Мероприятия AmCham')
        btn6 = types.KeyboardButton('🏦 Комитеты AmCham')
        btn7 = types.KeyboardButton('📲 AmCham Russia в Telegram')
        btn71 = types.KeyboardButton('📲 AmCham Russia в YouTube')
        btn72 = types.KeyboardButton('📲 AmCham Russia в LinkedIn')
        btn8 = types.KeyboardButton('🔙 Вернуться к выбору языка')
        markup.row(btn3, btn4)
        markup.row(btn5, btn6)
        markup.row(btn7, btn71) 
        markup.row(btn72, btn8)   
        botAmCham.send_message(message.from_user.id, "👋 Вас приветствует Американская торговая палата в России!", reply_markup=markup)
        botAmCham.send_message(message.from_user.id, 'Выберите интересующий вас раздел', reply_markup=markup, parse_mode='Markdown')
        

    elif message.text == '🔙 Вернуться к выбору языка':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('🇷🇺 Русский')
        btn2 = types.KeyboardButton('🇺🇸 English')
        markup.row(btn1)
        markup.row(btn2)
        botAmCham.send_message(message.from_user.id, "Выберите язык ⬇️ Choose your language", reply_markup=markup) 

                        
    elif message.text == '📚 О нас':
        start_markup = telebot.types.InlineKeyboardMarkup()
        btn9 = types.InlineKeyboardButton(text='Наша деятельность', url='https://www.amcham.ru/rus/about')
        btn10 = types.InlineKeyboardButton(text='Преимущества членства', url='https://www.amcham.ru/rus/membership_benefits')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('🔙 Главное меню')
        start_markup.row(btn9)
        start_markup.row(btn10)
        markup.row(btn1)
        botAmCham.send_message(message.from_user.id, 'AmCham - иностранная ассоциация деловых кругов, оказывающая поддержку своим членам в экономических вопросах и предоставляющая им возможности для обмена опытом и контактами.\n \nУ нас действуют 18 отраслевых комитетов, проводятся более 200 мероприятий ежегодно, а членство является инвестицией в авторитетную и эффективную организацию, которая способствует росту бизнеса в России.', reply_markup=start_markup, parse_mode='Markdown')

    elif message.text == '🤝 Как стать членом Палаты?':
        start_markup = telebot.types.InlineKeyboardMarkup()
        btn11 = types.InlineKeyboardButton(text='Подробнее о членстве', url='https://www.amcham.ru/rus/membership')
        btn09 = types.InlineKeyboardButton(text='Напишите нам', url='https://tinyurl.com/394wdpu9')
        btn12 = types.InlineKeyboardButton(text='Заполнить заявку на вступление', url='https://www.amcham.ru/rus/membership_form/registration')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('🔙 Главное меню')
        start_markup.row(btn11)
        start_markup.row(btn09)
        start_markup.row(btn12)
        markup.row(btn1)
        botAmCham.send_message(message.from_user.id, 'Приглашаем вас присоединиться к Американской торговой палате в России, где вы сможете расширить контакты и получить доступ к новым возможностям для роста.', reply_markup=start_markup, parse_mode='Markdown')
 
    elif message.text == '🎬 Мероприятия AmCham':
        start_markup = telebot.types.InlineKeyboardMarkup()
        btn13 = types.InlineKeyboardButton(text='Предстоящие мероприятия', url='https://www.amcham.ru/rus/events')
        btn113 = types.InlineKeyboardButton(text='Все мероприятия AmCham', url='https://www.amcham.ru/eng/policy_events')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('🔙 Главное меню')
        start_markup.row(btn13)
        start_markup.row(btn113)
        markup.row(btn1)
        botAmCham.send_message(message.from_user.id, 'Ежегодно наша Палата проводит более 200 мероприятий разного уровня, включая эксклюзивные брифинги с участием первых лиц и представителей руководства компаний, конференци и заседания комитетов.\n \nAmCham предоставляет своим членам уникальные возможности для обмена идеями, получения доступа к аналитической информации о рынке и установления контактов.', reply_markup=start_markup, parse_mode='Markdown')

    elif message.text == '🏦 Комитеты AmCham':
        start_markup = telebot.types.InlineKeyboardMarkup()
        btn14 = types.InlineKeyboardButton(text='Список комитетов', url='https://www.amcham.ru/rus/committees')
        btn114 = types.InlineKeyboardButton(text='Деятельность комитетов', url='https://www.amcham.ru/rus/events/committee_highlights')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('🔙 Главное меню')
        start_markup.row(btn14)
        start_markup.row(btn114)
        markup.row(btn1)
        botAmCham.send_message(message.from_user.id, 'В нашей палате действуют 20 отраслевых комитетов, которые занимаются основной контентной работой и являются площадкой для продвижения своей экспертизы и обмена практическим опытом.\n \nЗаседания всех комитетов являются открытыми для посещения любыми сотрудниками компаний-членов Палаты при предварительной регистрации.\n \nТакже мы с радостью приветствуем выступление представители компаний в качестве спикеров на тематических мероприятиях.', reply_markup=start_markup, parse_mode='Markdown')
  
    elif message.text =='📲 AmCham Russia в Telegram':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('🔙 Главное меню')
        markup.add(btn1)
        botAmCham.send_message(message.from_user.id, 'Чтобы быть в курсе всех актуальных новостей AmCham Russia, подписывайтесь на наш телеграм' + ' [канал](https://t.me/+Nwu-naDLzNY5ZWIy)', reply_markup=markup, parse_mode='Markdown')
        
    elif message.text =='📲 AmCham Russia в YouTube':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('🔙 Главное меню')
        markup.add(btn1)
        botAmCham.send_message(message.from_user.id, 'Чтобы посмотреть, как это было, загляните в наш AmCham Russia YouTube' + ' [канал](https://www.youtube.com/channel/UC8hwSL2_NGxuCWSPDWDpwxA)', reply_markup=markup, parse_mode='Markdown')

    elif message.text =='📲 AmCham Russia в LinkedIn':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('🔙 Главное меню')
        markup.add(btn1)
        botAmCham.send_message(message.from_user.id, 'AmCham Russia в' + ' [LinkedIn](https://www.linkedin.com/company/american-chamber-of-commerce-in-russia/)', reply_markup=markup, parse_mode='Markdown')
 
    elif message.text == '🔙 Главное меню':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn3 = types.KeyboardButton('📚 О нас')
        btn4 = types.KeyboardButton('🤝 Как стать членом Палаты?')
        btn5 = types.KeyboardButton('🎬 Мероприятия AmCham')
        btn6 = types.KeyboardButton('🏦 Комитеты AmCham')
        btn7 = types.KeyboardButton('📲 AmCham Russia в Telegram')
        btn71 = types.KeyboardButton('📲 AmCham Russia в YouTube')
        btn72 = types.KeyboardButton('📲 AmCham Russia в LinkedIn')
        btn8 = types.KeyboardButton('🔙 Вернуться к выбору языка')
        markup.row(btn3, btn4)
        markup.row(btn5, btn6)
        markup.row(btn7, btn71) 
        markup.row(btn72, btn8)     
        botAmCham.send_message(message.from_user.id, "Выберите интересующий вас раздел", reply_markup=markup)

    elif message.text == '🇺🇸 English':
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn3 = types.KeyboardButton('📚 About us')
        btn4 = types.KeyboardButton('🤝 To become a member')
        btn5 = types.KeyboardButton('🎬 AmCham Events')
        btn6 = types.KeyboardButton('🏦 AmCham Committees')
        btn7 = types.KeyboardButton('📲 Our Telegram channel')
        btn71 = types.KeyboardButton('📲 AmCham Russia in YouTube')
        btn72 = types.KeyboardButton('📲 AmCham Russia in LinkedIn')
        btn8 = types.KeyboardButton('🔙 Back to language selection')
        markup.row(btn3, btn4)
        markup.row(btn5, btn6) 
        markup.row(btn7, btn71) 
        markup.row(btn72, btn8)       
        botAmCham.send_message(message.chat.id, "👋 Welcome to The American Chamber of Commerce in Russia!", reply_markup=markup)
        botAmCham.send_message(message.from_user.id, 'Please select the section you are interested in', reply_markup=markup)
    
    elif message.text == '🔙 Back to language selection':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('🇷🇺 Русский')
        btn2 = types.KeyboardButton('🇺🇸 English')
        markup.row(btn1)
        markup.row(btn2)
        botAmCham.send_message(message.from_user.id, "Выберите язык ⬇️ Choose your language", reply_markup=markup)      
        
    elif message.text == '📚 About us':
        start_markup = telebot.types.InlineKeyboardMarkup()
        btn9 = types.InlineKeyboardButton(text='What we do', url='https://www.amcham.ru/eng/about')
        btn10 = types.InlineKeyboardButton(text='Membership benefits', url='https://www.amcham.ru/eng/membership_benefits')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('🔙 Main menu')
        start_markup.row(btn9)
        start_markup.row(btn10)
        markup.row(btn1)
        botAmCham.send_message(message.from_user.id, 'The American Chamber of Commerce in Russia (AmCham) is the leading international business organization in Russia.\n \nWe have 18 industry committees and hold more than 200 events annually. \n \n AmCham membership is an investment into effective organization that helps your business growth in Russia.', reply_markup=start_markup, parse_mode='Markdown') 

    elif message.text == '🤝 To become a member':
        start_markup = telebot.types.InlineKeyboardMarkup()
        btn11 = types.InlineKeyboardButton(text='About our membership', url='https://www.amcham.ru/eng/membership')
        btn111 = types.InlineKeyboardButton(text='Contact us', url='https://tinyurl.com/394wdpu9')
        btn12 = types.InlineKeyboardButton(text='Online application form', url='https://www.amcham.ru/eng/membership_form/registration')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('🔙 Main menu')
        start_markup.row(btn11)
        start_markup.row(btn111)
        start_markup.row(btn12)
        markup.row(btn1)
        botAmCham.send_message(message.from_user.id, 'We invite you to join the American Chamber of Commerce in Russia, where you will be able to expand your contacts and gain access to new opportunities.', reply_markup=start_markup, parse_mode='Markdown')
 
    elif message.text == '🎬 AmCham Events':
        start_markup = telebot.types.InlineKeyboardMarkup()
        btn13 = types.InlineKeyboardButton(text='Upcomming events', url='https://www.amcham.ru/eng/events')
        btn113 = types.InlineKeyboardButton(text='All AmCham events', url='https://www.amcham.ru/eng/policy_events')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('🔙 Main menu')
        start_markup.row(btn13)
        start_markup.row(btn113)
        markup.row(btn1)
        botAmCham.send_message(message.from_user.id, 'Every year AmCham holds more than 200 events of diverse levels, including executive briefings, conferences and committee meetings. \n \nWe provide our members with unique opportunities to exchange ideas and expertise and to establish new contacts.', reply_markup=start_markup, parse_mode='Markdown')

    elif message.text == '🏦 AmCham Committees':
        start_markup = telebot.types.InlineKeyboardMarkup()
        btn14 = types.InlineKeyboardButton(text='List of committees', url='https://www.amcham.ru/eng/committees')
        btn114 = types.InlineKeyboardButton(text='Committee highlights', url='https://www.amcham.ru/eng/events/committee_highlights')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('🔙 Main menu')
        start_markup.row(btn14)
        start_markup.row(btn114)
        markup.row(btn1)
        botAmCham.send_message(message.from_user.id, 'Our 20 sectoral committees offer expert analysis and advice to members regarding the latest developments in various areas of economy.', reply_markup=start_markup, parse_mode='Markdown')
  
    elif message.text == '📲 Our Telegram channel':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('🔙 Main menu')
        markup.add(btn1)
        botAmCham.send_message(message.from_user.id, 'Please follow us at AmCham Russia' + ' [Telegram](https://t.me/+Nwu-naDLzNY5ZWIy)', reply_markup=markup, parse_mode='Markdown')
                        
    elif message.text =='📲 AmCham Russia in YouTube':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('🔙 Main menu')
        markup.add(btn1)
        botAmCham.send_message(message.from_user.id, 'Have a look at AmCham Russia YouTube' + ' [channel](https://www.youtube.com/channel/UC8hwSL2_NGxuCWSPDWDpwxA)', reply_markup=markup, parse_mode='Markdown')

    elif message.text =='📲 AmCham Russia in LinkedIn':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('🔙 Main menu')
        markup.add(btn1)
        botAmCham.send_message(message.from_user.id, 'AmCham Russia in' + ' [LinkedIn](https://www.linkedin.com/company/american-chamber-of-commerce-in-russia/)', reply_markup=markup, parse_mode='Markdown')
 
 
    elif message.text == '🔙 Main menu':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn3 = types.KeyboardButton('📚 About us')
        btn4 = types.KeyboardButton('🤝 To become a member')
        btn5 = types.KeyboardButton('🎬 AmCham Events')
        btn6 = types.KeyboardButton('🏦 AmCham Committees')
        btn7 = types.KeyboardButton('📲 Our Telegram channel')
        btn71 = types.KeyboardButton('📲 AmCham Russia in YouTube')
        btn72 = types.KeyboardButton('📲 AmCham Russia in LinkedIn')
        btn8 = types.KeyboardButton('🔙 Back to language selection')
        markup.row(btn3, btn4)
        markup.row(btn5, btn6) 
        markup.row(btn7, btn71) 
        markup.row(btn72, btn8)     
        botAmCham.send_message(message.from_user.id, 'Please select the section you are interested in', reply_markup=markup)

botAmCham.polling(none_stop=True) 





