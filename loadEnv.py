import os
from dotenv import load_dotenv


def get_discord_token():
    return os.getenv('DISCORD_TOKEN')


def get_mcrcon_pass():
    return os.getenv('MCRCON_PASSWORD')
