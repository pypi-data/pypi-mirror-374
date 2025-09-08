class AionVKError(Exception):
    """Базовое исключение для всех ошибок библиотеки aionvk."""

    pass


class APIError(AionVKError):
    """
    Исключение, возникающее при ошибке со стороны VK API.

    Атрибуты:
        code (int): Код ошибки от VK API.
        msg (str): Текст ошибки от VK API.
    """

    def __init__(self, code: int, msg: str):
        self.code = code
        self.msg = msg
        super().__init__(f"VK API Error {code}: {msg}")
