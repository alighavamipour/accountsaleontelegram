import os
import threading

from flask import Flask, request

import telebot
from telebot import types

from database import (
    get_or_create_user,
    get_setting
)


# ==========================================
# CONFIG
# ==========================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

PORT = int(os.getenv("PORT", "8080"))


if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN تنظیم نشده است.")


bot = telebot.TeleBot(
    BOT_TOKEN,
    parse_mode="HTML"
)


app = Flask(__name__)


# ==========================================
# START
# ==========================================

@bot.message_handler(commands=["start"])
def start(message):

    user = get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )

    keyboard = types.InlineKeyboardMarkup()

    keyboard.row(
        types.InlineKeyboardButton(
            "🛒 خرید سرویس",
            callback_data="buy"
        )
    )

    keyboard.row(
        types.InlineKeyboardButton(
            "📦 سرویس‌های من",
            callback_data="my_services"
        )
    )

    keyboard.row(
        types.InlineKeyboardButton(
            "📞 پشتیبانی",
            callback_data="support"
        )
    )

    welcome = get_setting(
        "welcome_text",
        "به فروشگاه ما خوش آمدید 🌹"
    )

    bot.send_message(
        message.chat.id,
        welcome,
        reply_markup=keyboard
    )


# ==========================================
# CALLBACK
# ==========================================

@bot.callback_query_handler(
    func=lambda call: True
)
def callbacks(call):

    if call.data == "buy":

        bot.answer_callback_query(
            call.id
        )

        bot.send_message(
            call.message.chat.id,
            "🛒 بخش خرید به‌زودی فعال می‌شود."
        )

    elif call.data == "my_services":

        bot.answer_callback_query(
            call.id
        )

        bot.send_message(
            call.message.chat.id,
            "📦 سرویس‌های شما\n\n"
            "فعلاً هیچ سرویسی ثبت نشده است."
        )

    elif call.data == "support":

        bot.answer_callback_query(
            call.id
        )

        support = get_setting(
            "support_username",
            ""
        )

        if support:
            bot.send_message(
                call.message.chat.id,
                f"📞 پشتیبانی:\n{support}"
            )
        else:
            bot.send_message(
                call.message.chat.id,
                "📞 پشتیبانی هنوز تنظیم نشده است."
            )


# ==========================================
# WEBHOOK
# ==========================================

@app.route("/", methods=["GET"])
def home():

    return "VPN Shop Bot is running."


@app.route(
    "/webhook",
    methods=["POST"]
)
def webhook():

    json_string = request.get_data().decode(
        "utf-8"
    )

    update = telebot.types.Update.de_json(
        json_string
    )

    bot.process_new_updates(
        [update]
    )

    return "OK"


# ==========================================
# HEALTH CHECK
# ==========================================

@app.route(
    "/health",
    methods=["GET"]
)
def health():

    return {
        "status": "ok"
    }


# ==========================================
# MAIN
# ==========================================

if __name__ == "__main__":

    bot.remove_webhook()

    app.run(
        host="0.0.0.0",
        port=PORT
    )
