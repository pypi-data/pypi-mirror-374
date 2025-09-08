# aionvk

[![PyPI - Version](https://img.shields.io/pypi/v/aionvk)](https://pypi.org/project/aionvk/)
[![Python Versions](https://img.shields.io/pypi/pyversions/aionvk.svg)](https://pypi.org/project/aionvk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📦 Установка

```bash
pip install aionvk
```

##  quickstart Быстрый старт: Эхо-бот за 1 минуту

Этот простой бот будет отвечать на любое текстовое сообщение, отправляя его обратно пользователю.

```python
# echo_bot.py
import asyncio
import os

from aiohttp import web
from dotenv import load_dotenv

from aionvk import Bot, Dispatcher, F, Router
from aionvk.types import Message

load_dotenv()

# Замените на ваши данные в .env файле
VK_TOKEN = os.getenv("VK_BOT_TOKEN")
VK_SECRET = os.getenv("VK_CALLBACK_SECRET")
VK_CONFIRMATION_TOKEN = os.getenv("VK_CALLBACK_CONFIRMATION_TOKEN")

# 1. Инициализация компонентов
router = Router()
bot = Bot(token=VK_TOKEN)
dp = Dispatcher()

# 2. Создание обработчика
@router.message(F.text) # Сработает на любое сообщение с текстом
async def echo_handler(event: Message, bot: Bot):
    await bot.send_message(
        peer_id=event.peer_id,
        text=f"Вы написали: {event.text}"
    )

# 3. Настройка веб-сервера для Callback API
async def handle_vk_callback(request: web.Request):
    data = await request.json()
    if data.get("secret") != VK_SECRET: return web.Response(status=403)
    if data.get("type") == "confirmation": return web.Response(text=VK_CONFIRMATION_TOKEN)
    
    # Передаем событие и объект бота в диспетчер
    asyncio.create_task(dp.feed_raw_event(data, bot=bot))
    return web.Response(text="ok")

async def main():
    dp.include_router(router) # Регистрируем наши обработчики
    
    app = web.Application()
    app.router.add_post("/callback", handle_vk_callback)
    
    # Не забудьте закрыть сессию бота при выходе
    app.on_shutdown.append(lambda _: bot.close())

    await web.run_app(app, host='localhost', port=8080)

if __name__ == "__main__":
    asyncio.run(main())
```

## ✨ Примеры использования

### Клавиатуры и Callback-кнопки

`aionvk` позволяет легко создавать inline-клавиатуры.

```python
from aionvk import KeyboardBuilder, Button, F
from aionvk.types import Message, Callback

router = Router()

@router.message(F.text.lower() == "/start")
async def start_with_keyboard(event: Message, bot: Bot):
    kb = KeyboardBuilder(inline=True)
    kb.add(Button.callback("Нажми меня!", payload={"cmd": "button_pressed"}))
    
    await bot.send_message(
        peer_id=event.peer_id,
        text="Это кнопка!",
        keyboard=kb.build()
    )

@router.callback(F.payload["cmd"] == "button_pressed")
async def button_handler(event: Callback, bot: Bot):
    # Убираем "часики" и показываем уведомление
    await bot.show_snackbar(event, text="Кнопка была нажата!")
```

### Машина Состояний (FSM)

Создавайте сложные диалоги с помощью `StatesGroup` и `FSMContext`.

```python
from aionvk.bot.fsm import FSMContext, State, StatesGroup

class Registration(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()

@router.message(F.text.lower() == "/reg")
async def start_registration(event: Message, state: FSMContext, bot: Bot):
    await state.set_state(Registration.waiting_for_name)
    await bot.send_message(event.peer_id, "Введите ваше имя:")

@router.message(state=Registration.waiting_for_name)
async def name_entered(event: Message, state: FSMContext, bot: Bot):
    await state.update_data(name=event.text)
    await state.set_state(Registration.waiting_for_age)
    await bot.send_message(event.peer_id, "Отлично! Теперь введите ваш возраст:")

@router.message(state=Registration.waiting_for_age)
async def age_entered(event: Message, state: FSMContext, bot: Bot):
    if not event.text.isdigit():
        return await bot.send_message(event.peer_id, "Возраст должен быть числом!")
        
    user_data = await state.get_data()
    name = user_data.get("name")
    age = event.text
    
    await bot.send_message(event.peer_id, f"Регистрация завершена!\nИмя: {name}, Возраст: {age}")
    await state.clear()
```

## 🗺️ Дальнейшие планы

*   **Тестирование:** Покрытие кода юнит-тестами для обеспечения стабильности.
*   **Расширение API:** Добавление поддержки других типов событий, загрузки фото и т.д.
*   **Документация:** Создание полноценной документации по всем компонентам.

## 🤝 Участие в разработке

Проект находится на ранней стадии. Любые предложения, сообщения об ошибках (issues) и pull-реквесты приветствуются!

## 📜 Лицензия

Проект распространяется под лицензией MIT.