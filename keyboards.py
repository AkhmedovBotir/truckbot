from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from typing import List, Dict, Any

class Keyboards:
    @staticmethod
    def main_menu() -> ReplyKeyboardMarkup:
        """Oddiy foydalanuvchilar uchun asosiy menyu"""
        keyboard = [
            [KeyboardButton("🔍 Trek kodini tekshirish"), KeyboardButton("💱 Valyuta kursi")],
            [KeyboardButton("👤 Mening profilim")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    @staticmethod
    def admin_menu() -> ReplyKeyboardMarkup:
        """Admin menyusi"""
        keyboard = [
            [KeyboardButton("💱 Valyuta konverteri"), KeyboardButton("👥 Foydalanuvchilar")],
            [KeyboardButton("📦 Trek kod"), KeyboardButton("📢 Kanallar")],
            [KeyboardButton("📊 Statistika"), KeyboardButton("📤 Eksport")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    @staticmethod
    def currency_converter_menu() -> InlineKeyboardMarkup:
        """Valyuta konverteri pastki menyusi"""
        keyboard = [
            [InlineKeyboardButton("💰 Valyuta tanlash", callback_data="choose_currency")],
            [InlineKeyboardButton("⏰ Yuborish vaqtini belgilash", callback_data="set_send_time")],
            [InlineKeyboardButton("📝 Post shabloni", callback_data="post_template")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="back_admin")]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def currency_list(currencies: List[Dict[str, str]]) -> InlineKeyboardMarkup:
        """Valyuta tanlash klaviaturasini yaratish"""
        keyboard = []
        for i in range(0, len(currencies), 2):
            row = []
            for j in range(2):
                if i + j < len(currencies):
                    curr = currencies[i + j]
                    row.append(InlineKeyboardButton(
                        f"{curr['code']} - {curr['name'][:15]}...",
                        callback_data=f"select_currency_{curr['code']}"
                    ))
            keyboard.append(row)
        
        keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="currency_converter")])
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def phone_request() -> ReplyKeyboardMarkup:
        """Telefon raqamini so'rash klaviaturasi"""
        keyboard = [[KeyboardButton("📱 Telefon raqamini ulashish", request_contact=True)]]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    @staticmethod
    def cancel_keyboard() -> ReplyKeyboardMarkup:
        """Operatsiyani bekor qilish klaviaturasi"""
        keyboard = [[KeyboardButton("❌ Bekor qilish")]]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    @staticmethod
    def back_to_admin() -> InlineKeyboardMarkup:
        """Admin menyusiga qaytish tugmasi"""
        keyboard = [[InlineKeyboardButton("🔙 Admin menyusiga qaytish", callback_data="back_admin")]]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def confirm_keyboard() -> InlineKeyboardMarkup:
        """Tasdiqlash klaviaturasi"""
        keyboard = [
            [InlineKeyboardButton("✅ Tasdiqlash", callback_data="confirm")],
            [InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel")]
        ]
        return InlineKeyboardMarkup(keyboard)

keyboards = Keyboards()