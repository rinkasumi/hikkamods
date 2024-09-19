# meta developer: @ghosvxmodules

import os
import requests
import yt_dlp
from mutagen.id3 import ID3, APIC, TIT2, TPE1
from mutagen.mp3 import MP3
from .. import loader, utils

@loader.tds
class SoundCloudDownloadMod(loader.Module):
    """Скачивает песенки из саундклауда."""
    strings = {"name": "SoundCloudDL"}

    @loader.command()
    async def scdl(self, message):
        """<ссылка>"""
        args = utils.get_args_raw(message)

        if not args:
            await utils.answer(message, "❌ Укажите ссылку на песню!")
            return

        if "soundcloud.com" not in args:
            await utils.answer(message, "❌ Хуевая ссылка у тя")
            return

        loading_message = await utils.answer(message, "⏳ Загружаем аудио...")

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'noplaylist': True
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(args, download=True)
                file_path = ydl.prepare_filename(info_dict).rsplit('.', 1)[0] + '.mp3'

            track_title = info_dict.get('title', 'Unknown Track')
            artist = info_dict.get('uploader', 'Unknown Artist')
            thumbnail_url = info_dict.get('thumbnail')

            if thumbnail_url:
                cover_filename = await self.download_cover_image(thumbnail_url, track_title)
                if cover_filename:
                    await self.add_metadata(file_path, cover_filename, track_title, artist)
                    os.remove(cover_filename)

            if not os.path.exists(file_path):
                await utils.answer(message, "⚠️ Ошибка: файл не был скачан.")
                return

            await message.client.send_file(message.chat_id, file_path)

            await loading_message.delete()

            os.remove(file_path)

        except Exception as e:
            await utils.answer(message, f"⚠️ Ошибка при загрузке аудио: {str(e)}")

    async def download_cover_image(self, url, track_title):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                cover_filename = f"downloads/{track_title}_cover.jpg"
                with open(cover_filename, 'wb') as f:
                    f.write(response.content)
                return cover_filename
        except Exception:
            pass
        return None

    async def add_metadata(self, mp3_filename, cover_filename, title, artist):
        try:
            audio = MP3(mp3_filename, ID3=ID3)

            if audio.tags is None:
                audio.add_tags()

            with open(cover_filename, 'rb') as albumart:
                audio.tags.add(
                    APIC(
                        encoding=3,
                        mime='image/jpeg',
                        type=3,
                        desc='Cover',
                        data=albumart.read()
                    )
                )

            audio.tags.add(TIT2(encoding=3, text=title))
            audio.tags.add(TPE1(encoding=3, text=artist))

            audio.save()
        except Exception:
            pass
