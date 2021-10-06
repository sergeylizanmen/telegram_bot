from .general import find_city_id, checking_the_amount_of_hotels


def distance_range_check(message: 'TextMessage', *, bot: 'Telebot', city_id: int, sort_type: str,
                         price_range: tuple | None) -> None:
    """
    Функция проверяющая диапазон расстояния от центра города, который ввел пользователь.
    Если введено 0, значит диапазон пользователю неважен и функция отправляет данные на следующий шаг

    :param price_range: диапазон цен, введенный пользователем
    :param sort_type: тип сортировки полученного списка отелей для API (str). Значения:
                                                PRICE - сначала дешевые
                                                PRICE_HIGHEST_FIRST - сначала дорогие
    :param city_id: ID города, который ввел пользователь (int)
    :param bot: Бот
    :param message: сообщение пользователя
    :return: None
    """
    distance_range = None
    if message.text != '0':
        try:  # Введено корректное значение - checking_the_amount_of_hotels
            bottom_border, upper_border = tuple(map(float, message.text.split('-')))
            if bottom_border < 0 or bottom_border > upper_border:
                raise ValueError

            distance_range = (bottom_border, upper_border)

            bot.send_message(message.chat.id,
                             'Введите количество отелей, которые необходимо вывести в результате (не больше 25):')
            bot.register_next_step_handler(message, checking_the_amount_of_hotels,
                                           bot=bot, city_id=city_id, sort_type='PRICE',
                                           price_range=price_range, distance_range=distance_range,
                                           command='/bestdeal')
        except ValueError:  # Введено некорректное значение - переспрос
            bot.send_message(message.chat.id,
                             'Введите диапазон расстояния от центра (км)'
                             '\nнижняя граница числом - верхняя граница числом:'
                             '\nИли 0, если расстояние не важно:')
            bot.register_next_step_handler(message, distance_range_check,
                                           bot=bot, city_id=city_id, sort_type=sort_type,
                                           price_range=price_range)
    else:  # Введено '0'
        bot.send_message(message.chat.id,
                         'Введите количество отелей, которые необходимо вывести в результате (не больше 25):')
        bot.register_next_step_handler(message, checking_the_amount_of_hotels,
                                       bot=bot, city_id=city_id, sort_type='PRICE',
                                       price_range=price_range, distance_range=distance_range,
                                       command='/bestdeal')


def price_range_check(message: 'TextMessage', *, bot: 'Telebot', city_id: int, sort_type: str) -> None:
    """
    Функция проверяющая диапазон цен, который ввел пользователь.
    Если введено 0, значит диапазон пользователю неважен и функция отправляет данные на следующий шаг

    :param sort_type: тип сортировки полученного списка отелей для API (str). Значения:
                                                PRICE - сначала дешевые
                                                PRICE_HIGHEST_FIRST - сначала дорогие
    :param city_id: ID города, который ввел пользователь (int)
    :param bot: Бот
    :param message: сообщение пользователя
    :return: None
    """
    price_range = None
    if message.text != '0':
        try:  # Введено корректное значение - distance_range_check
            bottom_border, upper_border = tuple(map(float, message.text.split('-')))
            if bottom_border < 0 or bottom_border > upper_border:
                raise ValueError

            price_range = (bottom_border, upper_border)

            bot.send_message(message.chat.id,
                             'Введите диапазон расстояния от центра (км)'
                             '\nнижняя граница числом - верхняя граница числом:'
                             '\nИли 0, если расстояние не важно:')
            bot.register_next_step_handler(message, distance_range_check,
                                           bot=bot, city_id=city_id, sort_type='PRICE',
                                           price_range=price_range)
        except ValueError:  # Введено некорректное значение - переспрос
            bot.send_message(message.chat.id,
                             'Введите диапазон цен (руб)'
                             '\nнижняя граница числом - верхняя граница числом'
                             '\nИли 0, если цена не важна:')
            bot.register_next_step_handler(message, price_range_check,
                                           bot=bot, city_id=city_id, sort_type=sort_type)
    else:  # Введено '0'
        bot.send_message(message.chat.id,
                         'Введите диапазон расстояния от центра (км)'
                         '\nнижняя граница числом - верхняя граница числом:'
                         '\nИли 0, если расстояние не важно:')
        bot.register_next_step_handler(message, distance_range_check,
                                       bot=bot, city_id=city_id, sort_type='PRICE',
                                       price_range=price_range)


def bestdeal_command(message: 'TextMessage', bot: 'Telebot') -> None:
    """
    Команда бота /bestdeal - вывод список отелей, наиболее подходящих по цене и расположению от центра.

    Находит через ф-цию find_city_id ID города и отправляет данные на следующий шаг обработки,
    если города нет выводит соответствующее сообщение

    :param bot: Бот
    :param message: сообщение пользователя
    :return: None
    """

    bot.send_message(message.chat.id, 'Идет поиск...')

    city_id = find_city_id(message.text)
    if city_id:  # если город найден - price_range_check
        bot.send_message(message.chat.id,
                         'Введите диапазон цен (руб)'
                         '\nнижняя граница числом - верхняя граница числом'
                         '\nИли 0, если цена не важна:')
        bot.register_next_step_handler(message, price_range_check,
                                       bot=bot, city_id=city_id, sort_type='PRICE')
    else:  # если город не найден - выход из команды
        bot.send_message(message.chat.id, f'{message.text} не найден в списке городов')
