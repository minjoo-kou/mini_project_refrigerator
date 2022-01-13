from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

from bson import ObjectId

app = Flask(__name__)

# JWT 토큰을 만들 때 필요한 비밀문자열입니다.
SECRET_KEY = 'SPARTA'


client = MongoClient('mongodb://test:test@localhost', 27017)
db = client.dbsparta



# 메인 페이지
@app.route('/')
def home():
    # 쿠키에서 토큰 가져오기
    token_receive = request.cookies.get('mytoken')
    # 오늘 날짜 설정 (메인페이지에서 유통기한과 비교하여 유통기한별로 카드 색상을 바꾸기 위해 오늘 날짜 불러오기)
    d_today = datetime.today()
    try:
        # 로그인된 유저 정보 jwt 토큰 디코드하여 페이로드 설정
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 로그인 정보를 토대로 user_info 설정
        user_info = db.users.find_one({"user_id": payload["id"]})
        # refrigerator db에서 user_id(아이디)가 로그인 아이디와 일치하는 모든 재료 데이터 불러와서 date(유통기한)순으로 오름차순 정렬
        foods = list(db.refrigerator.find({'user_id': user_info['user_id']}).sort('date', 1))
        # 오늘 날짜 yyyymmdd형식으로 변경 (메인페이지에서 유통기한과 비교하여 유통기한별로 카드 색상을 바꾸기 위해 오늘 날짜 불러오기)
        # 변경이유 : refrigerator db에서 불러운 date(유통기한)이 yyyymmdd형식으로 저장되어 있음
        now = d_today.strftime('%Y%m%d')
        for i in range(len(foods)):
            # ObjectId 타입 문자열로 변경
            id = str(foods[i]['_id'])
            # 문자열로 변경한 ObjectId로 기존 ObjectId 대체
            foods[i]['_id']=id
            # 오늘 날짜 설정 (디데이 계산 과정)
            now_date = datetime.today()
            # refrigerator db에서 불러온 재료의 date(유통기한) 가져오기
            date = foods[i]['date']
            # refrigerator db에 불러온 재료의 date(유통기한) yyyymmdd형태로 변환
            # 변경이유 : refrigerator db에서 불러운 date(유통기한)이 yyyymmdd형식으로 저장되어 있음
            end_date = datetime.strptime(date, "%Y%m%d")
            # end_date(유통기한)-now_date(오늘날짜)를 계산하여 재료의 dday 계산
            dday = end_date - now_date
            # .days가 일수를 내림으로 계산하기 때문에 +1처리 (1일 5시간->2일)
            # 유통기한이 남은 경우 D-일수, 유통기한이 지난 경우 D+일수로 나타내기 위해 절대값으로 변환
            foods[i]['dday'] = abs(dday.days + 1)
            # 유저정보와 재료정보와 오늘날짜를 list.html로 전달
        return render_template('list.html', user_info=user_info, foods=foods, now=now)
    # JWT 토큰의 유효시간이 끝난 경우 로그인페이지로 이동
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    # 로그인 정보가 없으면 로그인페이지로 이동
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

# 로그인페이지 이동
@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)

# 로그인
# id, pw를 받아서 맞춰보고, 토큰을 만들어 발급합니다.
@app.route('/sign_in', methods=['POST'])
def sign_in():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    # pw를 암호화합니다.
    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    # id, 암호화된pw을 가지고 해당 유저를 찾습니다.
    result = db.users.find_one({'user_id': username_receive, 'user_pw': pw_hash})
    # 찾으면 JWT 토큰을 만들어 발급합니다.
    if result is not None:
        payload = {
         'id': username_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')
        # token을 줍니다.
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# 회원가입
# user_id, user_pw, user_name 을 받아서, mongoDB에 저장합니다.
@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "user_id": username_receive,
        "user_pw": password_hash,
        "user_name": username_receive

    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})

# 아이디 중복확인
@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"user_id": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


