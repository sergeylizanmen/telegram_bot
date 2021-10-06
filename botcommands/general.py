import requests
import json
import datetime
import telebot
import sqlite3


def insert_into_table(command: str, date_time: str, result: str) -> None:
    """
    Функция, которая создает (если нет) текстовую БД для введения истории команд

    :param command: Команда, которую в данный момент выполняет пользователь (str)
    :param date_time: Дата и время выполнения команды (str)
    :param result: Результат (город + список отелей, без фото) (str)
    :return: None
    """
    try:
        with sqlite3.connect('TooEasyTravel.db') as sqlite_connection:
            cursor = sqlite_connection.cursor()

            sqlite_create_table = """CREATE TABLE IF NOT EXISTS history
            (
            command_id INTEGER PRIMARY KEY AUTOINCREMENT,
            command TEXT NOT NULL,
            date_time TEXT NOT NULL,
            result TEXT NOT NULL
            )"""

            cursor.execute(sqlite_create_table)

            sqlite_insert_with_param = """INSERT INTO history
                                  (command, date_time, result)
                                  VALUES (?, ?, ?)
                                  """

            data_tuple = (command, date_time, result)
            cursor.execute(sqlite_insert_with_param, data_tuple)
            sqlite_connection.commit()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)


def find_all_hotels_by_parameters(message: 'TextMessage', options: dict) -> None:
    """
    Функция выводит информацию об отелях, по полученным параметрам
        ● название отеля,
        ● адрес,
        ● как далеко расположен от центра,
        ● цена,
        ● N фотографий отеля (если пользователь счёл необходимым их вывод)


    :param options: все параметры в виде словаря
    :param message: сообщение пользователя

    :return: None
    """

    # Назначает параметры переменым для удобства
    bot = options['bot']
    city_id = options['city_id']
    amount_of_hotels = options['amount_of_hotels']
    sort_type = options['sort_type']
    amount_of_photos = options['amount_of_photos']
    price_range = options['price_range']
    distance_range = options['distance_range']
    command = options['command']

    bot.send_message(message.chat.id, 'Идет поиск...')

    # Получает список отелей по параметрам
    url = "https://hotels4.p.rapidapi.com/properties/list"

    date_now = datetime.datetime.now().date()
    date_plus_three_days = date_now + datetime.timedelta(days=3)

    querystring = {'destinationId': city_id, 'pageNumber': "1", 'pageSize': 25,
                   'checkIn': date_now, 'checkOut': date_plus_three_days, 'adults1': "1",
                   'sortOrder': sort_type, 'locale': "ru_RU", 'currency': "RUB"}

    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': "9f0d9c157amsh42615855b43d5cbp1fa36cjsn44b504859a1e"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    response = json.loads(response.text)

    city_name = response['data']['body']['header']
    hotels_list = response['data']['body']['searchResults']['results'][:]

    if price_range:  # Если указан диапазон цен, то фильтруем список отелей
        for hotel_info in response['data']['body']['searchResults']['results']:
            price = hotel_info['ratePlan']['price']
            if not price_range[0] <= price["exactCurrent"] <= price_range[1]:
                hotels_list.pop(hotels_list.index(hotel_info))

    if distance_range:  # Если указан диапазон расстояния, то фильтруем список отелей
        for hotel_info in hotels_list[:]:

            distance = hotel_info["landmarks"][0]["distance"]
            distance = distance.replace(',', '.').split()
            distance = float(distance[0])

            if not distance_range[0] <= distance <= distance_range[1]:
                hotels_list.pop(hotels_list.index(hotel_info))

    hotels_list = hotels_list[:amount_of_hotels]

    # Выводим сообщения об отелях, также сохраняя в переменную result для ввода в БД
    result = f'\nРезультаты для {city_name}\nНайдено {len(hotels_list)} результатов:'
    bot.send_message(message.chat.id, result)

    for hotel_info in hotels_list:
        hotel_id = hotel_info['id']
        price = hotel_info['ratePlan']['price']
        try:
            hotel_result = f'{hotel_info["name"]}' \
                           f'\nАдрес: {hotel_info["address"]["streetAddress"]}' \
                           f'\nРастояние от центра: {hotel_info["landmarks"][0]["distance"]}' \
                           f'\nЦена {price["info"]}: {price["current"]}'
        except KeyError:
            pass

        bot.send_message(message.chat.id, hotel_result)
        result += '\n*****\n' + hotel_result

        if amount_of_photos:  # Если нужны фотографии - выводим их
            url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
            querystring = {"id": hotel_id}

            headers = {
                'x-rapidapi-host': "hotels4.p.rapidapi.com",
                'x-rapidapi-key': "9f0d9c157amsh42615855b43d5cbp1fa36cjsn44b504859a1e"
            }

            response = requests.request("GET", url, headers=headers, params=querystring)
            response = json.loads(response.text)

            hotel_photos_list = response['hotelImages']

            counter_photos = amount_of_photos
            if len(hotel_photos_list) < amount_of_photos:
                counter_photos = len(hotel_photos_list)

            for photo_number in range(counter_photos):
                try:
                    photo_url = hotel_photos_list[photo_number]['baseUrl'].format(size='z')
                    bot.send_photo(message.chat.id, photo_url)
                except telebot.apihelper.ApiTelegramException:
                    pass

    # Вводим полученные данные в БД
    insert_into_table(command=command, date_time=datetime.datetime.now().strftime('%m-%d-%Y %H:%M:%S'), result=result)


