from flask import Flask, request
import requests

app = Flask(__name__)

TOKEN = "7239204170:AAHNFT7BRtqN0OzXD9OD_DAfY5YJUbTq7DI"
CHAT_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwY035vYXieElReF6Eip7Zcq4hAPhJ-wN0xV1nZJJmfxXyAMNIuc8S0UlmzjVYdQ81V/exec"

CATEGORIES = {
    "еда": ["еда", "продукты", "магазин", "яйца", "овощи", "мясо"],
    "транспорт": ["такси", "автобус", "бензин", "транспорт", "поезд", "маршрутка"],
    "здоровье": ["аптека", "врач", "больница", "здоровье", "таблетки"],
    "образование": ["учёба", "школа", "книги", "репетитор", "курсы"],
    "красота и уход за собой": ["маникюр", "салон", "уход", "косметика", "краска"],
    "домашнее хозяйство": ["тряпки", "швабра", "моющее", "стирка", "хозяйство"],
    "подарки": ["подарок", "дар", "сюрприз", "поздравление"],
    "другое": []
}

def detect_category(text):
    for category, keywords in CATEGORIES.items():
        for word in keywords:
            if word in text.lower():
                return category
    return "другое"

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    print("🔔 Получен POST запрос")

    try:
        message = data["message"]["text"]
        chat_id = data["message"]["chat"]["id"]

        print(f"📩 Текст сообщения: {message}")
        print(f"👤 chat_id: {chat_id}")

        words = message.split()
        amount = next((int(s.replace("тг", "").replace("тенге", "").replace("₸", "").strip())
                      for s in words if s.replace("тг", "").replace("тенге", "").replace("₸", "").strip().isdigit()), 0)

        print(f"💰 Сумма: {amount}")

        category = detect_category(message)
        print(f"🏷 Категория: {category}")

        # Отправка в таблицу
        payload = {
            "amount": amount,
            "category": category,
            "comment": message
        }
        r1 = requests.post(SCRIPT_URL, data=payload)
        print(f"📊 Таблица ответила: {r1.status_code}")

        # Ответ пользователю
        reply = f"✅ Записала: {amount} тг — {category}"
        r2 = requests.post(CHAT_URL, json={"chat_id": chat_id, "text": reply})
        print(f"📤 Ответ пользователю отправлен: {r2.status_code}")

    except Exception as e:
        print("❌ Ошибка обработки:", e)

    return "OK", 200

@app.route("/", methods=["GET"])
def home():
    return "Сервер работает!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

