#!/bin/bash

uvicorn main:app --host 0.0.0.0 --port 8002 &
python telegram_bot.py
