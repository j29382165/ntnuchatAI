from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from transformers import pipeline
from datetime import datetime
from multiprocessing import freeze_support
import uuid
import torch

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:ROOTROOT@localhost/chat_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 定義資料庫模型
class Conversation(db.Model):
    __tablename__ = 'conversations'

    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    conversation_id = db.Column(db.String(36), db.ForeignKey('conversations.id'), nullable=False)
    sender = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'sender': self.sender,
            'message': self.message,
            'timestamp': self.timestamp
        }

class ModelConfig:
    def __init__(self):
        self.device = self.get_device()
        self.model = None
        self.pipeline = None

    def get_device(self, force_cpu=False):
        if force_cpu:
            return torch.device("cpu")
        if torch.backends.mps.is_available():
            return torch.device("mps")
        return torch.device("cpu")

    def load_model(self, model_name="uer/gpt2-chinese-cluecorpussmall", force_cpu=False):
        try:
            self.device = self.get_device(force_cpu)
            print(f"Loading model on device: {self.device}")

            self.pipeline = pipeline(
                "text-generation",
                model=model_name,
                device=self.device if self.device.type == "mps" else -1
            )
            print(f"Model loaded successfully on {self.device}")
            return True
        except Exception as e:
            print(f"Model loading failed: {e}")
            return False

# 初始化模型配置
model_config = ModelConfig()

# 提供首頁
@app.route('/')
def index():
    return render_template('index.html')

# 創建新對話
@app.route('/api/new_conversation', methods=['POST'])
def create_conversation():
    conversation_name = request.json.get('name', '新對話')
    conversation_id = str(uuid.uuid4())

    new_conversation = Conversation(id=conversation_id, name=conversation_name)
    db.session.add(new_conversation)
    db.session.commit()

    return jsonify({
        'id': conversation_id,
        'name': conversation_name
    })

# 處理 POST 請求
@app.route('/api/message', methods=['POST'])
def handle_message():
    # 獲取前端傳遞的訊息
    user_input = request.json.get('message', '')
    conversation_id = request.json.get('conversation_id')

    if not user_input or not conversation_id:
        return jsonify({"error": "Invalid request"}), 400

    # 確保模型已正確加載
    if not model_config.pipeline:
        return jsonify({"error": "AI 模型未加載，請檢查伺服器設定"}), 500

    # 儲存用戶訊息到資料庫
    user_message = ChatMessage(
        conversation_id=conversation_id,
        sender='user',
        message=user_input
    )
    db.session.add(user_message)

    # 使用 AI 模型生成回覆
    try:
        ai_response = model_config.pipeline(
            user_input, max_length=100, num_return_sequences=1, truncation=True
        )
        reply = ai_response[0]['generated_text']

        # 儲存 AI 回覆到資料庫
        ai_chat_message = ChatMessage(
            conversation_id=conversation_id,
            sender='ai',
            message=reply
        )
        db.session.add(ai_chat_message)

        # 提交資料庫事務
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"生成回覆時出錯: {str(e)}"}), 500

    return jsonify({"reply": reply})

# 查詢對話列表
@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    conversations = Conversation.query.order_by(Conversation.created_at.desc()).all()
    return jsonify([
        {
            'id': conv.id,
            'name': conv.name,
            'created_at': conv.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for conv in conversations
    ])

# 查詢特定對話的歷史記錄
@app.route('/api/chat_history/<conversation_id>', methods=['GET'])
def get_chat_history(conversation_id):
    messages = ChatMessage.query.filter_by(conversation_id=conversation_id).order_by(ChatMessage.timestamp).all()
    return jsonify([msg.to_dict() for msg in messages])

# 刪除對話
@app.route('/api/delete_conversation/<conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    try:
        # 刪除對話記錄
        ChatMessage.query.filter_by(conversation_id=conversation_id).delete()
        # 刪除對話
        Conversation.query.filter_by(id=conversation_id).delete()
        db.session.commit()
        return jsonify({"message": "對話已刪除"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"刪除對話時出錯: {str(e)}"}), 500

# 修改新對話聊天室名稱
@app.route('/api/rename_conversation/<conversation_id>', methods=['PUT'])
def rename_conversation(conversation_id):
    try:
        new_name = request.json.get('name')
        if not new_name:
            return jsonify({"error": "Name is required"}), 400

        conversation = Conversation.query.get(conversation_id)
        if not conversation:
            return jsonify({"error": "Conversation not found"}), 404

        conversation.name = new_name
        db.session.commit()

        return jsonify({
            "id": conversation.id,
            "name": conversation.name
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# 搜尋功能
@app.route('/api/search_messages', methods=['GET'])
def search_messages():
    query = request.args.get('query', '').lower()
    if not query:
        return jsonify([])

    try:
        # 搜尋所有符合關鍵字的訊息
        results = db.session.query(
            ChatMessage,
            Conversation.name.label('conversation_name')
        ).join(
            Conversation,
            ChatMessage.conversation_id == Conversation.id
        ).filter(
            db.or_(
                db.func.lower(ChatMessage.message).contains(query),
                db.func.lower(Conversation.name).contains(query)
            )
        ).all()

        # 格式化搜尋結果
        messages = [{
            'message': msg.message,
            'sender': msg.sender,
            'conversation_id': msg.conversation_id,
            'conversation_name': conv_name,
            'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        } for msg, conv_name in results]

        return jsonify(messages)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 創建資料庫表格
with app.app_context():
    db.create_all()

# 初始化時載入模型
with app.app_context():
    if not model_config.load_model():  # 預設使用 MPS (GPU)
        exit(1)  # 模型加載失敗時停止應用啟動

if __name__ == "__main__":
    freeze_support()
    app.run(debug=True, threaded=False)  # 生產環境建議使用 WSGI (例如 gunicorn)
