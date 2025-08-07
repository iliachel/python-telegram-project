from fastapi import FastAPI
from telegram_bot import bot
from pydantic import BaseModel

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
    # In a real application, you would fetch the chat history from a database
    return [
        {'username': 'user1', 'text': 'Hello!'},
        {'username': 'user2', 'text': 'Hi there!'},
    ]
