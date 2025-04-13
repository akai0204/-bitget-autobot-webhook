from flask import Flask, request, jsonify
import hmac, hashlib, time, base64, requests
import os

app = Flask(__name__)

# 讀取 Bitget API 環境變數
API_KEY = os.getenv("BITGET_API_KEY")
API_SECRET = os.getenv("BITGET_API_SECRET")
PASSPHRASE = os.getenv("BITGET_PASSPHRASE")

# 建立簽名函數
def sign(message, secret):
    return base64.b64encode(hmac.new(secret.encode(), message.encode(), hashlib.sha256).digest()).decode()

# 下單函數（用於 webhook 收到訊號時）
def send_order(side):
    url = "https://api.bitget.com/api/v2/mix/order/place-order"
    timestamp = str(int(time.time() * 1000))

    body = {
        "symbol": "ORDIUSDT",                     # ✅ 改成你要交易的幣種
        "marginCoin": "USDT",
        "size": "1",
        "side": "open_long" if side == "LONG" else "open_short",
        "orderType": "market",
        "productType": "umcbl",
        "leverage": "2"                           # ✅ 兩倍槓桿設定
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
    print("✅ Order sent:", res.text)
    return res.json()

# 接收 TradingView webhook
@app.route("/", methods=["POST"])
def webhook():
    data = request.get_data(as_text=True)
    print("📩 Received:", data)

    if "LONG" in data:
        result = send_order("LONG")
    elif "SHORT" in data:
        result = send_order("SHORT")
    else:
        result = {"msg": "Ignored"}

    return jsonify(result)

# 根目錄測試頁
@app.route("/", methods=["GET"])
def index():
    return "⚡ Bitget ORDI Bot Ready with 2x Leverage ⚡"

# 主程式入口
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
