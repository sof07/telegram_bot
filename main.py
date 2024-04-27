import asyncio
import logging
from aiogram import Bot, F  # F - магический фильтр
from aiogram import Dispatcher  # слушает сообщения которые приходят в бот
from aiogram import types  # подключает типы сообщений
from aiogram.filters import CommandStart, Command
from config import TELEGRAM_TOKEN


bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()


### ОБРАБОТЧИКИ КОМАНД ###


# Обработчик команды старт
@dp.message(CommandStart())
async def start(message: types.Message):
    # message.from_user.full_name получает полное имя пользователя, если его нет получает только имя
    # которое есть всегда
    await message.answer(text=f"Привет {message.from_user.full_name}")


# Обработчик команды help
@dp.message(Command("help"))
async def help(message: types.Message):
    text = "Тестовый бот"
    await message.answer(text=text)


### МАГИЧЕСКИЕ ФИЛЬТРЫ ###


@dp.message(F.photo, ~F.caption)
# Если приходит фото с без описания (caption) тльда (~) - инвертирует условие
# F.caption - если пришло описание к фото фильтр сработает
# ~F.caption - если НЕ пришло описание к фото фильтр сработает
async def message_photo_caption(message: types.Message):
    text = "Я хочу описания фото "
    # message.caption - описание к фото
    await message.reply(text=f"{text}{message.caption}")


# Вариант с запятой это условие И, если нужно комбинировать фильты по
# условию ИЛИ используем | пример:
# F.photo | F.video - если приходит фото или видео


@dp.message(F.photo, F.caption.contains("Пожалуйста"))
# Пример фильтра по условию если в описании есть текст Пожалуйста
async def message_photo_caption_please(message: types.Message):
    text = "Фото содержит подпись "
    # message.caption - описание к фото
    await message.reply(text=f"{text}{message.caption}")


# Фильтр для сообщений с фото
@dp.message(lambda message: message.photo)
# лямбда функция возвращает True если в сообщении пришло фото
# второй вариант вместо лямбда использовать магический фильтр F.photo
# результат будет тот же
async def photo_message(message: types.Message):
    text = "Извини братишка, с фото я не работаю 🤷‍♂️"
    await message.reply(text=text)


# Фильтр сообщений для админов
@dp.message(F.from_user.id.in_({1, 2, 146708975}), F.text == "secret")
# Здесь обрабатывается два условия:
# 1 если id пользователя отправившего сообщение 1, 2, 146708975 (считаем их админами)
# 2 и сообщение от пользователя с текстом secret
async def admin_secret_message(message: types.Message):
    await message.answer(text="Привет админ!")


# Декоратор который передает в функцию входящие сообщения
@dp.message()
async def echo(message: types.Message):
    # message - сообщение которое отправил пользователь
    # Отправляет сообщение
    # chat_id в какой чат отправить сообщение
    # message.chat.id получает id чата
    # reply_to_message_id цитирует сообщение на которое отправляется ответ
    # для цитирования можно использовать await message.reply
    await bot.send_message(
        chat_id=message.chat.id, text=f"Твой id: {message.from_user.id}"
    )
    await bot.send_message(
        chat_id=message.chat.id,
        text="Тестируем бота",
        reply_to_message_id=message.message_id,
    )
    # Обработка сообщений, если сообщение текст отправляет в ответ имя пользователя
    # Отправившего сообщение, если стикер, отправляет в ответ тот же стикер
    # иначе цитирует то что отправил пользователь
    if message.text:
        # Отправляет ответ на сообщение
        await message.answer(f"Пока {message.from_user.first_name}")
    elif message.sticker:
        await message.reply_sticker(message.sticker.file_id)
        # Отвечает на сообщение т.е. с цитированием сообщения
    else:
        await message.reply(text="Нужноотправить текст")


async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
