from unittest.mock import call

import telebot
from telebot import types
import sqlite3 as sl

bot = telebot.TeleBot('6481776262:AAEIJnxer7PHF41X8U6iS8kqYWZNsHkc6lI')

con = sl.connect('support_service.db', check_same_thread=False)
cur = con.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT,
    last_name TEXT
    )""")

cur.execute("""CREATE TABLE IF NOT EXISTS phones(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    phone TEXT,
    type INT,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(type) REFERENCES phone_types(id)
    )""")
cur.execute("""CREATE TABLE IF NOT EXISTS phone_types(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_name TEXT
    )""")

ph_type = 0
contact_id = 0
fn = ' '
ln = ' '
cur.execute("""SELECT * FROM phone_types""")
phone_types = dict(cur.fetchall())


def create_user(fn, ln):
    cur.execute("""INSERT INTO users (first_name, last_name) VALUES (?, ?)""", (fn.lower(), ln.lower()))
    return cur.lastrowid


def get_user_by_id(id):
    cur.execute("SELECT * FROM users WHERE id=?", (id,))
    return cur.fetchall()


def get_numbers_by_user_id(id):
    cur.execute("SELECT * FROM phones WHERE user_id=?", (id,))
    return cur.fetchall()


# Для удаления данных
def delete_user_by_id(id):
    cur.execute("DELETE FROM phones WHERE user_id=?", (id,))
    cur.execute("DELETE FROM users WHERE id=?", (id,))
    return


def update_first_name_in_base(id, fn):
    cur.execute("UPDATE users SET first_name=? WHERE id=?", (fn.lower(), id))


def update_last_name_in_base(id, ln):
    cur.execute("UPDATE users SET last_name=? WHERE id=?", (ln.lower(), id))


def add_number_to_base(contact_id, new_number, type):
    cur.execute("""INSERT OR IGNORE INTO phones (user_id, phone, type) VALUES (?, ?, ?)""",
                (contact_id, new_number, type))
    return


def edit_number_to_base(new_number, req_id):
    cur.execute("""UPDATE phones SET phone=? WHERE id=?""", (new_number, req_id))
    return


def delete_number_from_base(req_id):
    cur.execute("""DELETE FROM phones WHERE id=?""", req_id)
    return


def get_users():
    cur.execute("SELECT * FROM users LIMIT 10")
    return cur.fetchall()


def search_contact_by_query(que):
    str_que = "%" + que.lower() + "%"
    cur.execute("SELECT users.id FROM phones FULL JOIN users ON phones.user_id = users.id WHERE phones.phone LIKE ? OR "
                "users.first_name LIKE ? OR users.last_name LIKE ? GROUP BY users.id", (str_que, str_que, str_que))
    return cur.fetchall()


'''
# Добавления человека в базу данных

@bot.message_handler(commands=['start'])
def start(message):
    connect = sl.connect('users.db')
    cursor = connect.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS login_id(
        id INTEGER,
        user_name TEXT,
        last_name TEXT,
        phone_number INTEGER
    )""")
    connect.commit()

    # Делаем проверку есть или нет данные
    people_id = message.chat.id
    people_user = message.chat.id, 'user_name'
    people_last = message.chat.id, 'last_name'
    people_phone = message.chat.id, 'phone_number'
    cursor.execute(f"SELECT id, user_name, last_name, phone_number FROM login_id id = {people_id}, "
                   f"user_name = {people_user}, last_name = {people_last}, phone_number = {people_phone}")
    data = cursor.fetchone()
    if data is None:
        # Добавляем свои данные
        user_id = [message.chat.id, 'user_name', 'last_name', 'phone_number']
        cursor.execute("INSERT INTO login_id VALUES(?, ?, ?);", user_id)
        connect.commit()
    else:
        bot.send_message(message.chat.id, 'Такой пользователь уже существует')


bot.message_handler(commands=['delete'])


def delete(message):
    connect = sl.connect('users.db')
    cursor = connect.cursor()
    people_id = message.chat.id
    people_user = message.chat.id, 'user_name'
    people_last = message.chat.id, 'last_name'
    people_phone = message.chat.id, 'phone_number'
    cursor.execute(f"DELETE FROM login_id WHERE id = {people_id}, "
                   f"user_name = {people_user}, last_name = {people_last}, phone_number = {people_phone}")
    connect.commit()
