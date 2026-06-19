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
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'connect_args': {'sslmode': 'require'}
}
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
    {
        "text": "吾輩は猫である。名前はまだ無い。どこで生れたかとんと見当がつかぬ。",
        "ruby": "わがはいはねこである。なまえはまだない。どこでうまれたかとんとけんとうがつかぬ。"
    },
    {
        "text": "春はあけぼの。やうやう白くなりゆく山ぎは、少し明かりて、紫だちたる雲の細くたなびきたる。",
        "ruby": "はるはあけぼの。やうやうしろくなりゆくやまぎは、すこしあかりて、むらさきだちたるくものほそくたなびきたる。"
    },
    {
        "text": "国境の長いトンネルを抜けると雪国であった。夜の底が白くなった。",
        "ruby": "くにざかいのながいトンネルをぬけるとゆきぐにであった。よるのそこがしろくなった。"
    },
    {
        "text": "メロスは激怒した。必ず、かの邪智暴虐の王を除かなければならぬと決意した。",
        "ruby": "メロスはげきどした。かならず、かのじゃちぼうぎゃくのおうをのぞかなければならぬとけついした。"
    },
    {
        "text": "木曾路はすべて山の中である。あるところは崖の道であり、あるところは木曾川の岸であった。",
        "ruby": "きそじはすべてやまのなかである。あるところはがけのみちであり、あるところはきそがわのきしであった。"
    },
    {
        "text": "親譲りの無鉄砲で子供の時から損ばかりしている。学校の二階から飛び降りて腰を抜かした事がある。",
        "ruby": "おやゆずりのむてっぽうでこどものときからそんばかりしている。がっこうのにかいからとびおりてこしをぬかしたことがある。"
    },
    {
        "text": "ゆく河の流れは絶えずして、しかももとの水にあらず。よどみに浮かぶうたかたは、かつ消えかつ結びて、久しくとどまりたるためしなし。",
        "ruby": "ゆくかわのながれはたえずして、しかももとのみずにあらず。よどみにうかぶうたかたは、かつきえかつむすびて、ひさしくとどまりたるためしなし。"
    },
    {
        "text": "祇園精舎の鐘の声、諸行無常の響きあり。盛者必衰の理をあらはす。おごれる人も久しからず。",
        "ruby": "ぎおんしょうじゃのかねのこえ、しょぎょうむじょうのひびきあり。じょうしゃひっすいのことわりをあらわす。おごれるひともひさしからず。"
    },
    {
        "text": "山路を登りながら、こう考えた。智に働けば角が立つ。情に棹させば流される。意地を通せば窮屈だ。",
        "ruby": "やまみちをのぼりながら、こうかんがえた。ちにはたらけばかどがたつ。じょうにさおさせばながされる。いじをとおせばきゅうくつだ。"
    },
    {
        "text": "人間は考える葦である。宇宙は人間を押しつぶすことができる。しかし人間が宇宙より尊いのは、人間は死を知っているからだ。",
        "ruby": "にんげんはかんがえるあしである。うちゅうはにんげんをおしつぶすことができる。しかしにんげんがうちゅうよりとうといのは、にんげんはしをしっているからだ。"
    },
    {
        "text": "昔々あるところにおじいさんとおばあさんが住んでいました。おじいさんは山へ柴刈りに、おばあさんは川へ洗濯に行きました。",
        "ruby": "むかしむかしあるところにおじいさんとおばあさんがすんでいました。おじいさんはやまへしばかりに、おばあさんはかわへせんたくにいきました。"
    },
    {
        "text": "竹取の翁といふものありけり。野山にまじりて竹を取りつつ、よろづのことに使ひけり。",
        "ruby": "たけとりのおきなといふものありけり。のやまにまじりてたけをとりつつ、よろづのことにつかひけり。"
    },
    {
        "text": "桜の花びらが風に舞い、川面に落ちていく。春の訪れを告げるその光景は、日本人の心に深く刻まれている。",
        "ruby": "さくらのはなびらがかぜにまい、かわもにおちていく。はるのおとずれをつげるそのこうけいは、にほんじんのこころにふかくきざまれている。"
    },
    {
        "text": "富士山は日本一高い山であり、その美しい姿は古くから多くの芸術家たちに愛されてきた。",
        "ruby": "ふじさんはにほんいちたかいやまであり、そのうつくしいすがたはふるくからおおくのげいじゅつかたちにあいされてきた。"
    },
    {
        "text": "東京は世界有数の大都市であり、伝統と現代が共存する独特の文化を持っている。",
        "ruby": "とうきょうはせかいゆうすうのだいとしであり、でんとうとげんだいがきょうぞんするどくとくのぶんかをもっている。"
    },
    {
        "text": "科学技術の進歩により、私たちの生活は大きく変わった。しかしその一方で、自然との共生という課題も生まれている。",
        "ruby": "かがくぎじゅつのしんぽにより、わたしたちのせいかつはおおきくかわった。しかしそのいっぽうで、しぜんとのきょうせいというかだいもうまれている。"
    },
    {
        "text": "夏目漱石は明治時代を代表する文豪であり、その作品は現代においても多くの人々に読み継がれている。",
        "ruby": "なつめそうせきはめいじじだいをだいひょうするぶんごうであり、そのさくひんはげんだいにおいてもおおくのひとびとによみつがれている。"
    },
    {
        "text": "海は広いな大きいな、月が昇るし日が沈む。海に大きな夢がある、波に揺られて旅をする。",
        "ruby": "うみはひろいなおおきいな、つきがのぼるしひがしずむ。うみにおおきなゆめがある、なみにゆられてたびをする。"
    },
    {
        "text": "雨ニモマケズ風ニモマケズ雪ニモ夏ノ暑サニモマケヌ丈夫ナカラダヲモチ欲ハナク決シテ瞋ラズイツモシヅカニワラッテヰル。",
        "ruby": "あめにもまけずかぜにもまけずゆきにもなつのあつさにもまけぬじょうぶなからだをもちよくはなくけっしていからずいつもしずかにわらっている。"
    },
    {
        "text": "いつも心に太陽を、くちびるに歌を、苦しいときも悲しいときも、前を向いて歩いていこう。",
        "ruby": "いつもこころにたいようを、くちびるにうたを、くるしいときもかなしいときも、まえをむいてあるいていこう。"
    },
]

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/text')
def api_text():
    t = random.choice(TEXTS)
    text = t['text']
    ruby = t['ruby']
    # テキストとふりがなを1文字ずつ対応した配列に変換
    # ふりがなの文字数がテキストと異なる場合はそのまま返す
    chars = list(text)
    rubys = list(ruby)
    return jsonify({'text': text, 'ruby': ruby, 'chars': chars, 'rubys': rubys})

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
