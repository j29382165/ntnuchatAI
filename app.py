from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
import torch
from model import LanguageModel
from save_load_model import load_model
from tokenization import build_vocab
from data_cleaning import clean_text
from generate_text import generate_text

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

# # 加載 Hugging Face 的 AI 模型
# try:
#     ai_pipeline = pipeline("text-generation", model="facebook/opt-350m")  # 指定模型
# except Exception as e:
#     print(f"模型加載失敗: {e}")
#     ai_pipeline = None

# 加載自訓練模型
try:
    # 從 PDF 和 Word 文件讀取數據來初始化詞彙表
    from data_extraction import extract_pdf_text, extract_word_text
    
    try:
        pdf_text = extract_pdf_text("/Users/sma01/Downloads/testdata.pdf")
        word_text = extract_word_text("/Users/sma01/Downloads/testdata.docx")
        all_text = pdf_text + word_text
    except Exception as e:
        print(f"讀取訓練文件失敗: {e}")
        # 如果無法讀取文件，使用一個小的示例文本
        all_text = "這是一個測試文本 用於初始化詞彙表"
    
    cleaned_text = clean_text(all_text)
    vocab = build_vocab(cleaned_text)
    vocab_size = max(1000, len(vocab) + 1)  # 確保詞彙表大小至少為1000
    
    # 初始化模型
    embed_size = 128
    hidden_size = 256
    model = LanguageModel(vocab_size, embed_size, hidden_size)
    
    # 加載訓練好的模型
    loaded_vocab_size = load_model(model, "ntnuchatAI/language_model.pth")
    model.eval()  # 設置為評估模式
    
    # 創建反向詞彙表
    inv_vocab = {v: k for k, v in vocab.items()}
    
    print("模型加載成功")
    print(f"詞彙表大小: {vocab_size}")
    
except Exception as e:
    print(f"模型加載失敗: {e}")
    model = None
    vocab = None
    inv_vocab = None



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
    if not model or not vocab:
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
        # 使用模型生成回覆
        with torch.no_grad():
            reply = generate_text(
                model=model,
                start_text=user_input,
                vocab=vocab,
                inv_vocab=inv_vocab,
                max_length=50,
                seq_length=10
            )

        # 儲存 AI 回覆
        ai_message = ChatMessage(
            conversation_id=conversation_id,
            sender='ai', 
            message=reply
        )
        db.session.add(ai_message)
        db.session.commit()
        
        return jsonify({"reply": reply})

    except Exception as e:
        db.session.rollback()
        print(f"Error generating response: {e}")
        return jsonify({"error": f"生成回覆時出錯: {str(e)}"}), 500

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


#修改新對話聊天室名稱
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

if __name__ == "__main__":
    app.run(debug=True, threaded=False)  # 生產環境建議使用 WSGI (例如 gunicorn)