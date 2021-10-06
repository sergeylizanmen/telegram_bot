import telebot
from decouple import config
import botcommands

bot = telebot.TeleBot(config('TOKEN_TELEGRAM_BOT'))


@bot.message_handler(content_types=['text'])
def get_text_messages(message: 'TextMessage') -> None:
    """
    Общий метод управления ботом

    Обрабатывает текстовые сообщения, по определенным командам вызывает соответсвующие функции

    :param message: Сообщение от пользователя
    :return: None
    """
    match message.text:  # реализация Python 3.10
        case '/help':
            botcommands.help_command(message, bot)

        case '/lowprice':
            bot.send_message(message.chat.id, 'Введи название города (на русском):')
            bot.register_next_step_handler(message, botcommands.lowprice_command, bot)

        case '/highprice':
            bot.send_message(message.chat.id, 'Введи название города (на русском):')
            bot.register_next_step_handler(message, botcommands.highprice_command, bot)

        case '/bestdeal':
            bot.send_message(message.chat.id, 'Введи название города (на русском):')
            bot.register_next_step_handler(message, botcommands.bestdeal_command, bot)

        case '/history':
            botcommands.history_command(message, bot)

        case _:
            bot.send_message(message.chat.id, 'Я тебя не понимаю. Напиши /help.')


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
