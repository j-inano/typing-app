import os
import random
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
database_url = os.environ.get('DATABASE_URL', 'sqlite:///typing.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql+psycopg://', 1)
elif database_url.startswith('postgresql://'):
    database_url = database_url.replace('postgresql://', 'postgresql+psycopg://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'typing-secret-key')

db = SQLAlchemy(app)

class TypingScore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    score = db.Column(db.Integer, nullable=False)   # 正確に入力できた文字数
    elapsed = db.Column(db.Float, nullable=False)   # 経過秒数
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

TEXTS = [
    "吾輩は猫である。名前はまだ無い。どこで生れたかとんと見当がつかぬ。何でも薄暗いじめじめした所でニャーニャー泣いていた事だけは記憶している。",
    "春はあけぼの。やうやう白くなりゆく山ぎは、少し明かりて、紫だちたる雲の細くたなびきたる。",
    "国境の長いトンネルを抜けると雪国であった。夜の底が白くなった。信号所に汽車が止まった。",
    "メロスは激怒した。必ず、かの邪智暴虐の王を除かなければならぬと決意した。メロスには政治がわからぬ。",
    "木曾路はすべて山の中である。あるところは岨づたいに行く崖の道であり、あるところは数十間の深さに臨む木曾川の岸であり、あるところは山の尾をめぐる谷の入り口である。",
    "親譲りの無鉄砲で子供の時から損ばかりしている。小学校にいる時分学校の二階から飛び降りて一週間ほど腰を抜かした事がある。",
    "ゆく河の流れは絶えずして、しかももとの水にあらず。よどみに浮かぶうたかたは、かつ消えかつ結びて、久しくとどまりたるためしなし。",
    "祇園精舎の鐘の声、諸行無常の響きあり。沙羅双樹の花の色、盛者必衰の理をあらはす。おごれる人も久しからず、ただ春の夜の夢のごとし。",
]

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/text')
def api_text():
    return jsonify({'text': random.choice(TEXTS)})

@app.route('/api/score', methods=['POST'])
def api_score():
    data = request.get_json()
    username = data.get('username', '名無し').strip() or '名無し'
    score = int(data.get('score', 0))
    elapsed = float(data.get('elapsed', 0))
    record = TypingScore(username=username, score=score, elapsed=elapsed)
    db.session.add(record)
    db.session.commit()
    return jsonify({'status': 'ok'})

@app.route('/api/ranking')
def api_ranking():
    scores = TypingScore.query.order_by(
        TypingScore.score.desc(),
        TypingScore.elapsed.asc()
    ).limit(5).all()
    return jsonify([{
        'username': s.username,
        'score': s.score,
        'elapsed': s.elapsed,
        'created_at': s.created_at.strftime('%m/%d %H:%M')
    } for s in scores])

if __name__ == '__main__':
    app.run(debug=True, port=5001)
