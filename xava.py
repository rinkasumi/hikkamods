# meta developer: @ghosvxmodules

import asyncio
import random
from telethon.errors import FloodWaitError
from telethon.tl import functions  
from .. import loader, utils  

def format_time(seconds):
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    parts = []
    if days > 0:
        parts.append(f"{days} дн.")
    if hours > 0:
        parts.append(f"{hours} ч.")
    if minutes > 0:
        parts.append(f"{minutes} мин.")
    if seconds > 0 or not parts:
        parts.append(f"{seconds} сек.")
    return ' '.join(parts)

@loader.tds
class AvaFlood(loader.Module):
    """дрочь аватарками"""
    strings = {"name": "AvaFlood"}

    def __init__(self):
        self.ava_count = 0
        self.stop_flag = False

    @loader.command()
    async def xava(self, message):
        """<stop/resume/change>"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "🩻 Ожидайте, скачиваем вашу аватарку...")
            await self.get_self_avatar(message)
            await utils.answer(message, "🔶 Начинаю установку аватарок...")
            asyncio.create_task(self.ava_loop(message))
        elif args == 'stop':
            self.stop_flag = True
            await utils.answer(message, "🚫 Процесс установки аватарок заморожен.")
        elif args == 'resume':
            self.stop_flag = False
            await utils.answer(message, "▶️ Процесс установки аватарок возобновлен.")
        elif args == 'change':
            self.stop_flag = True
            await utils.answer(message, "🔄 Смена аватарки... Ожидайте.")
            path = await self.download_media(message)
            if path:
                await utils.answer(message, "🔄 Аватарка изменена. Продолжаем установку аватарок.")
                self.stop_flag = False
            else:
                await utils.answer(message, "⚠️ Не удалось скачать медиа. Ответьте на сообщение с медиа.")
                self.stop_flag = False
        else:
            await utils.answer(message, "❌ Неверная команда. Используйте: stop, resume или change.")

    async def ava_loop(self, message):
        while True:
            if self.stop_flag:
                await asyncio.sleep(1)
                continue

            for _ in range(5):
                try:
                    await self.set_profile_photo(message, 'ava.jpg')
                    self.ava_count += 1
                    await utils.answer(message, f"❤ Установлено аватарок: {self.ava_count}")
                    await asyncio.sleep(3)
                except FloodWaitError as e:
                    wait_time = e.seconds
                    formatted_time = format_time(wait_time)
                    await utils.answer(message, f"🚫 Тебя ебнуло! Продолжим через {formatted_time}...")
                    await asyncio.sleep(wait_time)

            await asyncio.sleep(random.randint(60, 120))

    async def download_media(self, message):
        reply = await message.get_reply_message()
        if reply and reply.media:
            path = await message.client.download_media(reply, 'ava.jpg')
            return path
        return None

    async def get_self_avatar(self, message):
        chat = await message.client.get_me()
        photos = await message.client.get_profile_photos(chat)
        if photos:
            photo = photos[0]
            file_path = await message.client.download_media(photo, 'ava.jpg')
            return file_path
        else:
            await utils.answer(message, "Ирод у тебя нету аватарки!")
            return None

    async def set_profile_photo(self, message, photo_path):
        await message.client(functions.photos.UploadProfilePhotoRequest(
            file=await message.client.upload_file(photo_path)
        ))
