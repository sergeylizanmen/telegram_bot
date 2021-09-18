import telebot
import requests
import json
from typing import Optional
import datetime

bot = telebot.TeleBot('1911628301:AAEzSl5P7gK3fNGkh3AXeqHM7b0kYKgOwnk')


def command_help(message: 'TextMessage') -> None:
    """ Команда бота /help - выводит список всех команд"""

    bot.send_message(message.chat.id, '● /help — помощь по командам бота, '
                                      '\n● /lowprice — вывод самых дешёвых отелей в городе, '
                                      '\n● /highprice — вывод самых дорогих отелей в городе, '
                                      '\n● /bestdeal — вывод отелей, наиболее подходящих по цене и расположению от центра. '
                                      '\n● /history — вывод истории поиска отелей')


def find_all_hotels_by_parameters(message: 'TextMessage', *, city_id: int, sort_type: str, amount_of_hotels: int,
                                  amount_of_photos: Optional[int]) -> None:
    """
    Функция выводит информацию об отелях, по полученным параметрам
        ● название отеля,
        ● адрес,
        ● как далеко расположен от центра,
        ● цена,
        ● N фотографий отеля (если пользователь счёл необходимым их вывод)


    :param message: сообщение пользователя
    :param city_id: ID города, который ввел пользователь (int)
    :param sort_type: тип сортировки полученного списка отелей для API (str). Значения:
                                                PRICE - сначала дешевые
                                                PRICE_HIGHEST_FIRST - сначала дорогие
    :param amount_of_hotels: Сколько необходимо вывести отелей (int)
    :param amount_of_photos: Сколько фотографий необходимо вывести (не больше 3),
                                                если None, то фотографий не будет
    :return: None
    """
    bot.send_message(message.chat.id, 'Идет поиск...')
    url = "https://hotels4.p.rapidapi.com/properties/list"

    date_now = datetime.datetime.now().date()
    date_plus_three_days = date_now + datetime.timedelta(days=3)

    querystring = {'destinationId': city_id, 'pageNumber': "1", 'pageSize': amount_of_hotels,
                   'checkIn': date_now, 'checkOut': date_plus_three_days, 'adults1': "1",
                   'sortOrder': sort_type, 'locale': "ru_RU", 'currency': "RUB"}

    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': "9f0d9c157amsh42615855b43d5cbp1fa36cjsn44b504859a1e"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    response = json.loads(response.text)

    city_name = response['data']['body']['header']
    hotels_list = response['data']['body']['searchResults']['results']

    bot.send_message(message.chat.id, f'\nРезультаты для {city_name}'
                                      f'\nНайдено {len(hotels_list)} результатов:')

    for hotel_info in hotels_list:
        hotel_id = hotel_info['id']
        price = hotel_info['ratePlan']['price']
        bot.send_message(message.chat.id, f'{hotel_info["name"]}'
                                          f'\nАдрес: {hotel_info["address"]["streetAddress"]}'
                                          f'\nРастояние от центра: {hotel_info["landmarks"][0]["distance"]}'
                                          f'\nЦена {price["info"]}: {price["current"]}')

        if amount_of_photos:
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
                    bot.send_photo(message.chat.id, hotel_photos_list[photo_number]['baseUrl'])
                except telebot.apihelper.ApiTelegramException:  # если фотография не найдена
                    pass


def need_photos(message: 'TextMessage', *, city_id: int, sort_type: str, amount_of_hotels: int):
    """
    Функция узнает нужно ли выводить фотографии к отелям

    Если да, то выполняет функцию checking_the_amount_of_photos, и далее на следующий шаг команды
    Если нет, то отправляет параметры сразу

    :param message: сообщение пользователя
    :param city_id: ID города, который ввел пользователь (int)
    :param sort_type: тип сортировки полученного списка отелей для API (str). Значения:
                                                PRICE - сначала дешевые
                                                PRICE_HIGHEST_FIRST - сначала дорогие
    :param amount_of_hotels: Сколько необходимо вывести отелей (int)
    :return: None
    """

    def checking_the_amount_of_photos(message_amount_of_photos: 'TextMessage'):
        """ Функция узнает сколько необходимо вывести фотографий (с проверкой ввода значения) """

        try:
            amount_of_photos = int(message_amount_of_photos.text)
            if amount_of_photos > 3:
                raise ValueError

            find_all_hotels_by_parameters(message, city_id=city_id, sort_type=sort_type,
                                          amount_of_hotels=amount_of_hotels, amount_of_photos=amount_of_photos)

        except ValueError:
            bot.send_message(message.chat.id,
                             'ОШИБКА ВВОДА'
                             '\nВведите количество фотографий (числом), которые необходимо вывести в результате (не больше 3):')
            bot.register_next_step_handler(message, checking_the_amount_of_photos)

    if message.text.lower() in ('да', 'yes', 'lf', 'нуы'):
        bot.send_message(message.chat.id,
                         'Введите количество фотографий, которые необходимо вывести в результате (не больше 3):')
        bot.register_next_step_handler(message, checking_the_amount_of_photos)
    elif message.text.lower() in ('нет', 'no', 'ytn', 'тщ'):
        find_all_hotels_by_parameters(message, city_id=city_id, sort_type=sort_type,
                                      amount_of_hotels=amount_of_hotels, amount_of_photos=None)
    else:
        bot.send_message(message.chat.id, 'Нужно ли загрузить фотографии отелей? (Да/Нет)')
        bot.register_next_step_handler(message, need_photos, city_id=city_id, sort_type=sort_type,
                                       amount_of_hotels=amount_of_hotels)


