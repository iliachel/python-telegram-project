import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from dotenv import load_dotenv

# Import database functions
import database

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)

# Get bot token from environment variables
bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
if not bot_token:
    logging.error("TELEGRAM_BOT_TOKEN not found in environment variables")
    exit()

# Initialize bot and dispatcher
bot = Bot(token=bot_token)
dp = Dispatcher()

# Handler for the /start command
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    # Add user to the database
    database.add_user(message.chat.id, message.from_user.username)
    await message.reply("Hi!\nI'm your new Telegram bot.")

# Handler for all other messages
@dp.message()
async def echo_message(message: types.Message):
    # Log message to the database
    database.add_message(message.chat.id, message.from_user.username, message.text)


# Main function to start the bot
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
