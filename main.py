import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup
import time


token = "6430480724:AAGqJDjgjP1xSMex0T9YEo2HYbEKbQiWRfg"
bot = telebot.TeleBot(token)

admin_ids = [932038847,1074303708]

# Словарь для отслеживания статуса пользователей
user_status = {}
last_alert_click = {}


@bot.message_handler(func=lambda message: message.text == "Группа в ВК \U0001F310")
def pab(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, '<a href="https://vk.com/felazfortik"><u>Паблик в ВКонтакте</u></a>', parse_mode="HTML")

@bot.message_handler(func=lambda message: message.text == "Администраторы \U00002709")
def adm(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "@FelazPlay (Валентин)\n@elpochkad (Фёдор)", parse_mode="HTML")

@bot.message_handler(commands=["start"])
def farm(message):
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    button1 = types.KeyboardButton("Фарм \U0001F4DD")
    button2 = types.KeyboardButton("Алерты \U0001F514")
    button3 = types.KeyboardButton("Администраторы \U00002709")
    button4 = types.KeyboardButton("Группа в ВК \U0001F310")


    markup.add(button1, button2 ,button3, button4)
    bot.send_message(chat_id, "👋Привет, этот бот отправляет отчет по фарму В-Баксов администраторам, жми на кнопку <u><i><b>Фарм</b></i></u>, чтобы отправить отчет",
                     reply_markup=markup, parse_mode="HTML")





questions = [
    "1) 📝Кто фармил:",
    "2) 📝Ник аккаунта с которого фармили:",
    "3) 📝Кол-во нафармленных В-баксов:"
]


def create_type_selection_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    button1 = types.KeyboardButton("Фарм \U0001F4DD")
    button2 = types.KeyboardButton("Алерты \U0001F514")
    button3 = types.KeyboardButton("Администраторы \U00002709")
    button4 = types.KeyboardButton("Группа в ВК \U0001F310")

    markup.add(button1, button2, button3, button4)
    return markup


@bot.message_handler(func=lambda message: message.text == "Фарм \U0001F4DD")
def start_farm(message):
    chat_id = message.chat.id
    user_status[chat_id] = {'current_question': 0, 'answers': []}  # Создаем словарь для хранения статуса пользователя
    send_next_question(chat_id)  # Отправляем первый вопрос без клавиатуры

@bot.message_handler(func=lambda message: message.text == "Отмена")
def cancel_farm(message):
    chat_id = message.chat.id
    user_status.pop(chat_id, None)
    reply_markup = create_type_selection_keyboard()
    bot.send_message(chat_id, "⚠️Вы отменили отправку сообщения администрации.", reply_markup=reply_markup)




@bot.message_handler(func=lambda message: user_status.get(message.chat.id, {}).get('current_question') is not None, content_types=['text'])
def handle_farm_message(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    username = message.from_user.username
    user_info = f"@{username} ({user_name})"
    text = message.text
    current_question = user_status[chat_id]['current_question']
    answers = user_status[chat_id].get('answers', [])

    if current_question < len(questions):
        answers.append(text)  # Сохраняем ответ на текущий вопрос
        current_question += 1

        if current_question < len(questions):
            user_status[chat_id]['current_question'] = current_question
            user_status[chat_id]['answers'] = answers
            send_next_question(chat_id)  # Отправляем следующий вопрос
        else:
            user_status.pop(chat_id)
            send_application_to_admins(chat_id, user_info, answers)
    else:
        user_status.pop(chat_id)
        send_application_to_admins(chat_id, user_info, text)


def send_next_question(chat_id):
    current_question = user_status[chat_id]['current_question']
    question = questions[current_question]
    reply_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    button1 = types.KeyboardButton("Отмена")
    reply_markup.add(button1)
    bot.send_message(chat_id, question, reply_markup=reply_markup, parse_mode="HTML")


def send_application_to_admins(chat_id, user_info, answers):
    application_text = "\n".join([f"{questions[i]} {answers[i]}" for i in range(len(questions))])
    utc_time = time.gmtime()
    utc_time_plus_3 = time.mktime(utc_time) + 3 * 3600
    formatted_time = time.strftime('%d.%m.%Y %H:%M', time.localtime(utc_time_plus_3))

    application_text = f"{application_text}\n\nОтчет отправлен: {formatted_time} МСК"

    for admin_id in admin_ids:
        bot.send_message(admin_id, f"Фармер: {user_info} написал:\n{application_text}", parse_mode="HTML")

    # Отправляем сообщение с клавиатурой типа сообщения после отправки отчета
    bot.send_message(chat_id, "Ваше сообщение отправлено администраторам.",
                     reply_markup=create_type_selection_keyboard())






@bot.message_handler(func=lambda message: message.text == "Алерты \U0001F514")
def aler(message):
    user_id = message.chat.id
    last_click_time = last_alert_click.get(user_id)
    bot.send_message(message.chat.id,"⚙️Пожалуйста подождите...")
    if not last_click_time or (time.time() - last_click_time) >= 600:
        url = "https://stw-planner.com"
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            missions = soup.find_all('div', class_='mission-entry')


            if len(missions) == 0:
                bot.send_message(message.chat.id, "Сегодня нет алертов",reply_markup=create_type_selection_keyboard())
            else:
                for mission in missions:
                    title = mission.find('div', class_='mission-details').text.strip()
                    mission_pl = mission.find("div", class_="mission-pl").text.strip()
                    mis_backs = mission.find("div", class_="mission-reward-name").text.strip()
                    mission_info = f"{mission_pl} мощь\n{mis_backs} В-баксов"

                    bot.send_message(message.chat.id, f"🌩<i>{title}\n{mission_info}</i>", parse_mode="HTML",reply_markup=create_type_selection_keyboard())


        # Обновляем время последнего нажатия
        last_alert_click[user_id] = time.time()
    else:
        bot.send_message(message.chat.id, "Пожалуйста, подождите <i><b>10</b></i> минут перед следующим нажатием на <i><b>Алерты</b></i>",
                         parse_mode="HTML",reply_markup=create_type_selection_keyboard())


@bot.message_handler(func=lambda message: 1)
def mes(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "❗️Неизвестная команда",reply_markup=create_type_selection_keyboard())

bot.polling()