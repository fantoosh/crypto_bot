import os
from dotenv import load_dotenv

load_dotenv()

# Application
MAXIMUM_CONFIRMATION_CHECKS = 20
MINIMUM_CONFIRMATIONS = 10

BASE_URL = 'https://api-testnet.bscscan.com/api'
BANK_PROTOCOL = 'https'
BOT_ACCOUNT_NUMBER = '0xBF4a6C8dB939469fccA37a1EB76055bA8B7beaF8'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/50.0.2661.102 Safari/537.36'}


# Discord
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Mongo
MONGO_DB_NAME = 'discord-db'
MONGO_HOST = 'mongodb+srv://mute:Avalon74@cluster0.fptsg.mongodb.net/test'
MONGO_PORT = 27017

# blockchain
API_KEY = os.getenv('API_KEY')
