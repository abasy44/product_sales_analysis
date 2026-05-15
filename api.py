from flask import Flask, request, jsonify

app = Flask(__name__)

# دي "البوابة" اللي هتستقبل البيانات
@app.route('/webhook', methods=['POST'])
def receive_data():
    # بنحاول ناخد البيانات اللي مبعوتة (زي رسالة واتساب أو تنبيه من الـ Status Checker)
    data = request.json
    
    if data:
        print(f"Received Data: {data}")
        # هنا مستقبلاً هنضيف كود الإرسال لـ Google Sheets
        return jsonify({"status": "success", "message": "Data received!"}), 200
    else:
        return jsonify({"status": "error", "message": "No data found"}), 400

if __name__ == '__main__':
    # تشغيل السيرفر في وضع التطوير
    app.run(debug=True, port=5000)
