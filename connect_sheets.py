import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 1. Google Sheets API ruxsatlari
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# 2. JSON kalit yuklash
creds = ServiceAccountCredentials.from_json_keyfile_name("toptovar.json", scope)  
client = gspread.authorize(creds)

# 3. Jadvalga ulanish (nomi bo‘yicha)
spreadsheet = client.open("Data")  # <-- bu yerga Google Sheets nomini yozing

# 4. Ma’lumot o‘qish (masalan, 1-varaqlarning hammasini olish)
sheet = spreadsheet.sheet1
data = sheet.get_all_records()

print(data)
