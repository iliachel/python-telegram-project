from fastapi import FastAPI
from telegram_bot import bot
from pydantic import BaseModel

# Import database functions
import database

app = FastAPI()

class Message(BaseModel):
    user_id: int
    text: str

@app.post("/send_message")
async def send_message(message: Message):
    await bot.send_message(chat_id=message.user_id, text=message.text)
    return {"status": "success"}

@app.get("/chat_history")
async def get_chat_history():
    return database.get_chat_history()

@app.get("/users")
async def get_users():
    return database.get_all_users()
