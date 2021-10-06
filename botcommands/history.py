import sqlite3


def history_command(message: 'TextMessage', bot: 'Telebot') -> None:
    """
    Команда бота /history - выводит последние 10 команд с результатами

    Если таблица не найдена или данных нет, то выводит соответствующее сообщение

    :param bot: Бот
    :param message: сообщение пользователя
    :return: None
    """

    try:  # Все хорошо - последние 10 результатов
        with sqlite3.connect('TooEasyTravel.db') as sqlite_connection:
            cursor = sqlite_connection.cursor()

            sqlite_select = """SELECT * FROM history ORDER BY command_id DESC LIMIT 10"""
            for command_info in cursor.execute(sqlite_select):
                bot.send_message(message.chat.id, f'{command_info[2]} {command_info[1]} {command_info[3]}')

    except sqlite3.OperationalError:  # Если таблицы нет
        bot.send_message(message.chat.id, 'История пустая')

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
