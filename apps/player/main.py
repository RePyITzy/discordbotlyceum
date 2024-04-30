from discord.ext import commands
from pytube import YouTube

import discord
import nacl
import os


class Player(commands.Bot):
    def __init__(self):
        commands.Bot.__init__(self, command_prefix='проигрыватель.', intents=discord.Intents.all())
        self.run('MTIzNDgyODkyOTMyNDU0ODE0Ng.GJblqR.UvmN-hTmQcE-sEFymcMla317uu2O6K-eYj5vtM')

    async def on_message(self, message):
        if not message.content.startswith('проигрыватель.'): return
        if message.channel.id != 1234834485195833354: return
        if message.author.bot: return

        arguments = message.content.split('проигрыватель.')[1].split()
        if arguments[0] == 'поставить':
            video_url, channel_id = arguments[2], arguments[1]
            channel_id = int(channel_id.replace('<#', '').replace('>', ''))
            if 'music.mp3' in os.listdir(r'apps\player\loaded'): os.remove(os.path.join(r'apps\player\loaded', 'music.mp3'))

            video = YouTube(video_url).streams.filter(only_audio=True).first()
            downloaded_file = video.download(r'apps\player\loaded')

            os.rename(downloaded_file, os.path.join(r'apps\player\loaded', 'music.mp3'))

            vc = self.get_guild(1225508549111840831).get_channel(channel_id)
            await vc.connect()

            voice = self.voice_clients[0]
            voice.play(discord.FFmpegPCMAudio(source=r'apps\player\loaded\music.mp3', executable=rf'data\ffmpeg\bin\ffmpeg.exe'))

        elif arguments[0] == 'остановить':
            voice = self.voice_clients[0]
            voice.stop()

            await message.delete()

if __name__ == '__main__':
    Player()