# 재료 등록하기
@app.route('/board', methods=['POST'])
def posting():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"user_id": payload["id"]})

        # 클라이언트에서 받은 Input 값 넘겨주기(접속한 사용자 id, 재료명, 재료 수, 단위, 유통기한, 메모)
        user_id_receive = user_info['user_id']
        name_receive = request.form['name_give']
        count_receive = request.form['count_give']
        msrmt_receive = request.form['msrmt_give']

        # 클라이언트에서 넘겨주는 유통기한 형식(MM/DD/YYYY) -> DDAY계산을 위해 형식 변환(YYYYMMDD)
        date_receive_temp = request.form['date_give'].split('/')
        date_receive = date_receive_temp[2] + date_receive_temp[0] + date_receive_temp[1]
        memo_receive = request.form['memo_give']
        doc = {
            'user_id': user_id_receive,
            'name': name_receive,
            'count': int(count_receive),
            'msrmt': msrmt_receive,
            'date': date_receive,
            'memo': memo_receive
        }
        db.refrigerator.insert_one(doc)
        return jsonify({'msg': '저장이 완료되었습니다!'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

# 재료 삭제하기
@app.route('/board', methods=['DELETE'])
def test_post():
    # 쿠키에서 토큰 가져오기
    token_receive = request.cookies.get('mytoken')
    try:
        # 로그인된 유저 정보 jwt 토큰 디코드하여 페이로드 설정
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 로그인 정보를 토대로 user_info 설정
        user_info = db.users.find_one({"user_id": payload["id"]})
        # user_info를 토대로 유저의 아이디를 user_id_receive로 설정
        user_id_receive = user_info['user_id']
        # DELETE 요청으로 받은 name_give(삭제할 재료이름)을 name_receive로 설정
        name_receive = request.form['name_give']
        # DELETE 요청으로 받은 date_give(삭제할 재료의 유통기한)을 date_receive로 설정
        date_receive = request.form['date_give']
        # DELETE 요청으로 받은 msrmt_give(삭제할 재료의 단위)을 mrsmt_receive로 설정
        msrmt_receive = request.form['msrmt_give']
        # refrigerator db에서 삭제하려는 재료와 user_id, name, date, msrmt가 같은 데이터를 찾아 삭제
        db.refrigerator.delete_one(
            {'user_id': user_id_receive, 'name': name_receive, 'date': date_receive, 'msrmt': msrmt_receive})
        return jsonify({'msg': '삭제되었습니다!'})
    # # JWT 토큰의 유효시간이 끝났거나 로그인 정보가 없으면 홈페이지로 이동
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

# 재료 수정페이지 보여주기
@app.route('/edit/<id>',methods=['GET'])
def show_edit(id):
    # str값으로 받은 id를 ObjectId 형식으로 변환
    set_id = ObjectId(id)

    # ObjectId로 db에서 내가 수정할 article 데이터 가져오기(clicked_article)
    # (*사용자 기준으로 필터링 된 재료가 아닌, 전체 db에서 다시 가져와야하는 비효율 발생)
    clicked_article = db.refrigerator.find_one({'_id':set_id})

    # date를 보기 좋은 형태로 내려주기 (MM/DD/YYYY)
    raw_date = clicked_article['date']
    str_date = str(raw_date)
    year = str_date[0:4]
    month = str_date[4:6]
    day = str_date[6:8]
    new_date = month + "/" + day + "/" + year

    # new_date 값 저장하고, objectID값은 다시 string 값으로 clicked_article에 저장해줌
    clicked_article['new_date'] = new_date
    clicked_article['_id'] = str(clicked_article['_id'])

    # clicked_article값을 result에 저장하고, 해당 함수 실행시 수정페이지 rendering
    return render_template('edit.html', result=clicked_article)


# 재료 수정하기
@app.route('/edit/<id>',methods=['POST'])
def detail_edit(id):
    # str값으로 받은 id를 ObjectId 형식으로 변환
    set_id = ObjectId(id)
    name_receive = request.form['name_give']
    count_receive = request.form['count_give']
    msrmt_receive = request.form['msrmt_give']

    # 유통기한 수정 여부 1)수정X -> YYYYMMDD 전달 2) 수정O -> MM/DD/YYYY 전달
    date_receive = request.form['date_give']

    # 2)의 경우 YYYYYMMDD형태로 처리해서 db에 update 필요
    if "/" in date_receive:
        date_list = date_receive.split('/')
        date_string = ''.join(date_list)
        date_receive = date_string[4: ]+date_string[0:2] + date_string[2:4]

    memo_receive = request.form['memo_give']

    # ObjectId기준으로 update할 재료 찾고 수정해주기 (재료 수정 페이지 보여주기 함수에서도 똑같이 이렇게 set_id로 찾아주는데, 중복된 작업인지?)
    db.refrigerator.update_one({'_id': ObjectId(id)}, {'$set': {'name': name_receive, "count": count_receive, "msrmt": msrmt_receive, "date": date_receive, "memo": memo_receive}})
    return jsonify({'msg': '변경되었어요!'})

# 재료 상세페이지
@app.route('/detail/<id>', methods=['GET'])
def watch_article(id):
    # 메인페이지에서 클릭한 str type의 id 파라메터를 ObjectId 형식으로 변환
    set_id = ObjectId(id)
    clicked_article = db.refrigerator.find_one({'_id': set_id})

    # 날짜를 보기 좋은 형태로 내려주기 (MM/DD/YYYY)
    str_date = clicked_article['date']
    year = str_date[0:4]
    month = str_date[4:6]
    day = str_date[6:8]

    new_date = year + "/" + month + "/" + day

    # new_date 값 저장하고, objectID값은 다시 string 값으로 clicked_article에 저장해줌
    clicked_article['new_date'] = new_date
    clicked_article['_id'] = str(clicked_article['_id'])

    return render_template('detail.html', result=clicked_article)



if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)