def checking_the_amount_of_hotels(message: 'TextMessage', *, city_id: int, sort_type: str) -> None:
    """
    Ф-ция получает сообщение пользователя о количестве отелей, которые необходимо вывести (<= 25)

    Если сообщение корректно, то отправляет параметры на следующий шаг команды
    Иначе выводит уведомление и запрос на повтор ввода

    :param message: сообщение пользователя
    :param city_id: ID города, который ввел пользователь (int)
    :param sort_type: тип сортировки полученного списка отелей для API (str). Значения:
                                                PRICE - сначала дешевые
                                                PRICE_HIGHEST_FIRST - сначала дорогие
    :return: None
    """
    try:
        amount_of_hotels = int(message.text)
        if amount_of_hotels > 25:
            raise ValueError

        bot.send_message(message.chat.id, 'Нужно ли загрузить фотографии отелей? (Да/Нет)')
        bot.register_next_step_handler(message, need_photos, city_id=city_id, sort_type=sort_type,
                                       amount_of_hotels=amount_of_hotels)

    except ValueError:
        bot.send_message(message.chat.id,
                         'ОШИБКА ВВОДА'
                         '\nВведите количество отелей (числом), которые необходимо вывести в результате (не больше 25):')
        bot.register_next_step_handler(message, checking_the_amount_of_hotels, city_id=city_id, sort_type=sort_type)


def find_city_id(city: str = None) -> Optional[int]:
    """
    Метод ищет по введенному названию города по API сервиса RapidApi

    Вовращает ID города, либо None

    :param city: название города (str)
    :return: Optional[int]
    """

    city = city.title()
    url = 'https://hotels4.p.rapidapi.com/locations/search'

    querystring = {'query': city, 'locale': "ru_RU"}

    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': "9f0d9c157amsh42615855b43d5cbp1fa36cjsn44b504859a1e"
    }

    response = requests.request('GET', url, headers=headers, params=querystring)
    response = json.loads(response.text)

    for entity in response['suggestions'][0]['entities']:
        if entity['name'] == city or entity['name'] == city.replace(' ', '-'):
            return int(entity['destinationId'])
    return None


def command_lowprice(message: 'TextMessage') -> None:
    """
    Команда бота /lowprice - выводит список отелей в выбранном городе

    Находит через ф-цию find_city_id ID города и отправляет данные на следующий шаг обработки,
    если города нет выводит соответствующее сообщение

    :param message: сообщение пользователя
    :return: None
    """

    city_id = find_city_id(message.text)
    if city_id:
        bot.send_message(message.chat.id,
                         'Введите количество отелей, которые необходимо вывести в результате (не больше 25):')
        bot.register_next_step_handler(message, checking_the_amount_of_hotels, city_id=city_id, sort_type='PRICE')
    else:
        bot.send_message(message.chat.id, f'{message.text} не найден в списке городов')


@bot.message_handler(content_types=['text'])
def get_text_messages(message: 'TextMessage') -> None:
    """
    Общий метод управления ботом

    Обрабатывает текстовые сообщения, по определенным командам вызывает соответсвующие функции

    :param message:
    :return: None
    """

    if message.text == '/help':
        command_help(message)
    elif message.text == '/lowprice':
        bot.send_message(message.chat.id, 'Введи название города (на русском):')
        bot.register_next_step_handler(message, command_lowprice)
    else:
        bot.send_message(message.chat.id, 'Я тебя не понимаю. Напиши /help.')


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)