from pymongo import MongoClient
import jwt
import datetime 
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash,send_from_directory
from werkzeug.utils import secure_filename
import certifi
import os
from tag import extract_tags as extract_tags



ca = certifi.where()
app = Flask(__name__)
client = MongoClient('mongodb+srv://test:sparta@cluster0.bep7j.mongodb.net/Cluster0?retryWrites=true&w=majority',
                     tlsCAFile=ca)
db = client.dbsparta

app.config["TEMPLATES_AUTO_RELOAD"] = True

SECRET_KEY = 'SPARTA'


#################################
##  HTML을 주는 부분             ##
#################################
@app.route('/', methods=['GET', 'POST'])
def home():
    # 현재 이용자의 컴퓨터에 저장된 cookie 에서 mytoken 을 가져옵니다.
    token_receive = request.cookies.get('mytoken')
    try:
        # 암호화되어있는 token의 값을 우리가 사용할 수 있도록 디코딩(암호화 풀기)해줍니다!
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"id": payload['id']})
        return render_template('main.html', nickname=user_info["nick"], id=user_info["id"])
    # 만약 해당 token의 로그인 시간이 만료되었다면, 아래와 같은 코드를 실행합니다.
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login"))
    except jwt.exceptions.DecodeError:
        # 만약 해당 token이 올바르게 디코딩되지 않는다면, 아래와 같은 코드를 실행합니다.
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

# @app.route('/tags', methods=['GET'])
# def tags():
#     today = datetime.datetime.today()       # prevent mongodb error (date.today())
#     dt = datetime.datetime(today.year, today.month, today.day) 
#     tags = db.tags.find_one({'today':dt})
#     return jsonify({'tags':tags})

@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/register/', methods=['GET'])
def register():
    return render_template('register.html')


@app.route('/main')
def main():
    today = datetime.datetime.today()       # prevent mongodb error (date.today())
    dt = datetime.datetime(today.year, today.month, today.day) 
    tags = db.tags.find_one({'today':dt})['tags']
    print(tags)
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"id": payload['id']})
        return render_template('main.html', nickname=user_info["nick"], id=user_info["id"], tags=tags)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/mypage', methods=['GET'])
def mypage():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256']) 
        user_info = db.user.find_one({"id": payload['id']})
        return render_template('mypage.html', mytoken=token_receive, nickname=user_info["nick"], id=user_info["id"],
                               posts=user_info["posts"], followers=user_info["followers"],
                               following=user_info["following"])
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route("/comment", methods=["POST"])
def comment_post():
    comment_receive = request.form['comment_give']
    nickname_receive = request.form['nickname_give']
    doc = {
        'nick': nickname_receive,
        'comment': comment_receive
    }
    db.comments.insert_one(doc)

    return jsonify({'msg': '댓글 게시 완료'})


@app.route("/comment", methods=["GET"])
def comment_get():
    comments_list = list(db.comments.find({}, {'_id': False}))
    return jsonify({'comments': comments_list})

UPLOAD_FOLDER = 'Team-project/new_Claire/static/image/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024   # RequestEntityTooLarge if more than 16mb

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/fileupload', methods = ['GET', 'POST'])
def save_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.abspath(UPLOAD_FOLDER+filename))
            return render_template('main.html', msg="업로드 되었습니다.")


######## ================ #######


#################################
##  로그인을 위한 API            ##
#################################

# [회원가입 API]
# id, pw, nickname을 받아서, mongoDB에 저장합니다.
# 저장하기 전에, pw를 sha256 방법(=단방향 암호화. 풀어볼 수 없음)으로 암호화해서 저장합니다.
@app.route('/api/register', methods=['POST'])
def api_register():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    nickname_receive = request.form['nickname_give']
    posts_receive = request.form['posts_give']
    followers_receive = request.form['followers_give']
    following_receive = request.form['following_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    db.user.insert_one({'id': id_receive, 'pw': pw_hash, 'nick': nickname_receive, 'posts': posts_receive,
                        'followers': followers_receive, 'following': following_receive})

    return jsonify({'result': 'success'})


# [로그인 API]
# id, pw를 받아서 맞춰보고, 토큰을 만들어 발급합니다.
@app.route('/api/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    # 회원가입 때와 같은 방법으로 pw를 암호화합니다.
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    # id, 암호화된 pw을 가지고 해당 유저를 찾습니다.
    result = db.user.find_one({'id': id_receive, 'pw': pw_hash})

    # 찾으면 JWT 토큰을 만들어 발급합니다.
    if result is not None:
        # JWT 토큰에는, payload와 시크릿키가 필요합니다.
        # 시크릿키가 있어야 토큰을 디코딩(=암호화 풀기)해서 payload 값을 볼 수 있습니다.
        # 아래에선 id와 exp를 담았습니다. 즉, JWT 토큰을 풀면 유저ID 값을 알 수 있습니다.
        # exp에는 만료시간을 넣어줍니다. 만료시간이 지나면, 시크릿키로 토큰을 풀 때 만료되었다고 에러가 납니다.
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=360)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        userinfo = db.user.find_one({'id': request.form['id_give']}, {'_id': 0})
        # token을 줍니다.
        return jsonify({'result': 'success', 'token': token, 'msg': userinfo[
                                                                        'nick'] + '님, 안녕하세요!'})  # 'nick': userinfo['nick'] 은 찾아지는데 nick에 넣어서 넘겨지지 않음,,그래서 msg로 넘김
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# [유저 정보 확인 API]
# 로그인된 유저만 call 할 수 있는 API입니다.
# 유효한 토큰을 줘야 올바른 결과를 얻어갈 수 있습니다.
# (그렇지 않으면 남의 장바구니라든가, 정보를 누구나 볼 수 있겠죠?)
@app.route('/api/nick', methods=['GET'])
def api_valid():
    token_receive = request.cookies.get('mytoken')
    try:
        # token을 시크릿키로 디코딩합니다.
        # 보실 수 있도록 payload를 print 해두었습니다. 우리가 로그인 시 넣은 그 payload와 같은 것이 나옵니다.
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        # print(type(payload))
        # QQQ. 얘는 <class 'dict'> 이던데 왜 얘를 comment_post()에서 api_valid()로 받으니까 <class 'flask.wrappers.Response'>인지?

        # payload 안에 id가 들어있습니다. 이 id로 유저정보를 찾습니다.
        # 여기에선 그 예로 닉네임을 보내주겠습니다.
        userinfo = db.user.find_one({'id': payload['id']}, {'_id': 0})
        print(userinfo['id'])

        return jsonify({'result': 'success', 'nickname': userinfo['nick']})
    except jwt.ExpiredSignatureError:
        # 위를 실행했는데 만료시간이 지났으면 에러가 납니다.
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

####### image upload to folder #######
UPLOAD_FOLDER = 'Team-project/new_Claire/static/image/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # RequestEntityTooLarge if more than 16mb


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/fileupload', methods=['GET', 'POST'])
def save_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.abspath(UPLOAD_FOLDER + filename))
            return render_template('main.html', msg="업로드 되었습니다.")
