
from flask import Flask, request
import requests
import datetime
import os

app = Flask(__name__)

# === НАСТРОЙКИ ===
TOKEN = "7239204170:AAHNFT7BRtqN0OzXD9OD_DAfY5YJUbTq7DI"
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwY035vYXieElReF6Eip7Zcq4hAPhJ-wN0xV1nZJJmfxXyAMNIuc8S0UlmzjVYdQ81V/exec"

# === КАТЕГОРИИ ДЛЯ АВТОРАСПОЗНАВАНИЯ ===
CATEGORIES = {
    "Продукты": ["молоко", "яйца", "хлеб", "сыр", "овощи", "фрукты", "гречка", "курица", "мясо", "йогурт", "макароны"],
    "Транспорт": ["бензин", "такси", "проезд", "маршрутка", "автобус", "транспорт", "метро"],
    "Здоровье": ["аптека", "лекарства", "витамины", "врач", "поликлиника", "анализы"],
    "Красота и уход": ["крем", "шампунь", "уход", "салон", "косметика", "маникюр", "маска", "уходовый"],
    "Образование": ["курс", "обучение", "учеба", "книга", "тренинг", "вебинар"],
    "Подарки": ["подарок", "цветы", "поздравление", "сюрприз"],
    "Домашнее хозяйство": ["салфетки", "губка", "моющее", "хозяйственное", "бытовая", "вёдро", "швабра", "перчатки"]
}

# === ФУНКЦИЯ РАСПОЗНАВАНИЯ КАТЕГОРИИ ===
def detect_category(text):
    text = text.lower()
    for category, keywords in CATEGORIES.items():
        if any(keyword in text for keyword in keywords):
            return category
    return "Другое"

# === ФУНКЦИЯ ОБРАБОТКИ СООБЩЕНИЯ ===
def process_message(text):
    parts = text.strip().split()
    if len(parts) < 2:
        return "Пожалуйста, укажи сумму и описание, например: 1200 яйца"

    try:
        amount = int(parts[0])
        description = " ".join(parts[1:])
        category = detect_category(description)
        date = datetime.datetime.now().strftime("%d.%m.%Y")

        data = {
            "date": date,
            "amount": amount,
            "description": description,
            "category": category
        }

        requests.post(GOOGLE_SCRIPT_URL, data=data)

        if category == "Другое":
            return f"Записала: {amount}тг — '{description}' (категория не определена, отнесено в 'Другое')"
        return f"Записала: {amount}тг — '{description}' в категорию '{category}'"

    except ValueError:
        return "Не удалось распознать сумму. Пример ввода: 2000 хлеб"

# === ОСНОВНОЙ МАРШРУТ ===
@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        response = process_message(text)
        send_message(chat_id, response)
    return "OK"

# === ОТПРАВКА СООБЩЕНИЯ В ТЕЛЕГРАМ ===
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

# === СТАРТ СЕРВЕРА ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
