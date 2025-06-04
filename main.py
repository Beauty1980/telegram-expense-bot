from flask import Flask, request
import requests

app = Flask(__name__)

BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
GOOGLE_SCRIPT_URL = "YOUR_GOOGLE_APPS_SCRIPT_WEBHOOK"

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

@app.route("/", methods=["POST"])
def webhook():
    data = request.json
    chat_id = data["message"]["chat"]["id"]
    text = data["message"]["text"]

    try:
        words = text.lower().split()
        digits = [w for w in words if w.isdigit()]
        if not digits:
            send_message(chat_id, "❌ Я не нашла сумму в сообщении. Напиши, например: 'Потратила 3000 на продукты'")
            return "no amount"
        amount = int(digits[0])
        description = text
        category = "другое"

        keywords = {
            "еда": ["еда", "продукты", "магазин", "обед", "ужин", "завтрак", "фрукты", "овощи"],
            "транспорт": ["транспорт", "такси", "проезд", "автобус", "метро", "бензин", "маршрутка"],
            "одежда": ["одежда", "платье", "штаны", "куртка", "кроссовки", "обувь"],
            "подарки": ["подарок", "подарки", "поздравление"],
            "красота и уход за собой": ["маникюр", "салон", "косметика", "уход", "крем"],
            "здоровье": ["аптека", "лекарство", "врач", "здоровье", "витамины", "больница"],
            "домашнее хозяйство": ["хозтовары", "тряпки", "моющее", "порошок", "бумага"],
            "образование": ["курсы", "учеба", "школа", "репетитор", "обучение"],
            "форс-мажор": ["штраф", "поломка", "ремонт"],
        }

        for key, values in keywords.items():
            if any(word in text.lower() for word in values):
                category = key
                break

        payload = {
            "amount": amount,
            "description": description,
            "category": category
        }

        r = requests.post(GOOGLE_SCRIPT_URL, json=payload)
        if r.status_code == 200:
            send_message(chat_id, f"✅ Записала: {amount} тг — {category}")
        else:
            send_message(chat_id, "⚠️ Не удалось отправить данные в таблицу.")

    except Exception as e:
        send_message(chat_id, f"❌ Ошибка: {str(e)}")

    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
