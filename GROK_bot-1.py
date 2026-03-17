#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔══════════════════════════════════════════════╗
║         ELARABY AI BOT - Telegram Bot        ║
║         Python Version                       ║
║         Developer: TAREK ELARABY             ║
║         Telegram:  @offline_f_orever         ║
║         مبني على نموذج GROK Ai              ║
╚══════════════════════════════════════════════╝
"""

import json
import logging
import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

# ─────────────────────────────────────────────
#              الإعدادات الرئيسية
# ─────────────────────────────────────────────

VISCO = "7571549731:AAEMeDq7mq9n2Z8_hdHOVa4Xj54zpteJ0-g"        # ← ضع توكن البوت هنا
APIVD = "https://viscodev.x10.mx/GROK/api.php"

bot = telebot.TeleBot(VISCO)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
#         دالة إرسال الطلب لـ GROK AI
# ─────────────────────────────────────────────

def send_api_request(message: str) -> dict:
    """إرسال رسالة المستخدم إلى خادم GROK AI"""
    full_url = f"{APIVD}?message={requests.utils.quote(message)}"
    headers = {
        "Accept": "application/json",
        "User-Agent": "TelegramBot/1.0"
    }
    try:
        response = requests.get(full_url, headers=headers, timeout=30, verify=False)
        return {
            "response": response.text,
            "http_code": response.status_code,
            "error": ""
        }
    except requests.exceptions.RequestException as e:
        return {
            "response": "",
            "http_code": 0,
            "error": str(e)
        }


# ─────────────────────────────────────────────
#         معالجة رد الذكاء الاصطناعي
# ─────────────────────────────────────────────

def process_with_ai(text: str) -> dict:
    """إرسال النص لـ GROK AI واسترجاع الرد"""
    result = send_api_request(text)

    if result["http_code"] == 200:
        try:
            return json.loads(result["response"])
        except json.JSONDecodeError:
            return {"success": False, "error": "خطأ في تحليل رد الخادم"}

    # تسجيل الأخطاء في ملف
    error_log = (
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} "
        f"- HTTP: {result['http_code']} "
        f"- Error: {result['error']} "
        f"- Response: {result['response']}\n"
    )
    try:
        with open("api_error.txt", "a", encoding="utf-8") as f:
            f.write(error_log)
    except Exception:
        pass

    return {"success": False, "error": f"فشل في الاتصال بالخادم - HTTP: {result['http_code']}"}


# ─────────────────────────────────────────────
#              لوحات المفاتيح
# ─────────────────────────────────────────────

def get_channel_button() -> InlineKeyboardMarkup:
    """زر قناة المطور"""
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📢 قناة المطور", url="https://t.me/offline_f_orever"))
    return markup


def get_start_keyboard() -> InlineKeyboardMarkup:
    """لوحة مفاتيح الترحيب"""
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📢 قناة المطور", url="https://t.me/offline_f_orever"))
    markup.add(InlineKeyboardButton("🚀 ابدأ المحادثة", callback_data="start_chat"))
    return markup


# ─────────────────────────────────────────────
#            رسالة الترحيب
# ─────────────────────────────────────────────

def send_welcome_message(chat_id: int, first_name: str):
    """إرسال رسالة الترحيب مع الصورة"""
    welcome_text = (
        f"👋 <b>أهلاً وسهلاً بك {first_name}!</b>\n\n"
        "🤖 <b>أنا ELARABY AI BOT - بوت الذكاء الاصطناعي المتقدم يعمل على نموذج GROK Ai</b>\n\n"
        "✨ <b>المميزات:</b>\n"
        "• 💬 دردشة ذكية مع الذكاء الاصطناعي\n"
        "• 🚀 معالجة سريعة ودقيقة\n\n"
        "🔍 <b>كيفية الاستخدام:</b>\n"
        "ما عليك سوى إرسال رسالة وسأرد عليك فوراً!\n\n"
        "⚡ <b>لبدء المحادثة:</b>\n"
        "اضغط على الزر أدناه أو اكتب رسالة مباشرة"
    )
    try:
        bot.send_photo(
            chat_id,
            photo="https://t.me/DL_SQ/278",
            caption=welcome_text,
            parse_mode="HTML",
            reply_markup=get_start_keyboard()
        )
    except Exception:
        bot.send_message(
            chat_id,
            welcome_text,
            parse_mode="HTML",
            reply_markup=get_start_keyboard()
        )


# ─────────────────────────────────────────────
#            معالجة أمر /start
# ─────────────────────────────────────────────

@bot.message_handler(commands=["start"])
def handle_start(message):
    first_name = message.from_user.first_name or "المستخدم"
    send_welcome_message(message.chat.id, first_name)


# ─────────────────────────────────────────────
#            معالجة الرسائل النصية
# ─────────────────────────────────────────────

@bot.message_handler(func=lambda msg: True, content_types=["text"])
def handle_message(message):
    chat_id    = message.chat.id
    message_id = message.message_id
    text       = message.text

    if not text:
        bot.reply_to(message, "⚠️ أرسل نصاً للدردشة مع ELARABY AI BOT")
        return

    # رسالة انتظار
    processing_msg = bot.reply_to(message, "⏳")
    bot.send_chat_action(chat_id, "typing")

    # الحصول على رد الذكاء الاصطناعي
    ai_response = process_with_ai(text)

    # حذف رسالة الانتظار
    try:
        bot.delete_message(chat_id, processing_msg.message_id)
    except Exception:
        pass

    # إرسال الرد
    if ai_response.get("success"):
        bot.send_message(
            chat_id,
            ai_response.get("response", ""),
            reply_to_message_id=message_id,
            parse_mode="HTML",
            reply_markup=get_channel_button()
        )
    else:
        error_msg = f"❌ <b>حدث خطأ:</b> {ai_response.get('error', 'خطأ غير معروف')}"
        bot.send_message(
            chat_id,
            error_msg,
            reply_to_message_id=message_id,
            parse_mode="HTML"
        )


# ─────────────────────────────────────────────
#          معالجة الأزرار (Callback)
# ─────────────────────────────────────────────

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id    = call.message.chat.id
    message_id = call.message.message_id
    first_name = call.from_user.first_name or "المستخدم"

    try:
        bot.delete_message(chat_id, message_id)
    except Exception:
        pass

    if call.data == "/start":
        send_welcome_message(chat_id, first_name)

    elif call.data == "start_chat":
        bot.send_message(
            chat_id,
            "💬 <b>أهلاً بك في وضع المحادثة!</b>\n\n"
            "يمكنك الآن إرسال أي رسالة وسأرد عليك.\n\n"
            "🚀 <b>اكتب رسالتك الآن...</b>",
            parse_mode="HTML",
            reply_markup=get_channel_button()
        )

    bot.answer_callback_query(call.id, "✅ تم البدء")


# ─────────────────────────────────────────────
#                 تشغيل البوت
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("🤖 ELARABY AI BOT - Python Version")
    print("👨‍💻 Developer: TAREK ELARABY")
    print("📢 Telegram: @offline_f_orever")
    print("✅ البوت يعمل الآن...")
    bot.infinity_polling()
