from flask_sqlalchemy import SQLAlchemy
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:ROOTROOT@localhost/chat_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 測試資料庫連接
with app.app_context():
    try:
        db.create_all()
        print("資料庫連接成功")
    except Exception as e:
        print(f"資料庫連接失敗: {e}")
