def help_command(message: 'TextMessage', bot: 'Telebot') -> None:
    """ Команда бота /help - выводит список всех команд"""

    bot.send_message(message.chat.id, '● /help — помощь по командам бота, '
                                      '\n● /lowprice — вывод самых дешёвых отелей в городе, '
                                      '\n● /highprice — вывод самых дорогих отелей в городе, '
                                      '\n● /bestdeal — вывод отелей, наиболее подходящих '
                                      'по цене и расположению от центра. '
                                      '\n● /history — вывод истории поиска отелей')