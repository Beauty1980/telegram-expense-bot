
from flask import Flask, request
import requests
import datetime

app = Flask(__name__)

# Токен и URL Google Apps Script
TOKEN = "7239204170:AAHNFT7BRtqN0OzXD9OD_DAfY5YJUbTq7DI"
SPREADSHEET_URL = "https://script.google.com/macros/s/AKfycbwY035vYXieElReF6Eip7Zcq4hAPhJ-wN0xV1nZJJmfxXyAMNIuc8S0UlmzjVYdQ81V/exec"

# Категории с ключевыми словами
CATEGORIES = {
    "Продукты": ["молоко", "яйца", "хлеб", "масло", "гречка", "овощи", "фрукты", "сыр", "макароны", "творог", "рыба", "мясо"],
    "Транспорт": ["такси", "маршрутка", "проезд", "бензин", "метро", "автобус"],
    "Здоровье": ["аптека", "таблетки", "витамины", "лекарства"],
    "Красота и уход за собой": ["косметика", "шампунь", "крем", "маникюр", "салон", "стрижка", "уход"],
    "Образование": ["курс", "учеба", "школа", "книга", "обучение"],
    "Домашнее хозяйство": ["порошок", "мыло", "уборка", "губки", "чистящее", "бумага", "салфетки"],
    "Подарки": ["подарок", "букет", "цветы", "праздник", "поздравление"]
}

def detect_category(text):
    text = text.lower()
    for category, keywords in CATEGORIES.items():
        if any(word in text for word in keywords):
            return category
    return "Другое"

@app.route("/", methods=["POST"])
def webhook():
    data = request.json
    message = data["message"]["text"]
    chat_id = data["message"]["chat"]["id"]

    parts = message.split()
    try:
        amount = int([word for word in parts if word.isdigit()][0])
    except (IndexError, ValueError):
        amount = 0

    category = detect_category(message)

    today = datetime.datetime.now().strftime("%Y-%m-%d")
    requests.get(SPREADSHEET_URL, params={"date": today, "amount": amount, "category": category})

    response_message = f"Записала: {amount}тг – {category}."
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": chat_id, "text": response_message})

    return "OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
