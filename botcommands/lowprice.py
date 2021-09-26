from .general import find_city_id, checking_the_amount_of_hotels


def lowprice_command(message: 'TextMessage', bot: 'Telebot') -> None:
    """
    Команда бота /lowprice - выводит список отелей в выбранном городе (начиная с дешевых)

    Находит через ф-цию find_city_id ID города и отправляет данные на следующий шаг обработки,
    если города нет выводит соответствующее сообщение

    :param bot: Бот
    :param message: сообщение пользователя
    :return: None
    """

    bot.send_message(message.chat.id, 'Идет поиск...')

    city_id = find_city_id(message.text)
    if city_id:
        bot.send_message(message.chat.id,
                         'Введите количество отелей, которые необходимо вывести в результате (не больше 25):')
        bot.register_next_step_handler(message, checking_the_amount_of_hotels,
                                       bot=bot, city_id=city_id, sort_type='PRICE')
    else:
        bot.send_message(message.chat.id, f'{message.text} не найден в списке городов')
