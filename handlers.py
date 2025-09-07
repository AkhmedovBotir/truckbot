import csv
import io
from datetime import datetime
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode

from database import db
from currency_api import currency_api
from keyboards import keyboards
from config import ADMIN_IDS

# Conversation states
WAITING_NAME, WAITING_PHONE, WAITING_TRACK_PHONE, WAITING_TRACK_CODE = range(4)
WAITING_CURRENCY_TEMPLATE, WAITING_SEND_TIME = range(4, 6)

class BotHandlers:
    def __init__(self):
        pass

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start komandasi"""
        user_id = update.effective_user.id
        user = await db.get_user(user_id)
        
        if user:
            # Foydalanuvchi allaqachon ro'yxatdan o'tgan
            if user_id in ADMIN_IDS:
                await update.message.reply_text(
                    "👋 Xush kelibsiz, Admin!",
                    reply_markup=keyboards.admin_menu()
                )
            else:
                await update.message.reply_text(
                    f"👋 Xush kelibsiz, {user['fullname']}!",
                    reply_markup=keyboards.main_menu()
                )
        else:
            # Yangi foydalanuvchi - ro'yxatdan o'tishni boshlash
            await update.message.reply_text(
                "👋 Xush kelibsiz! Iltimos, to'liq ismingizni kiriting:",
                reply_markup=ReplyKeyboardRemove()
            )
            return WAITING_NAME

    async def handle_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ro'yxatdan o'tish paytida ism kiritishni boshqarish"""
        context.user_data['fullname'] = update.message.text
        await update.message.reply_text(
            "📱 Iltimos, telefon raqamingizni ulashing:",
            reply_markup=keyboards.phone_request()
        )
        return WAITING_PHONE

    async def handle_phone(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ro'yxatdan o'tish paytida telefon kiritishni boshqarish"""
        if update.message.contact:
            phone = update.message.contact.phone_number
        else:
            phone = update.message.text

        user_id = update.effective_user.id
        fullname = context.user_data.get('fullname', '')
        
        success = await db.add_user(user_id, fullname, phone)
        
        if success:
            if user_id in ADMIN_IDS:
                await update.message.reply_text(
                    "✅ Ro'yxatdan o'tish yakunlandi! Xush kelibsiz, Admin!",
                    reply_markup=keyboards.admin_menu()
                )
            else:
                await update.message.reply_text(
                    "✅ Ro'yxatdan o'tish yakunlandi! Botga xush kelibsiz!",
                    reply_markup=keyboards.main_menu()
                )
        else:
            await update.message.reply_text(
                "❌ Ro'yxatdan o'tish muvaffaqiyatsiz. Iltimos, qayta urinib ko'ring.",
                reply_markup=ReplyKeyboardRemove()
            )
        
        return ConversationHandler.END

    async def check_track_code(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Trek kodini tekshirish"""
        user_id = update.effective_user.id
        user = await db.get_user(user_id)
        
        if not user:
            await update.message.reply_text("❌ Iltimos, avval /start orqali ro'yxatdan o'ting")
            return

        phone = user['phone']
        user_data = await db.get_user_by_phone(phone)
        
        if user_data and user_data.get('track_code'):
            await update.message.reply_text(
                f"📦 Sizning trek kodingiz: `{user_data['track_code']}`",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await update.message.reply_text("❌ Sizning raqamingiz uchun trek kod topilmadi.")

    async def check_currency(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Valyuta kursini tekshirish"""
        currencies = await currency_api.get_available_currencies()
        
        if not currencies:
            await update.message.reply_text("❌ Valyuta ma'lumotlarini olishda xatolik. Iltimos, keyinroq urinib ko'ring.")
            return

        await update.message.reply_text(
            "💱 Valyutani tanlang:",
            reply_markup=keyboards.currency_list(currencies)
        )

    async def my_profile(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Foydalanuvchi profilini ko'rsatish"""
        user_id = update.effective_user.id
        user = await db.get_user(user_id)
        
        if not user:
            await update.message.reply_text("❌ Iltimos, avval /start orqali ro'yxatdan o'ting")
            return

        profile_text = f"""
👤 **Mening profilim**

📝 To'liq ism: {user['fullname']}
📱 Telefon: {user['phone']}
📦 Trek kod: {user.get('track_code', 'Tayinlanmagan')}
📅 Ro'yxatdan o'tgan sana: {user['reg_date'][:10]}
        """
        
        await update.message.reply_text(profile_text, parse_mode=ParseMode.MARKDOWN)

    # Admin ishlovchilari
    async def currency_converter(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Valyuta konverteri menyusi"""
        if update.effective_user.id not in ADMIN_IDS:
            await update.message.reply_text("❌ Ruxsat berilmagan.")
            return

        await update.message.reply_text(
            "💱 Valyuta konverteri sozlamalari:",
            reply_markup=keyboards.currency_converter_menu()
        )

    async def users_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Foydalanuvchilar ro'yxatini ko'rsatish"""
        if update.effective_user.id not in ADMIN_IDS:
            await update.message.reply_text("❌ Ruxsat berilmagan.")
            return

        users = await db.get_all_users()
        
        if not users:
            await update.message.reply_text("👥 Foydalanuvchilar topilmadi.")
            return

        text = "👥 **Ro'yxatdan o'tgan foydalanuvchilar:**\n\n"
        for i, user in enumerate(users[:20], 1):  # Show first 20 users
            text += f"{i}. {user['fullname']} - {user['phone']}\n"
        
        if len(users) > 20:
            text += f"\n... va yana {len(users) - 20} ta foydalanuvchi"

        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

    async def track_code_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Trek kod tayinlash"""
        if update.effective_user.id not in ADMIN_IDS:
            await update.message.reply_text("❌ Ruxsat berilmagan.")
            return

        await update.message.reply_text(
            "📦 Trek kod tayinlash uchun telefon raqamini kiriting:",
            reply_markup=keyboards.cancel_keyboard()
        )
        return WAITING_TRACK_PHONE

    async def handle_track_phone(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Trek kod tayinlash uchun telefon raqamini boshqarish"""
        if update.message.text == "❌ Bekor qilish":
            await update.message.reply_text(
                "❌ Operatsiya bekor qilindi.",
                reply_markup=keyboards.admin_menu()
            )
            return ConversationHandler.END

        phone = update.message.text
        user = await db.get_user_by_phone(phone)
        
        if not user:
            await update.message.reply_text(
                "❌ Bu telefon raqami bilan foydalanuvchi topilmadi.",
                reply_markup=keyboards.admin_menu()
            )
            return ConversationHandler.END

        context.user_data['track_phone'] = phone
        await update.message.reply_text(
            f"📦 {user['fullname']} ({phone}) uchun trek kodini kiriting:",
            reply_markup=keyboards.cancel_keyboard()
        )
        return WAITING_TRACK_CODE

    async def handle_track_code(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Trek kod tayinlashni boshqarish"""
        if update.message.text == "❌ Bekor qilish":
            await update.message.reply_text(
                "❌ Operatsiya bekor qilindi.",
                reply_markup=keyboards.admin_menu()
            )
            return ConversationHandler.END

        track_code = update.message.text
        phone = context.user_data.get('track_phone')
        
        success = await db.update_track_code(phone, track_code)
        
        if success:
            await update.message.reply_text(
                f"✅ Trek kod `{track_code}` {phone} raqamiga tayinlandi",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.admin_menu()
            )
        else:
            await update.message.reply_text(
                "❌ Trek kod tayinlashda xatolik.",
                reply_markup=keyboards.admin_menu()
            )
        
        return ConversationHandler.END

    async def statistics(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Bot statistikasini ko'rsatish"""
        if update.effective_user.id not in ADMIN_IDS:
            await update.message.reply_text("❌ Ruxsat berilmagan.")
            return

        stats = await db.get_user_stats()
        settings = await db.get_settings()
        channels = settings.get('channels', '').split(',') if settings.get('channels') else []
        
        stats_text = f"""
📊 **Bot statistikasi**

👥 Jami foydalanuvchilar: {stats['total_users']}
🟢 Faol foydalanuvchilar (30 kun): {stats['active_users']}
📢 Ulangan kanallar: {len([ch for ch in channels if ch.strip()])}
💱 Joriy valyuta: {settings.get('currency', 'USD')}
⏰ Yuborish vaqti: {settings.get('send_time', '09:00')}
        """
        
        await update.message.reply_text(stats_text, parse_mode=ParseMode.MARKDOWN)

    async def export_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Foydalanuvchilarni CSV formatida eksport qilish"""
        if update.effective_user.id not in ADMIN_IDS:
            await update.message.reply_text("❌ Ruxsat berilmagan.")
            return

        users = await db.get_all_users()
        
        if not users:
            await update.message.reply_text("👥 Eksport qilish uchun foydalanuvchilar yo'q.")
            return

        # CSV yaratish
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['To\'liq ism', 'Telefon', 'Trek kod', 'Ro\'yxatdan o\'tgan sana'])
        
        for user in users:
            writer.writerow([
                user['fullname'],
                user['phone'],
                user.get('track_code', ''),
                user['reg_date']
            ])
        
        # CSV faylini yuborish
        csv_data = output.getvalue().encode('utf-8')
        filename = f"foydalanuvchilar_eksport_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        await update.message.reply_document(
            document=io.BytesIO(csv_data),
            filename=filename,
            caption=f"📤 Foydalanuvchilar eksporti - {len(users)} ta foydalanuvchi"
        )

    # Callback ishlovchilari
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Callback so'rovlarini boshqarish"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "currency_converter":
            await query.edit_message_text(
                "💱 Valyuta konverteri sozlamalari:",
                reply_markup=keyboards.currency_converter_menu()
            )
        
        elif data == "choose_currency":
            currencies = await currency_api.get_available_currencies()
            await query.edit_message_text(
                "💰 Kunlik postlar uchun valyutani tanlang:",
                reply_markup=keyboards.currency_list(currencies)
            )
        
        elif data.startswith("select_currency_"):
            currency_code = data.replace("select_currency_", "")
            await db.update_settings(currency=currency_code)
            await query.edit_message_text(
                f"✅ Valyuta {currency_code} ga o'rnatildi",
                reply_markup=keyboards.back_to_admin()
            )
        
        elif data.startswith("show_currency_"):
            currency_code = data.replace("show_currency_", "")
            currency_data = await currency_api.get_currency_by_code(currency_code)
            
            if currency_data:
                settings = await db.get_settings()
                template = settings.get('template', '')
                message = currency_api.format_currency_info(currency_data, template)
                await query.edit_message_text(message, parse_mode=ParseMode.MARKDOWN)
            else:
                await query.edit_message_text("❌ Valyuta ma'lumotlari topilmadi.")

# Global handlers instance
handlers = BotHandlers()