'''


@bot.message_handler(content_types=['text'])
def start_message(message):
    start_keyboard = types.InlineKeyboardMarkup()  # тип кнопку
    key_start = types.InlineKeyboardButton(text='В главное меню', callback_data='main_menu')  # Добавляется кнопка
    start_keyboard.add(key_start)
    mess = f'{message.from_user.first_name} {message.from_user.last_name}, Добро пожаловать в службу поддержки.'
    bot.send_message(message.chat.id, text=mess, reply_markup=start_keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    global contact_id
    global ph_type
    call_str = call.data.split('|')
    if len(call_str) > 0:
        action = call_str[0]
    if len(call_str) > 1:
        user_id = call_str[1]
    if len(call_str) > 2:
        phone_type = call_str[2]
    if call.data == 'main_menu':
        keyboard = types.InlineKeyboardMarkup()
        key_reg = types.InlineKeyboardButton(text='CisArt', callback_data='cis_art')
        keyboard.add(key_reg)
        key_money = types.InlineKeyboardButton(text='Money', callback_data='info_money')
        keyboard.add(key_money)
        key_orders = types.InlineKeyboardButton(text='Orders', callback_data='orders')
        keyboard.add(key_orders)
        key_question = types.InlineKeyboardButton(text='Another_Question', callback_data='another_Question')
        keyboard.add(key_question)
        key_directory = types.InlineKeyboardButton(text='Telephone_directory', callback_data='telephone_directory')
        keyboard.add(key_directory)
        bot.send_message(call.message.chat.id, text='Выберите действие:\n1 '
                                                    'Регистрация в КИС "АРТ": необходимо нажать на кнопку "CisArt".\n2 '
                                                    'Хотите понять про деньги?: необходимо нажать кнопку "Money".\n3 '
                                                    'Хотите узнать почему закрыт доступ: необходимо нажать на кнопку '
                                                    '"Orders".\n4 По другим вопросом: необходимо нажать на кнопку '
                                                    '"Another_Question"\n5 '
                                                    ' Если хотите войти в телефонный справочник: необходимо нажать на '
                                                    'кнопку "Telephone_directory" ', reply_markup=keyboard)
    elif call.data == 'cis_art':
        help_keyboard = types.InlineKeyboardMarkup()
        key_main = types.InlineKeyboardButton(text='Вернуться в главное меню', callback_data='main_menu')
        help_keyboard.add(key_main)
        bot.send_message(call.message.chat.id, text='Один раз можно получить временный идентификатор на 30дней.\n1. '
                                                    'За это время нужно завершить регистрацию постоянного ID - '
                                                    'инструкция есть на сайте Яндекс.Про.', reply_markup=help_keyboard)

    elif call.data == 'info_money':
        help_keyboard = types.InlineKeyboardMarkup()
        key_main = types.InlineKeyboardButton(text='Вернуться в главное меню', callback_data='main_menu')
        help_keyboard.add(key_main)
        bot.send_message(call.message.chat.id, text=' Если нужно разобраться с оплатой или бонусами по заказу — '
                                                    'выберите из списка заказов нужный и напишите нам.\n1  Не пришли '
                                                    'деньги за заказ, и прошло меньше трёх дней. Мы возмещаем нужную '
                                                    'сумму не позднее 3 дней с момента совершения поездки. Вам не '
                                                    'нужно для этого ничего делать — через три дня деньги придут '
                                                    'сами. Бывает, что пришла только часть суммы, это означает, '
                                                    'что недостающая часть дойдёт.\n2  Не пришли деньги за заказ, '
                                                    'и прошло больше трёх дней. Напишите нам в комментарии к заказу — '
                                                    'будем разбираться.\n3  Как снимается комиссия. Комиссия — это '
                                                    'плата'
                                                    'за получение заказа, она списывается за каждую поездку. Есть '
                                                    'комиссия сервиса и комиссия таксопарка (если вы работаете через '
                                                    'таксопарк). Списание комиссии по каждому заказу отражается в '
                                                    'Карточке финансового отчёта в профиле.',
                         reply_markup=help_keyboard)
    elif call.data == 'access':
        help_keyboard = types.InlineKeyboardMarkup()
        key_main = types.InlineKeyboardButton(text='Вернуться в главное меню', callback_data='main_menu')
        help_keyboard.add(key_main)
        bot.send_message(call.message.chat.id, text='Зайдите в раздел Диагностика. Здесь видно всё, что мешает '
                                                    'работе.\n1 Если есть надпись Доступ приостановлен — включилось '
                                                    'временное ограничение. Оно снимется автоматически, '
                                                    'система показывает точное время, когда можно вернуться к '
                                                    'заказам.\n2 Если горит надпись Доступ закрыт — следуйте '
                                                    'инструкциям, чтобы снова выйти на линию. В случае серьёзных '
                                                    'нарушений вернуться к заказам не получится.\n3 Чтобы успешно '
                                                    'работать и не терять доступ к заказам, пожалуйста, соблюдайте '
                                                    'стандарты качества и безопасности.', reply_markup=help_keyboard)
    elif call.data == 'orders':
        help_keyboard = types.InlineKeyboardMarkup()
        key_main = types.InlineKeyboardButton(text='Вернуться в главное меню', callback_data='main_menu')
        help_keyboard.add(key_main)
        bot.send_message(call.message.chat.id, text='Заказы распределяются системой автоматически, наши специалисты '
                                                    'не могут назначить заказ вручную. Это даёт всем водителям равные '
                                                    'условия работы.\n1 Сейчас поездок стало меньше, ждать заказов '
                                                    'приходится дольше. Если нового заказа нет, начните с этих '
                                                    'шагов:\n2 -Проверьте раздел Диагностика: если есть ограничения по '
                                                    'заказам, там будут все подробности\n3 — Проверьте, '
                                                    'есть ли стабильное интернет-подключение\n4  — Включите статус На '
                                                    'линии.\n5 Если всё работает стабильно, но заказы не приходят, '
                                                    'обратите внимание на эти рекомендации:\n6 — Держитесь ближе к '
                                                    'центру города.\n7 — Выходите на линию в пиковые часы: в будни с '
                                                    '7:00 до 21:00 и в выходные с 12:00 до полуночи\n8 — Не стойте на '
                                                    'месте, перемещайтесь\n9 — Переключайтесь в статус Занят только при'
                                                    'необходимости\n10 — Учитывайте, что заказов будет меньше, '
                                                    'если включён режим «Домой» или «По делам», выбран только один '
                                                    'способ оплаты\n11 — Используйте все доступные вам тарифы, '
                                                    'включая «Доставку» и «Курьер» — спрос на них сейчас растёт\n12 '
                                                    'Подключить тариф «Доставка» или «Курьер»',
                         reply_markup=help_keyboard)
    elif call.data == 'another_Question':
        help_keyboard = types.InlineKeyboardMarkup()
        key_main = types.InlineKeyboardButton(text='Вернуться в главное меню', callback_data='main_menu')
        help_keyboard.add(key_main)
        bot.send_message(call.message.chat.id, text='По другим вопросам звоните по номеру телефона: 89323233232',
                         reply_markup=help_keyboard)

    elif call.data == 'telephone_directory':
        help_keyboard = types.InlineKeyboardMarkup()
        key_start = types.InlineKeyboardButton(text='Справочная меню', callback_data='phone_menu')
        help_keyboard.add(key_start)
        bot.send_message(call.message.chat.id, text='Добро пожаловать в телефонный справочник:\n1 Вы можете найти '
                                                    'нужный '
                                                    'контакт и просмотреть,\n2 добавить контакты,\n3 удалить контакт,'
                                                    '\n4'
                                                    ' отредактировать контакт', reply_markup=help_keyboard)

    elif call.data == 'phone_menu':
        help_keyboard = types.InlineKeyboardMarkup()
        key_main = types.InlineKeyboardButton(text='Вернуться в главное меню', callback_data='main_menu')
        help_keyboard.add(key_main)
        key_watch = types.InlineKeyboardButton(text='Watch_contacts', callback_data='watch_contacts')
        help_keyboard.add(key_watch)
        key_search = types.InlineKeyboardButton(text='Search_contact', callback_data='search_contact')
        help_keyboard.add(key_search)
        key_add = types.InlineKeyboardButton(text='Add_contact', callback_data='add_contact')
        help_keyboard.add(key_add)
        key_add_number = types.InlineKeyboardButton(text='Добавить номер', callback_data='choose_type_number')
        help_keyboard.add(key_add_number)

        bot.send_message(call.message.chat.id,
                         text='1. Чтобы найти нужный контакт, необходимо нажать на кнопку "Search_contact" и ввести '
                              'имя или номер телефона\n2. Для добавления контакта нужно нажать на кнопку "Add_contact"'
                              ' и ввести необходимые данные\n3. Чтобы посмотреть журнал контактов: нужно нажать '
                              'на кнопку "Watch_contacts"',
                         reply_markup=help_keyboard)
    elif call.data == 'add_contact':
        help_keyboard = types.InlineKeyboardMarkup()
        key_start = types.InlineKeyboardButton(text='Справочная меню', callback_data='phone_menu')
        help_keyboard.add(key_start)
        bot.send_message(call.message.chat.id, text="Введите имя:")
        bot.register_next_step_handler(call.message, get_user_first_name)

    elif call.data == 'watch_contacts':
        help_keyboard = types.InlineKeyboardMarkup()
        key_start = types.InlineKeyboardButton(text='Справочная меню', callback_data='phone_menu')
        help_keyboard.add(key_start)
        users = get_users()
        users_keyboard = types.InlineKeyboardMarkup()
        for i in users:
            user_info = get_user_by_id(i[0])
            text = user_info[0][2].title() + ' ' + user_info[0][1].title()
            key_user = types.InlineKeyboardButton(text, callback_data='get_user|' + str(i[0]))
            users_keyboard.add(key_user)
        bot.send_message(call.message.chat.id, "Контакты: ", reply_markup=users_keyboard)
        if call.data == 'choose_type_number':
            users_keyboard = types.InlineKeyboardMarkup()
            for id in phone_types:
                key_type = types.InlineKeyboardButton(phone_types.get(id),
                                                      callback_data='add_number|' + str(user_id) + '|' + str(id))
                users_keyboard.add(key_type)
            bot.send_message(call.message.chat.id, "Выберите тип номера: ", reply_markup=users_keyboard)
        elif call.data == 'add_number':
            contact_id = user_id
            ph_type = phone_type
            bot.send_message(call.message.chat.id, text="Введите номер: ")
            bot.register_next_step_handler(call.message, ask_number_to_add)

    elif call.data == 'search_contact':
        bot.send_message(call.message.chat.id, text="Введите номер, имя или фамилию:")
        bot.register_next_step_handler(call.message, search_contact)

    elif call.data == 'choose_type_number':
        help_keyboards = types.InlineKeyboardMarkup()
        for id in phone_types:
            key_type = types.InlineKeyboardButton(phone_types.get(id),
                                                  callback_data='add_number|' + str(user_id) + '|' + str(id))
            help_keyboards.add(key_type)
        bot.send_message(call.message.chat.id, "Выберите тип номера: ", reply_markup=help_keyboards)

    elif call.data == 'add_number':
        contact_id = user_id
        ph_type = phone_type
        bot.send_message(call.message.chat.id, text="Введите номер: ")
        bot.register_next_step_handler(call.message, ask_number_to_add)

    elif call.data == "delete_contact":
        delete_user_by_id(user_id)
        delete_keyboard = types.InlineKeyboardMarkup()
        key_main = types.InlineKeyboardButton(text='Вернуться в главное меню', callback_data='main_menu')
        delete_keyboard.add(key_main)
        bot.send_message(call.message.chat.id, text="Контакт удален", reply_markup=delete_keyboard)

    elif call.data == "choose_number_to_delete":
        user_numbers = get_numbers_by_user_id(user_id)
        numbers_keyboard = types.InlineKeyboardMarkup()
        for number in user_numbers:
            key_number = types.InlineKeyboardButton(number[2],
                                                    callback_data='delete_number|' + str(user_id) + '|' + str(
                                                        number[0]))
            numbers_keyboard.add(key_number)
        bot.send_message(call.message.chat.id, "Выберите номер, который хотите удалить: ",
                         reply_markup=numbers_keyboard)

    elif call.data == "delete_number":
        contact_id = user_id
        ph_type = phone_type
        delete_number_from_base(phone_type)
        user_menu(contact_id, call.message.chat.id)
        contact_id = 0

    elif call.data == "get_user":
        user_menu(user_id, call.message.chat.id)


def get_user_first_name(message):
    global fn
    fn = message.text
    bot.send_message(message.chat.id, text="Введите фамилию:")
    bot.register_next_step_handler(message, get_user_last_name)


def ask_number_to_add(message):
    global contact_id
    global ph_type
    new_number = message.text
    add_number_to_base(contact_id, new_number, ph_type)
    user_menu(contact_id, message.chat.id)
    contact_id = 0
    ph_type = 0


def get_user_last_name(message):
    global ln
    ln = message.text
    user_id = create_user(fn, ln)
    user_menu(user_id, message.chat.id)


def user_menu(user_id, chat_id):
    global contact_id
    global ph_type
    global phone_types
    user_info = get_user_by_id(user_id)
    user_numbers = get_numbers_by_user_id(user_id)

    user_keyboard = types.InlineKeyboardMarkup()
    key_add = types.InlineKeyboardButton(text='Добавить номер', callback_data='choose_type_number|' + str(user_id))
    user_keyboard.add(key_add)
    key_edit_num = types.InlineKeyboardButton(text='Изменить номер',
                                              callback_data='choose_number_to_edit|' + str(user_id))
    user_keyboard.add(key_edit_num)

    if len(user_numbers) > 0:
        key_delete_num = types.InlineKeyboardButton(text='Удалить номер',
                                                    callback_data='choose_number_to_delete|' + str(user_id))
        user_keyboard.add(key_delete_num)

    key_edit_firstname = types.InlineKeyboardButton(text='Изменить имя', callback_data='edit_firstname|' + str(user_id))
    user_keyboard.add(key_edit_firstname)
    key_edit_lastname = types.InlineKeyboardButton(text='Изменить фамилию',
                                                   callback_data='edit_lastname|' + str(user_id))
    user_keyboard.add(key_edit_lastname)
    key_delete_user = types.InlineKeyboardButton(text='Удалить контакт', callback_data='delete_contact|' + str(user_id))
    user_keyboard.add(key_delete_user)
    key_main_menu = types.InlineKeyboardButton(text='Вернуться в главное меню', callback_data='main_menu')
    user_keyboard.add(key_main_menu)
    # Добавить данные:
    if len(user_numbers) > 0:
        phones = '\n\nТелефоны:'
        for i in user_numbers:
            phones = phones + '\n' + str(phone_types.get(i[3])) + ': ' + str(i[2])
    else:
        phones = ''

    text = "Пользователь ID-" + str(user_info[0][0]) + "\nИмя: " + str(user_info[0][1].title()) + "\nФамилия: " + str(
        user_info[0][2].title()) + phones

    bot.send_message(chat_id, text, reply_markup=user_keyboard)


def search_contact(message):
    query = message.text
    user_id = search_contact_by_query(query)

    if len(user_id) > 0:
        if len(user_id) == 1:
            user_menu(user_id[0][0], message.chat.id)
        elif len(user_id) > 1:
            users_keyboard = types.InlineKeyboardMarkup()
            for i in user_id:
                user_info = get_user_by_id(i[0])
                text = user_info[0][2].title() + ' ' + user_info[0][1].title()
                key_user = types.InlineKeyboardButton(text, callback_data='get_user|' + str(i[0]))
                users_keyboard.add(key_user)
            bot.send_message(message.chat.id, "Найдены пользователи: ", reply_markup=users_keyboard)
    else:
        user_keyboard = types.InlineKeyboardMarkup()
        key_main_menu = types.InlineKeyboardButton(text='Вернуться в главное меню', callback_data='main_menu')
        user_keyboard.add(key_main_menu)
        bot.send_message(message.chat.id, "Контакты или номера не найдены.", reply_markup=user_keyboard)


bot.polling(none_stop=True)
