from flask import Flask, request, jsonify, render_template
from transformers import pipeline

app = Flask(__name__)

# 加載 Hugging Face 的 AI 模型
try:
    ai_pipeline = pipeline("text-generation", model="facebook/opt-350m")  # 指定模型
except Exception as e:
    print(f"模型加載失敗: {e}")
    ai_pipeline = None

# 提供首頁, 搭配test1.html
@app.route('/test1')
def index():
    return render_template('test1.html')

# 處理 POST 請求
@app.route('/api/message', methods=['POST'])
def handle_message():
    # 獲取前端傳遞的訊息
    user_input = request.json.get('message', '')

    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    # 確保模型已正確加載
    if not ai_pipeline:
        return jsonify({"error": "AI 模型未加載，請檢查伺服器設定"}), 500

    # 使用 AI 模型生成回覆
    try:
        ai_response = ai_pipeline(
            user_input, max_length=50, num_return_sequences=1, truncation=True
        )
        reply = ai_response[0]['generated_text']
    except Exception as e:
        return jsonify({"error": f"生成回覆時出錯: {str(e)}"}), 500

    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True, threaded=False)  # 生產環境建議使用 WSGI (例如 gunicorn)


