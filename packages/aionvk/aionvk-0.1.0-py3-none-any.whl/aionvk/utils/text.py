def mention_user(user_id: int, text: str) -> str:
    """
    Создает строку для упоминания пользователя.

    Пример: mention_user(1, "Павел Дуров") -> "[id1|Павел Дуров]"

    :param user_id: ID пользователя VK.
    :param text: Текст, который будет отображаться как ссылка.
    :return: Отформатированная строка упоминания.
    """
    return f"[id{user_id}|{text}]"


def mention_club(club_id: int, text: str) -> str:
    """
    Создает строку для упоминания сообщества.

    Пример: mention_club(1, "Команда ВКонтакте") -> "[club1|Команда ВКонтакте]"

    :param club_id: ID сообщества VK.
    :param text: Текст, который будет отображаться как ссылка.
    :return: Отформатированная строка упоминания.
    """
    return f"[club{club_id}|{text}]"
