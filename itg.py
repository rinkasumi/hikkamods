# meta developer: @ghosvxmodules

import os
import subprocess
from .. import loader, utils

@loader.tds
class ImgToGifMod(loader.Module):
    """Делает смишнявки ( гифки ) с фоточек """
    strings = {"name": "ImgToGif"}

    @loader.command()
    async def itg(self, message):
        """(ответ на фото)"""
        reply = await message.get_reply_message()

        if not reply or not reply.media:
            await utils.answer(message, "❌ Ответьте на сообщение с фотографией!")
            return

        try:
            photo = await message.client.download_media(reply, "downloads/photo.jpg")
        except Exception as e:
            await utils.answer(message, f"⚠️ Ошибка при загрузке фотографии: {str(e)}")
            return

        if not photo or not os.path.exists(photo):
            await utils.answer(message, "⚠️ Не удалось скачать фото.")
            return

        video_path = "downloads/photo.mp4"

        ffmpeg_command = [
            'ffmpeg', '-loop', '1', '-i', photo, '-c:v', 'libx264', '-t', '2', '-pix_fmt', 'yuv420p',
            '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2', video_path, '-y'
        ]

        try:
            subprocess.run(ffmpeg_command, check=True)

            await message.client.send_file(message.chat_id, video_path)

            os.remove(photo)
            os.remove(video_path)

        except subprocess.CalledProcessError as e:
            await utils.answer(message, f"⚠️ Ошибка при конвертации фото в видео: {str(e)}")
            return

