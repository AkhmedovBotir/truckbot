from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from typing import List, Dict, Any

class Keyboards:
    @staticmethod
    def main_menu() -> ReplyKeyboardMarkup:
        """Oddiy foydalanuvchilar uchun asosiy menyu"""
        keyboard = [
            [KeyboardButton("🔍 Trek kodini tekshirish")],
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
            [InlineKeyboardButton("🚀 Test yuborish", callback_data="test_send")],
            [InlineKeyboardButton("📅 Rejani tekshirish", callback_data="check_schedule")],
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

    @staticmethod
    def currency_selection_keyboard(currencies: List[Dict[str, str]], selected_currencies: List[str] = None) -> InlineKeyboardMarkup:
        """Valyuta tanlash klaviaturasi (checkbox'lar bilan)"""
        if selected_currencies is None:
            selected_currencies = []
        
        keyboard = []
        for i in range(0, len(currencies), 2):
            row = []
            for j in range(2):
                if i + j < len(currencies):
                    curr = currencies[i + j]
                    is_selected = curr['code'] in selected_currencies
                    checkbox = "☑️" if is_selected else "☐"
                    row.append(InlineKeyboardButton(
                        f"{checkbox} {curr['code']} - {curr['name'][:15]}...",
                        callback_data=f"toggle_currency_{curr['code']}"
                    ))
            keyboard.append(row)
        
        keyboard.append([InlineKeyboardButton("✅ Saqlash", callback_data="save_currencies")])
        keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="currency_converter")])
        return InlineKeyboardMarkup(keyboard)


    @staticmethod
    def test_send_keyboard() -> InlineKeyboardMarkup:
        """Test yuborish klaviaturasi"""
        keyboard = [
            [InlineKeyboardButton("🚀 Hozir yuborish (Test)", callback_data="test_send")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="currency_converter")]
        ]
        return InlineKeyboardMarkup(keyboard)


    @staticmethod
    def user_currencies_keyboard(selected_currencies: List[str]) -> InlineKeyboardMarkup:
        """Foydalanuvchilar uchun valyuta klaviaturasi"""
        keyboard = [
            [InlineKeyboardButton("📊 Barcha valyutalarni ko'rish", callback_data="show_all_currencies")]
        ]
        
        # Add individual currency buttons as well
        for i in range(0, len(selected_currencies), 2):
            row = []
            for j in range(2):
                if i + j < len(selected_currencies):
                    curr_code = selected_currencies[i + j]
                    row.append(InlineKeyboardButton(
                        curr_code,
                        callback_data=f"show_currency_{curr_code}"
                    ))
            keyboard.append(row)
        
        keyboard.append([InlineKeyboardButton("🔙 Asosiy menyu", callback_data="back_main")])
        return InlineKeyboardMarkup(keyboard)

keyboards = Keyboards()