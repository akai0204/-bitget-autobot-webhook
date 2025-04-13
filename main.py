from flask import Flask, request, jsonify
import hmac, hashlib, time, base64, requests
import os

app = Flask(__name__)

API_KEY = os.getenv("BITGET_API_KEY")
API_SECRET = os.getenv("BITGET_API_SECRET")
PASSPHRASE = os.getenv("BITGET_PASSPHRASE")

def sign(message, secret):
    return base64.b64encode(hmac.new(secret.encode(), message.encode(), hashlib.sha256).digest()).decode()

def send_order(side):
    url = "https://api.bitget.com/api/v2/mix/order/place-order"
    timestamp = str(int(time.time() * 1000))
    
    body = {
        "symbol": "ADAUSDT",
        "marginCoin": "USDT",
        "size": "1",
        "side": "open_long" if side == "LONG" else "open_short",
        "orderType": "market",
        "productType": "umcbl"
    }

    body_json = str(body).replace("'", '"')
    to_sign = timestamp + "POST" + "/api/v2/mix/order/place-order" + body_json
    signature = sign(to_sign, API_SECRET)

    headers = {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": PASSPHRASE,
        "Content-Type": "application/json"
    }

    res = requests.post(url, headers=headers, json=body)
    print("Order sent:", res.text)
    return res.json()

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_data(as_text=True)
    print("Received:", data)

    if "LONG" in data:
        result = send_order("LONG")
    elif "SHORT" in data:
        result = send_order("SHORT")
    else:
        result = {"msg": "Ignored"}

    return jsonify(result)

@app.route("/", methods=["GET"])
def index():
    return "⚡ Bitget Autobot Ready ⚡"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
