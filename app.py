from flask import Flask, request
import requests
import os

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

# -------------------------
# Webhook verification
# -------------------------
@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Verification failed", 403


# -------------------------
# Receive messages
# -------------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    try:
        entry = data["entry"][0]
        change = entry["changes"][0]
        value = change["value"]

        # Ignore status updates
        if "messages" not in value:
            return "ok", 200

        msg = value["messages"][0]
        sender = msg.get("from")

        # Prevent bot replying to itself
        if sender == PHONE_NUMBER_ID:
            return "ok", 200

        # Handle non-text messages
        if msg.get("type") != "text":
            send_message(sender, "❌ Please send text only.\nType *menu* to see options.")
            return "ok", 200

        text = msg["text"]["body"].strip().lower()

        # -------------------------
        # Chatbot logic
        # -------------------------
        if text in ["hi", "hello", "menu"]:
            reply = (
                "👋 Welcome!\n\n"
                "Reply with:\n"
                "1️⃣ Appointments\n"
                "2️⃣ Timings\n"
                "3️⃣ Location"
            )

        elif text == "1":
            reply = (
                "📅 Appointment Booking\n\n"
                "Send your *Name* and *Date*.\n"
                "Example:\n"
                "Ali – 25 Sept"
            )

        elif text == "2":
            reply = (
                "⏰ Timings:\n"
                "Monday – Saturday\n"
                "10:00 AM – 8:00 PM"
            )

        elif text == "3":
            reply = (
                "📍 Location:\n"
                "ABC Clinic\n"
                "Main Road, Karachi"
            )

        else:
            reply = "❌ Invalid option.\nType *menu* to see options."

        send_message(sender, reply)

    except Exception as e:
        print("Error:", e)

    return "ok", 200


# -------------------------
# Send WhatsApp message
# -------------------------
def send_message(to, text):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    requests.post(url, headers=headers, json=payload)


# -------------------------
# Railway entry point
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
