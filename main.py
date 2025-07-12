# This example requires the 'message_content' intent.

import discord
from loadEnv import get_discord_token

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
DC_TOKEN = get_discord_token()


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


client.run(DC_TOKEN)
