import telebot
import gspread
from google.oauth2.service_account import Credentials
from telebot import types

# --- Bot sozlamalari ---
BOT_TOKEN = "7601511393:AAG1hEj3UlLPo43RSUf5iiczy4US4BnKTDY"
bot = telebot.TeleBot(BOT_TOKEN)

# --- Google Sheets ulanish ---
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("toptovar.json", scopes=SCOPES)
client = gspread.authorize(creds)

SPREADSHEET_ID = "1-14Gg1Nk2sF7SPsIgVerUC8jLTkPSh-p0XdmkNX3wag"

# --- Tugmalar ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📊 Ballarim", "📜 Ballar tarixi")
    markup.row("🛒 Xaridlarim", "🏆 Reyting")
    markup.row("🤝 Do‘st taklif qilish", "🔍 ID tekshirish")
    markup.row("💬 Fikr bildirish", "ℹ Qoidalar")
    markup.row("📞 Admin bilan bog‘lanish")
    return markup

# --- Google Drive linkini direct linkga aylantirish ---
def gdrive_direct_link(rasm_url):
    if not rasm_url:
        return None
    try:
        if "/d/" in rasm_url:
            file_id = rasm_url.split("/d/")[1].split("/")[0]
        elif "id=" in rasm_url:
            file_id = rasm_url.split("id=")[1].split("&")[0]
        else:
            return None
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    except:
        return None

# --- Start komandasi ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    telegram_id = str(message.from_user.id)
    username = message.from_user.username or "Ismsiz foydalanuvchi"
    args = message.text.split()

    if len(args) > 1:
        inviter_id = args[1]
        sheet = client.open_by_key(SPREADSHEET_ID).worksheet("Takliflar")
        sheet.append_row([str(inviter_id), telegram_id])
        bot.send_message(message.chat.id, "🤝 Siz do‘stingizning taklif havolasi orqali qo‘shildingiz!")
        bot.send_message(inviter_id, f"🎉 {message.from_user.full_name} sizning taklifingiz orqali qo‘shildi!")
        bot.send_message(message.chat.id, "📢 Bizning rasmiy guruhimizga qo‘shiling: @toptovar_and")

    sheet = client.open_by_key(SPREADSHEET_ID).worksheet("Mijozlar")
    ids = sheet.col_values(4)

    if telegram_id in ids:
        row_index = ids.index(telegram_id) + 1
        custom_id = sheet.cell(row_index, 1).value
        bot.send_message(
            message.chat.id,
            f"👋 Assalomu alaykum, @{username}!\n🆔 Sizning ID raqamingiz: {custom_id}",
            reply_markup=main_menu()
        )
    else:
        bot.reply_to(
            message,
            "❌ Sizning ID raqamingiz bazada topilmadi.\nIltimos, admin bilan bog‘laning."
        )

# --- 📊 Ballarim ---
@bot.message_handler(func=lambda message: message.text == "📊 Ballarim")
def show_points(message):
    telegram_id = str(message.chat.id)
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet("Mijozlar")
    ids = sheet.col_values(4)
    balls = sheet.col_values(6)

    if telegram_id in ids:
        index = ids.index(telegram_id)
        points = balls[index] if balls[index] else "0"
        bot.send_message(message.chat.id, f"Sizning qolgan ballaringiz: {points} 🎯")
    else:
        bot.send_message(message.chat.id, "Siz ro'yxatdan o'tmagansiz.")

# --- 📜 Ballar tarixi ---
@bot.message_handler(func=lambda message: message.text == "📜 Ballar tarixi")
def show_points_history(message):
    telegram_id = str(message.chat.id)
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet("Mijozlar")
    ids = sheet.col_values(4)

    if telegram_id in ids:
        index = ids.index(telegram_id) + 1
        buyurtma_ball = sheet.cell(index, 7).value or "0"
        dost_ball = sheet.cell(index, 8).value or "0"
        bonus_ball = sheet.cell(index, 10).value or "0"
        jami_ball = sheet.cell(index, 11).value or "0"
        foyd_ball = sheet.cell(index, 12).value or "0"
        qolg_ball = sheet.cell(index, 6).value or "0"

        text = (
            "📜 *Ballar tarixi:*\n\n"
            f"📦 Buyurtma uchun ballar: *{buyurtma_ball}*\n"
            f"👥 Do‘st qo‘shish ballari: *{dost_ball}*\n"
            f"🎁 Bonus ballar: *{bonus_ball}*\n"
            f"🏆 Jami ballar: *{jami_ball}*\n"
            f"❌ Foydalanilgan ballar: *{foyd_ball}*\n"
            f"🎯 Qolgan ballar: *{qolg_ball}*"
        )
        bot.send_message(message.chat.id, text, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "❌ Siz ro'yxatdan o'tmagansiz.")

# --- 📞 Admin bilan bog‘lanish ---
@bot.message_handler(func=lambda message: message.text == "📞 Admin bilan bog‘lanish")
def contact_admin(message):
    bot.send_message(message.chat.id, "📞 Admin bilan bog‘lanish: @Toptovaradmin")

# --- 🛒 Xaridlarim ---
@bot.message_handler(func=lambda message: message.text in ["🛒 Xaridlarim", "/xaridlarim"])
def xaridlarim_handler(message):
    markup = types.InlineKeyboardMarkup()
    statuses = ["🇨🇳 Xitoyda", "🚚 Yo'lda", "Yetib kelgan", "Tamomlangan", "Bekor qilingan"]
    for status in statuses:
        markup.add(types.InlineKeyboardButton(status, callback_data=f"status_{status}"))
    bot.send_message(message.chat.id, "Qaysi holatdagi buyurtmalarni ko‘rmoqchisiz?", reply_markup=markup)

# --- Callbacklar, Reyting, Taklif, Feedback va Qoidalar ---
# ... (Sizning qolgan kodlar o‘zgarmaydi) ...

# --- Botni ishga tushirish ---
if __name__ == "__main__":
    print("Bot ishga tushdi...")
    bot.polling(none_stop=True)
