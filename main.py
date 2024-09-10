import logging
import os
import uuid

import asyncio
from typing import List

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from fastapi import FastAPI, Depends, HTTPException
from fastapi import BackgroundTasks
from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db import get_db
from app.models.channels import Channel
from app.schemas.channel import ChannelSchema, ChannelResponse
import aiohttp

# Constants for API token and FastAPI URL
API_TOKEN = os.getenv("TELEGRAM_BOT_API_TOKEN")
FASTAPI_URL = 'http://192.168.100.133:8000/user-create'

# Create FastAPI app
app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create the bot and dispatcher instances
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Function to send user data to FastAPI


async def check_subscription(user_id: int, chat_id: str):
    """Foydalanuvchining ma'lum kanal yoki guruhga a'zo ekanligini tekshirish"""
    try:
        member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logging.error(f"Error checking subscription: {e}")
        return False


async def send_user_data_to_fastapi(user_info):
    async with aiohttp.ClientSession() as session:
        async with session.post(FASTAPI_URL, json=user_info) as response:
            if response.status != 200:
                logging.error(f"Failed to send user data to FastAPI: {response.status}")
            else:
                logging.info("User data successfully sent to FastAPI")



# Handler for the /start command
@dp.message(Command("start"))
async def send_welcome(message: Message):
    # Extract user information
    user_info = {
        "telegram_id": message.from_user.id,
        "username": message.from_user.username,
        "fullname": f"{message.from_user.first_name} {message.from_user.last_name}" if message.from_user.last_name else message.from_user.first_name,
    }

    # Send user data to FastAPI
    await send_user_data_to_fastapi(user_info)

    # Logging user information
    logging.info(f"User information: {user_info}")

    # Create a reply keyboard
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="O'yinni boshlash", web_app={"url": "https://khayrullodev.uz/"})],
            [KeyboardButton(text="Kanalga obuna bo'lish")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    # Send the welcome message with the keyboard
    await message.answer(f"O'yin oynasini ochish uchun tugmani bosing:", reply_markup=keyboard)

@app.get('/get-subscribe', response_model=bool)
async def get_subscribe(user_chan: ChannelSchema, db: AsyncSession = Depends(get_db)):
    user_id = user_chan.user_id
    channel_id = user_chan.channel_id

    # Fetch the channel from the database
    result = await db.execute(
        select(Channel).where(Channel.channel_id == channel_id)
    )
    channel = result.scalar()

    if channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")

    # Call function to check subscription
    is_subscribed = await check_subscription(user_id, channel_id)

    return is_subscribed


@app.get('/list-channels', response_model=List[ChannelResponse])
async def get_channels(db: AsyncSession = Depends(get_db)):
    channels = await db.execute(select(Channel))
    channels = channels.scalars().all()
    return channels



# Startup function
@app.on_event("startup")
async def on_startup():
    logging.info("Starting bot")

    # Running the bot's polling loop in the background
    asyncio.create_task(dp.start_polling(bot))


# Healthcheck endpoint to verify if FastAPI is running
@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}


# Entry point of the script
if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)