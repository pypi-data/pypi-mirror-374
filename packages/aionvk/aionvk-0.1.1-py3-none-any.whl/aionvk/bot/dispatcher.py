import inspect
import logging
from functools import partial
from typing import Any, Callable, Dict

from pydantic import ValidationError

from ..types import Callback, Message, VKEvent
from .middleware import BaseMiddleware
from .router import Router

logger = logging.getLogger(__name__)


class Dispatcher:
    """
    Главный диспетчер. Управляет роутерами, middleware и обработкой событий.
    """

    def __init__(self):
        self.router = Router()
        self.middlewares: list[BaseMiddleware] = []

    def include_router(self, router: Router):
        self.router.handlers.extend(router.handlers)

    def register_middleware(self, middleware: BaseMiddleware):
        self.middlewares.append(middleware)

    async def _trigger_event(self, event: VKEvent, data: Dict[str, Any]) -> None:
        """
        Основной метод, который ищет и вызывает подходящий обработчик.
        """
        for handler in self.router.handlers:
            if handler.filters and not await handler.filters[0].check(event, **data):
                continue

            await self._call_handler(handler.callback, event, **data)
            return

    @staticmethod
    async def _call_handler(callback: Callable[..., Any], event: VKEvent, **data: Any):
        """
        Анализирует сигнатуру функции-обработчика и передает
        в нее только те аргументы, которые она ожидает.
        """
        signature = inspect.signature(callback).parameters
        args_to_pass: Dict[str, Any] = {}

        available_deps = data.copy()
        available_deps["event"] = event

        for param_name, param in signature.items():
            if param_name in available_deps:
                args_to_pass[param_name] = available_deps[param_name]
                continue

            if param.annotation is not inspect.Parameter.empty:
                for dep_value in available_deps.values():
                    if isinstance(dep_value, param.annotation):
                        args_to_pass[param_name] = dep_value
                        break

        await callback(**args_to_pass)

    async def feed_raw_event(self, event_data: Dict[str, Any], **kwargs: Any) -> None:
        """
        Точка входа. Принимает сырое событие от VK, парсит его
        и запускает цепочку обработки.
        """
        event_type = event_data.get("type")
        event_obj: VKEvent

        try:
            if event_type == "message_new":
                event_obj = Message.model_validate(event_data["object"])
            elif event_type == "message_event":
                event_obj = Callback.model_validate(event_data["object"])
            else:
                logger.debug("Ignored unknown event type: %s", event_type)
                return
        except ValidationError as e:
            logger.warning(
                "Failed to validate VK event. Type: %s, Error: %s, Data: %s",
                event_type,
                e,
                event_data,
            )
            return
        except Exception as e:
            logger.error(
                "An unexpected error occurred during event parsing. Type: %s, Error: %s",
                event_type,
                e,
                exc_info=True,
            )
            return

        handler_to_call = self._trigger_event

        for middleware in reversed(self.middlewares):
            handler_to_call = partial(middleware, handler_to_call)

        context_data = kwargs.copy()

        try:
            await handler_to_call(event=event_obj, data=context_data)
        except Exception as e:
            logger.exception("Exception raised during event processing: %s", e)
