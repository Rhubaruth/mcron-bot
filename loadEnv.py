import os
from dotenv import load_dotenv


def get_discord_token():
    load_dotenv()
    return os.getenv('DISCORD_TOKEN')
