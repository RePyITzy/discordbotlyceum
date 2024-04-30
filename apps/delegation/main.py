from discord.ui import Button, View
from discord.ext import commands

import discord, datetime
import logging
import random
import os


class Delegation(commands.Bot):
    def __init__(self):
        commands.Bot.__init__(self, command_prefix='делегация.', intents=discord.Intents.all())
        self.run('MTIyNTUxMTk1ODYwMjU4NDEwNA.G-WgC9.0x2p8XJvd5WanMSP0brl6Vk9MJqN7mhIa7rgdA')

    async def on_ready(self):
        self.blocklist = {}
        
        await self.load_context_menu()

    async def load_context_menu(self):
        menu_channel = self.get_channel(1225508550382583901)
        await menu_channel.purge(limit=500)

        for index, request in enumerate(os.listdir(r'apps\delegation\requests')):
            statement = os.path.join(r'apps\delegation\requests', request, 'заявление.txt')
            
            with open(statement, encoding='utf-8') as request_file:
                button_1 = Button(label='Заполнить заявление', style=discord.ButtonStyle.green)
                button_2 = Button(label='Удалить заявление', style=discord.ButtonStyle.red)
                button_1.callback, button_2.callback = self.new_statement, self.rem_statement
                
                view = View(timeout=None)
                view.add_item(button_1)
                view.add_item(button_2)
                
                await menu_channel.send(request_file.read(), view=view)
                if (index + 1) != len(os.listdir(r'apps\delegation\requests')):
                    await menu_channel.send('ㅤ')

    async def rem_statement(self, interaction):
        parent_text = interaction.message.content
        if 'идеи/поиска' in parent_text: stype = 'запрос'
        elif 'работы' in parent_text: stype = 'работа'

        channel = await self.user_got_statement(interaction.user.id, stype)
        if channel: await channel.delete(reason='По-собственному желанию было удалено.')
        if channel: self.blocklist[interaction.user.id] = datetime.datetime.now()

    async def new_statement(self, interaction):
        if interaction.user.id in self.blocklist:
            diff = datetime.datetime.now() - self.blocklist[interaction.user.id]
            if diff.seconds >= 90: del self.blocklist[interaction.user.id]
            else: return
        
        parent_text = interaction.message.content
        if 'идеи/поиска' in parent_text: stype, path = 'запрос', '2 - поиск'
        elif 'работы' in parent_text: stype, path = 'работа', '1 - работа'

        if await self.user_got_statement(interaction.user.id, stype): return

        channel_name = stype + '-' + await self.generate_id()
        category = list(filter(lambda c: c.id == 1234069466384699433, interaction.guild.categories))[0]
        overwrites = {interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                      interaction.guild.get_role(1225517023547752599): discord.PermissionOverwrite(read_messages=True),
                      interaction.guild.get_role(1234208836374495243): discord.PermissionOverwrite(read_messages=True),
                      interaction.user: discord.PermissionOverwrite(read_messages=True)}

        params = {'name': channel_name, 'category': category, 'overwrites': overwrites,
                  'topic': f'{interaction.user.id}, {datetime.datetime.now().strftime("%d.%m.%Y")}'}
        channel = await interaction.guild.create_text_channel(**params)

        for file in ['ознакомление.txt', 'содержимое.txt']:
            with open(os.path.join(r'apps\delegation\requests', path, file), encoding='utf-8') as text:
                await channel.send(text.read())
                await channel.send('ㅤ')

        button_1 = Button(label='Опубликовать заявление', style=discord.ButtonStyle.green)
        button_2 = Button(label='Отозвать заявление', style=discord.ButtonStyle.red)
        button_1.callback, button_2.callback = self.publish_statement, self.decline_statement

        view = View(timeout=None)
        view.add_item(button_1)
        view.add_item(button_2)

        await channel.send('Ожидайте прибытия модерации для проверки. Это может занять немного времени. [<@&1234208836374495243>]', view=view)

    async def decline_statement(self, interaction):
        role = interaction.guild.get_role(1234208836374495243)
        if role not in interaction.user.roles: return
        
        await interaction.channel.delete(reason=f'Заявление было отозвано модератором: <@{interaction.user.id}>')

    async def publish_statement(self, interaction):
        role = interaction.guild.get_role(1234208836374495243)
        if role not in interaction.user.roles: return

        publicant_id = interaction.channel.topic.split(', ')[0]
        message_to_publish = None
        
        async for message in interaction.channel.history(limit=1000):
            if message.author.id != int(publicant_id): continue
            
            for reaction in message.reactions:
                users = [user async for user in reaction.users()]
                if interaction.user in users: message_to_publish = message

            if message_to_publish: break

        if not message_to_publish:
            await interaction.channel.send(f'<@{interaction.user.id}>, отметьте реакцией итогое заявление и разрешите публикацию снова.')
            return

        await self.publish(message_to_publish, interaction.channel.name)
        await interaction.channel.delete(reason=f'Заявление было исполнено модератором: <@{interaction.user.id}>')

    async def publish(self, message, statement):
        if 'работа' in statement: webhook_url = 'https://discord.com/api/webhooks/1234787694643777536/iXAVF4lfHiJCQwtBz3Wa51_hNXP9_JUt-FCIK4RSs7wyWJoXEYTkdVJ4Sb7Ie0Y87og1'
        elif 'запрос' in statement: webhook_url = 'https://discord.com/api/webhooks/1234788026501169154/2j5ehvjUQTd2QFi3uIo1aZLK9QOn6fBCK88zrZ3EFOIeEmDlVDteVv2IP8x2e9pXTu9F'
        webhook = discord.Webhook.from_url(webhook_url, client=self)

        params = {'content': message.content, 'username': message.author.name, 'avatar_url': message.author.avatar,
                  'embeds': message.embeds, 'files': [await attachment.to_file() for attachment in message.attachments]}

        await webhook.send(**params)

    async def generate_id(self):
        exist_ids = []
        
        for channel in await self.get_guild(1225508549111840831).fetch_channels():
            if channel.category and channel.category.id == 1234069466384699433:
                exist_ids.append(channel.name.split('-')[1])

        while True:
            new_id = random.randint(100000000, 999999999)
            if new_id not in exist_ids: break

        return str(new_id)

    async def user_got_statement(self, user_id, statement):
        for channel in await self.get_guild(1225508549111840831).fetch_channels():
            if statement not in channel.name: continue
            if str(user_id) not in channel.topic: continue

            return channel

        return False
    

if __name__ == '__main__':
    bot = Delegation()