def need_photos(message: 'TextMessage', options: dict):
    """
    Функция узнает нужно ли выводить фотографии к отелям

    Если да, то выполняет функцию checking_the_amount_of_photos, и далее на следующий шаг команды
    Если нет, то отправляет параметры сразу

    :param options: все параметры в виде словаря
    :param message: сообщение пользователя

    :return: None
    """
    bot = options['bot']

    def checking_the_amount_of_photos(message_amount_of_photos: 'TextMessage'):
        """ Функция узнает сколько необходимо вывести фотографий (с проверкой ввода значения) """

        try:  # Введено корректное значение - find_all_hotels_by_parameters
            amount_of_photos = int(message_amount_of_photos.text)
            if amount_of_photos > 5:
                raise ValueError
            options['amount_of_photos'] = amount_of_photos
            find_all_hotels_by_parameters(message, options=options)

        except ValueError:  # Введено некорректное значение - переспрос
            bot.send_message(message.chat.id,
                             'ОШИБКА ВВОДА'
                             '\nВведите количество фотографий (числом), которые необходимо вывести в результате (не больше 5):')
            bot.register_next_step_handler(message, checking_the_amount_of_photos)

    if message.text.lower() in ('да', 'yes', 'lf', 'нуы'):  # Если нужны фото - checking_the_amount_of_photos
        bot.send_message(message.chat.id,
                         'Введите количество фотографий, которые необходимо вывести в результате (не больше 5):')
        bot.register_next_step_handler(message, checking_the_amount_of_photos)

    elif message.text.lower() in ('нет', 'no', 'ytn', 'тщ'):  # Если не нужны фото - find_all_hotels_by_parameters
        options['amount_of_photos'] = None
        find_all_hotels_by_parameters(message, options=options)

    else:  # Введено некорректное значение - переспрос
        bot.send_message(message.chat.id, 'Нужно ли загрузить фотографии отелей? (Да/Нет)')
        bot.register_next_step_handler(message, need_photos,
                                       options=options)


def checking_the_amount_of_hotels(message: 'TextMessage', **options) -> None:
    """
    Ф-ция получает сообщение пользователя о количестве отелей, которые необходимо вывести (<= 25)

    Если сообщение корректно, то отправляет параметры на следующий шаг команды
    Иначе выводит уведомление и запрос на повтор ввода

    :param message: сообщение пользователя
    :param **options: все именные параметры, которые передаются из других функций
    :return: None
    """

    bot = options['bot']
    try:  # Введено корректное значение - need_photos
        amount_of_hotels = int(message.text)
        if amount_of_hotels > 25:
            raise ValueError

        options['amount_of_hotels'] = amount_of_hotels
        bot.send_message(message.chat.id, 'Нужно ли загрузить фотографии отелей? (Да/Нет)')
        bot.register_next_step_handler(message, need_photos, options=options)

    except ValueError:  # Введено некорректное значение - переспрос
        bot.send_message(message.chat.id,
                         'ОШИБКА ВВОДА'
                         '\nВведите количество отелей (числом), которые необходимо вывести в результате (не больше 25):')
        bot.register_next_step_handler(message, checking_the_amount_of_hotels,
                                       bot=bot, city_id=options['city_id'],
                                       sort_type=options['sort_type'], price_range=options['price_range'],
                                       distance_range=options['distance_range'],
                                       command=options['command'])


def find_city_id(city: str = None) -> int | None:
    """
    Метод ищет по введенному названию города по API сервиса RapidApi

    Вовращает ID города, либо None

    :param city: название города (str)
    :return: Optional[int]
    """

    # Получаем значения городов
    city = city.title()
    url = 'https://hotels4.p.rapidapi.com/locations/search'

    querystring = {'query': city, 'locale': "ru_RU"}

    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': "9f0d9c157amsh42615855b43d5cbp1fa36cjsn44b504859a1e"
    }

    response = requests.request('GET', url, headers=headers, params=querystring)
    response = json.loads(response.text)

    # Проверяем значение пользователя
    for entity in response['suggestions'][0]['entities']:
        if entity['name'] == city or entity['name'] == city.replace(' ', '-'):
            return int(entity['destinationId'])
    return None
