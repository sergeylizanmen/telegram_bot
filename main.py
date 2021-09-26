import telebot
from decouple import config
import botcommands

bot = telebot.TeleBot(config('TOKEN_TELEGRAM_BOT'))


def command_help(message: 'TextMessage') -> None:
    """ Команда бота /help - выводит список всех команд"""

    bot.send_message(message.chat.id, '● /help — помощь по командам бота, '
                                      '\n● /lowprice — вывод самых дешёвых отелей в городе, '
                                      '\n● /highprice — вывод самых дорогих отелей в городе, '
                                      '\n● /bestdeal — вывод отелей, наиболее подходящих по цене и расположению от центра. '
                                      '\n● /history — вывод истории поиска отелей')


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
        bot.register_next_step_handler(message, botcommands.lowprice_command, bot)
    elif message.text == '/highprice':
        bot.send_message(message.chat.id, 'Введи название города (на русском):')
        bot.register_next_step_handler(message, botcommands.highprice_command, bot)
    else:
        bot.send_message(message.chat.id, 'Я тебя не понимаю. Напиши /help.')


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
