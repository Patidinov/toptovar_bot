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

    # --- Agar taklif havolasi bilan kelsa ---
    if len(args) > 1:
        inviter_id = args[1]  # taklif qilgan odamning ID
        sheet = client.open_by_key(SPREADSHEET_ID).worksheet("Takliflar")
        sheet.append_row([str(inviter_id), telegram_id])
        bot.send_message(message.chat.id, "🤝 Siz do‘stingizning taklif havolasi orqali qo‘shildingiz!")
        bot.send_message(inviter_id, f"🎉 {message.from_user.full_name} sizning taklifingiz orqali qo‘shildi!")

        # --- Taklif orqali kirganga guruh linkini yuborish ---
        bot.send_message(message.chat.id, "📢 Bizning rasmiy guruhimizga qo‘shiling: @toptovar_and")

    # --- Mijozlar jadvalidan tekshirish ---
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet("Mijozlar")
    ids = sheet.col_values(4)  # D ustun - Telegram ID

    if telegram_id in ids:
        row_index = ids.index(telegram_id) + 1
        custom_id = sheet.cell(row_index, 1).value  # A ustun - Custom ID
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

    ids = sheet.col_values(4)   # D ustun
    balls = sheet.col_values(6) # F ustun

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
@bot.message_handler(func=lambda message: message.text == "🛒 Xaridlarim" or message.text == "/xaridlarim")
def xaridlarim_handler(message):
    markup = types.InlineKeyboardMarkup()
    statuses = ["Xitoyda", "Yo'lda", "Yetib kelgan", "Tamomlangan", "Bekor qilingan"]
    for status in statuses:
        markup.add(types.InlineKeyboardButton(status, callback_data=f"status_{status}"))
    bot.send_message(message.chat.id, "Qaysi holatdagi buyurtmalarni ko‘rmoqchisiz?", reply_markup=markup)

# --- Status bo‘yicha buyurtmalarni chiqarish ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("status_"))
def send_filtered_orders(call):
    selected_status = call.data.replace("status_", "")
    user_tg_id = str(call.from_user.id)

    mijozlar_sheet = client.open_by_key(SPREADSHEET_ID).worksheet("Mijozlar")
    mijozlar_data = mijozlar_sheet.get_all_values()

    user_custom_id = None
    for row in mijozlar_data[1:]:
        if row[3] == user_tg_id:
            user_custom_id = row[0]
            break

    if not user_custom_id:
        bot.send_message(call.message.chat.id, "❌ Siz ro‘yxatdan o‘tmagansiz.")
        return

    buyurtmalar_sheet = client.open_by_key(SPREADSHEET_ID).worksheet("Buyurtmalar")
    buyurtmalar_data = buyurtmalar_sheet.get_all_values()

    STATUS_COL = 12
    PHOTO_COL = 15

    filtered_orders = [
        row for row in buyurtmalar_data[1:]
        if len(row) > STATUS_COL and row[0] == user_custom_id and row[STATUS_COL] == selected_status
    ]

    if not filtered_orders:
        bot.send_message(call.message.chat.id, f"📦 '{selected_status}' holatidagi buyurtmangiz yo‘q.")
        return

    for order in filtered_orders:
        buyurtma_sana = order[13]
        yetib_kelgan_sana = order[14] if order[14] else "🚚 Yo‘lda"
        narx = order[5]
        kargo_narxi = order[7] if order[7] else "✈️ Yetib kelganda aniq bo‘ladi"
        umumiy_narx = order[8] if order[7] else f"{order[8]} + Kargo"
        tolangan = order[10] if order[10] else "-"
        qolgan_tolov = order[11]
        holati = order[12]
        kargo_turi = order[16]

        file_link = gdrive_direct_link(order[PHOTO_COL] if len(order) > PHOTO_COL else None)

        caption = (
            f"📅 Buyurtma sanasi: {buyurtma_sana}\n"
            f"🚚 Yetib kelgan sana: {yetib_kelgan_sana}\n"
            f"💰 Narxi: {narx}\n"
            f"📦 Kargo: {kargo_narxi}\n"
            f"🔥 Umumiy narx: {umumiy_narx}\n"
            f"✅ To‘langan: {tolangan}\n"
            f"💵 Qolgan to‘lov: {qolgan_tolov}\n"
            f"📌 Holati: {holati}\n"
            f"📮 Kargo turi: {kargo_turi}"
        )

        if file_link:
            bot.send_photo(call.message.chat.id, file_link, caption=caption, parse_mode="Markdown")
        else:
            bot.send_message(call.message.chat.id, caption, parse_mode="Markdown")

# --- 🏆 Reyting ---
@bot.message_handler(func=lambda message: message.text == "🏆 Reyting")
def show_reyting(message):
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet("Mijozlar")
    data = sheet.get_all_values()[1:]  # sarlavhasiz
    sorted_data = sorted(data, key=lambda x: int(x[10] or 0), reverse=True)  # Jami ballar

    medals = ["🥇", "🥈", "🥉"]  # 1, 2, 3 o‘rin uchun belgilar
    text = "🏆 *TOP 10 REYTING*\n\n"

    for i, row in enumerate(sorted_data[:10], 1):
        medal = medals[i-1] if i <= 3 else f"{i}."
        text += f"{medal} {i}-o‘rin   | 👤 *ID:* `{row[0]}` | 💎 *Ball:* {row[10]}\n"

    bot.send_message(message.chat.id, text, parse_mode="Markdown")

# --- 🤝 Do‘st taklif qilish ---
@bot.message_handler(func=lambda message: message.text == "🤝 Do‘st taklif qilish")
def invite_friend(message):
    bot.send_message(message.chat.id, "👥 Do‘st taklif qilish uchun ushbu havolani ulashing:\nhttps://t.me/toptovarand_bot?start=" + str(message.from_user.id))

# --- 🔍 ID tekshirish ---
@bot.message_handler(func=lambda message: message.text == "🔍 ID tekshirish")
def check_id(message):
    telegram_id = str(message.from_user.id)
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet("Mijozlar")
    ids = sheet.col_values(4)
    if telegram_id in ids:
        index = ids.index(telegram_id) + 1
        custom_id = sheet.cell(index, 1).value
        bot.send_message(message.chat.id, f"🆔 Sizning ID raqamingiz: {custom_id}")
    else:
        bot.send_message(message.chat.id, "❌ ID topilmadi.")

# Admin Telegram ID (o'zingizning ID'ingizni yozing)
ADMIN_ID = 373070131  # bu yerga o'zingizning ID'ingizni yozing

# --- 💬 Fikr bildirish ---
@bot.message_handler(func=lambda message: message.text == "💬 Fikr bildirish")
def feedback(message):
    bot.send_message(message.chat.id, "💬 Fikr yoki takliflaringizni bu yerga yozing va yuboring. Adminlar ko‘rib chiqadi.")
    bot.register_next_step_handler(message, save_feedback)

def save_feedback(message):
    # Admin ID'ga fikrni yuborish
    bot.send_message(ADMIN_ID, f"📩 Yangi fikr:\n\n{message.text}\n\n👤 Yuborgan ID: {message.from_user.id}")
    bot.send_message(message.chat.id, "✅ Fikringiz yuborildi! Rahmat.")

# --- ℹ Qoidalar ---
@bot.message_handler(func=lambda message: message.text == "ℹ Qoidalar")
def rules(message):
    bot.send_message(message.chat.id, "Yaqin orada habar qilinadi!")

print("Bot ishga tushdi...")
bot.polling(none_stop=True)