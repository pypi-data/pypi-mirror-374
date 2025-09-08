# aionvk/builders/keyboard.py

import json
from typing import Any, Dict, List, Optional, Self


class Button:
    """
    Класс-фабрика для создания словарей, представляющих кнопки VK.
    Используйте статические методы этого класса для создания кнопок.
    """

    @staticmethod
    def text(label: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Создает обычную текстовую кнопку (для reply-клавиатур)."""
        payload = payload or {"button": label}
        return {
            "action": {
                "type": "text",
                "label": label,
                "payload": json.dumps(payload, ensure_ascii=False),
            }
        }

    @staticmethod
    def callback(label: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Создает inline-кнопку с callback-событием."""
        return {
            "action": {
                "type": "callback",
                "label": label,
                "payload": json.dumps(payload, ensure_ascii=False),
            }
        }

    @staticmethod
    def open_link(label: str, link: str) -> Dict[str, Any]:
        """Создает кнопку-ссылку."""
        return {
            "action": {
                "type": "open_link",
                "label": label,
                "link": link,
            }
        }


class KeyboardBuilder:
    """
    Класс для программного создания и форматирования клавиатур VK.
    """

    def __init__(self, one_time: bool = False, inline: bool = False):
        self.one_time = one_time
        self.inline = inline
        self._buttons: List[List[Dict[str, Any]]] = []
        self._current_row: List[Dict[str, Any]] = []

    def add(self, *buttons: Dict[str, Any]) -> Self:
        self._current_row.extend(buttons)
        return self

    def row(self, *buttons: Dict[str, Any]) -> Self:
        if self._current_row:
            self._buttons.append(self._current_row)
        self._current_row = list(buttons)
        return self

    def build(self) -> Optional[str]:
        if self._current_row:
            self._buttons.append(self._current_row)
            self._current_row = []
        if not self._buttons:
            return None
        markup = {
            "one_time": self.one_time,
            "inline": self.inline,
            "buttons": self._buttons,
        }
        return json.dumps(markup, ensure_ascii=False)
