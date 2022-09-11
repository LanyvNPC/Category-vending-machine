from logging import log
from flask import Flask, render_template, request, make_response
from flask import session, redirect, url_for, abort
from datetime import timedelta
import datetime
import time
import sqlite3
import randomstring
import os
import datetime
from datetime import timedelta
import json
from discord_webhook import DiscordEmbed, DiscordWebhook
import time
import warnings
import sys
import os
import time
import requests
import json
from flask import Flask,jsonify, request
import traceback

curdir = os.path.dirname(__file__) + "/"
app = Flask(__name__)

app.secret_key = randomstring.pick(30)


warnings.filterwarnings("ignore", category=DeprecationWarning)

start = time.time()


def is_expired(time):
    ServerTime = datetime.datetime.now()
    ExpireTime = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M')
    if ((ExpireTime - ServerTime).total_seconds() > 0):
        return False
    else:
        return True

def get_expiretime(time):
    ServerTime = datetime.datetime.now()
    ExpireTime = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M')
    if ((ExpireTime - ServerTime).total_seconds() > 0):
        how_long = (ExpireTime - ServerTime)
        days = how_long.days
        hours = how_long.seconds // 3600
        minutes = how_long.seconds // 60 - hours * 60
        return str(round(days)) + "일 " + str(round(hours)) + "시간" 
    else:
        return False

def make_expiretime(days):
    ServerTime = datetime.datetime.now()
    ExpireTime = ServerTime + timedelta(days=days)
    ExpireTime_STR = (ServerTime + timedelta(days=days)).strftime('%Y-%m-%d %H:%M')
    return ExpireTime_STR

def add_time(now_days, add_days):
    ExpireTime = datetime.datetime.strptime(now_days, '%Y-%m-%d %H:%M')
    ExpireTime_STR = (ExpireTime + timedelta(days=add_days)).strftime('%Y-%m-%d %H:%M')
    return ExpireTime_STR

def nowstr():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

def get_logwebhk(serverid):
    con = sqlite3.connect("../DB/" + str(serverid) + ".db")
    cur = con.cursor()
    cur.execute("SELECT logwebhk FROM serverinfo;")
    data = cur.fetchone()[0]
    con.close()
    return data

@app.route("/", methods=["GET"])
def index():
    if ("id" in session):
        return redirect(url_for("login"))
    else:
        return redirect(url_for("setting"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if (request.method == "GET"):
        if ("id" in session):
            return redirect(url_for("setting"))
        else:
            return render_template("login.html")
    else:
        if ("id" in request.form and "pw" in request.form):
            if (request.form["id"].isdigit() and os.path.isfile("../DB/" + request.form["id"] + ".db")):
                con = sqlite3.connect("../DB/" + request.form["id"] + ".db")
                cur = con.cursor()
                cur.execute("SELECT * FROM serverinfo")
                serverinfo = cur.fetchone()
                con.close()
                if (request.form["pw"] == serverinfo[4]):
                    session.clear()
                    session["id"] = request.form["id"]
                    return """<script>alert("로그인에 성공했습니다!"); window.location.href = "/setting";</script>"""
                else:
                    return """<script>alert("비밀번호가 틀렸습니다."); window.location.href = "/login";</script>"""
            else:
                return """<script>alert("아이디가 틀렸습니다."); window.location.href = "/login";</script>"""
        else:
            return """<script>alert("아이디가 틀렸습니다."); window.location.href = "/login";</script>"""

@app.route("/setting", methods=["GET", "POST"])
def setting():
    if (request.method == "GET"):
        if ("id" in session):
            con = sqlite3.connect("../DB/" + session["id"] + ".db")
            cur = con.cursor()
            cur.execute("SELECT * FROM serverinfo")
            serverinfo = cur.fetchone()
            cur.execute("SELECT * FROM total")
            total = cur.fetchone()
            total = list(total)
            for i in range(len(total)):
                total[i] = format(total[i], ',')
            cur.execute("SELECT * FROM sold ORDER BY time DESC")
            sold_infos = cur.fetchall()
            con.close()
            try:
                bank = json.loads(serverinfo[9])
                bank['banknum']
            except:
                bank = {}
            return render_template("manage.html", info=serverinfo, bank=bank, total=total, sold_infos=sold_infos)
        else:
            return redirect(url_for("login"))
    else:
        try:
            if ("id" in session):
                if (session["id"] != "495888018058510357"):
                    if (request.form["webpanelpw"].isalnum()):
                        if (request.form["buyusernamehide"] == "Y" or request.form["buyusernamehide"] == "N"):
                            if (request.form["normaloff"].isdigit() and request.form["vipoff"].isdigit() and request.form["vvipoff"].isdigit() and request.form["reselloff"].isdigit()):
                                if (request.form["roleid"].isdigit() and request.form["viproleid"].isdigit() and request.form["vviproleid"].isdigit()):
                                    if (request.form["color"] == "파랑" or request.form["color"] == "빨강" or request.form["color"] == "초록" or request.form["color"] == "검정" or request.form["color"] == "회색"):
                                        if request.form["webhookname"] != "" or request.form["webhookprofile"] != "":
                                            if (request.form["vipautosetting"].isdigit() and request.form["vvipautosetting"].isdigit()):
                                                con = sqlite3.connect("../DB/" + session["id"] + ".db")
                                                cur = con.cursor()
                                                bankdata={"bankname": request.form['bankname'],"banknum": request.form['banknum'],"bankowner": request.form['bankowner'], "bankpw": request.form['bankpw']}
                                                cur.execute("UPDATE serverinfo SET pw = ?, cultureid = ?, culturepw = ?, logwebhk = ?, buylogwebhk = ?, roleid = ?, culture_fee = ?, bank = ?, normaloff = ?, vipoff = ?, vvipoff = ?, reselloff = ?, color = ?, chargeban = ?, vipautosetting = ?, vvipautosetting = ?, buyusernamehide = ?, viproleid = ?, vviproleid = ?, webhookprofile = ?, webhookname = ?, notice = ?;", (request.form["webpanelpw"],request.form["cultureid"], request.form["culturepw"], request.form["logwebhk"], request.form["buylogwebhk"], request.form["roleid"], request.form['fee'], json.dumps(bankdata), request.form["normaloff"], request.form["vipoff"], request.form["vvipoff"], request.form["reselloff"], request.form["color"], request.form["chargeban"], request.form["vipautosetting"], request.form["vvipautosetting"], request.form["buyusernamehide"], request.form["viproleid"], request.form["vviproleid"], request.form["webhookprofile"], request.form["webhookname"], request.form["notice"]))
                                                con.commit()
                                                con.close()
                                                return "ok"
                                            else:
                                                return "VIP 자동 등급 설정 금액, VVIP 자동 등급 설정 금액은 정수로만 적어주세요."
                                        else:
                                            return "웹훅 이름과 웹훅 프로필을 적어주세요."
                                    else:
                                        return "버튼, 임베드 색깔은 파랑, 빨강, 초록, 검정, 회색중에 하나를 입력해주세요."
                                else:
                                    return "역할 아이디는 숫자로만 입력해주세요."
                            else:
                                return "할인율은 숫자로만 입력해주세요."
                        else:
                            return "Y 또는 N으로만 입력해주세요."
                    else:
                        return "웹패널 PW는 알파벳과 숫자로만 입력해주세요."
                else:
                    return "잘못된 접근입니다."
            else:
                return "로그인이 해제되었습니다. 다시 로그인해주세요."
        except Exception as e:
            print(traceback.format_exc())
            return "오류"

@app.route("/culsetting", methods=["POST"])
def culsetting():
    if ("id" in session):
        cultureid = request.form["cultureid"]
        culturepw = request.form["culturepw"]
        res = requests.post('http://210.97.92.225:1177/api/setup', json={"token": "G4cehXsjIYNtasOxsmat", "id": cultureid,"pw": culturepw})
        req = res.json()
        print(session)
        print(req)
        if req['result'] == 'true':
            con = sqlite3.connect("../DB/" + session["id"] + ".db")
            cur = con.cursor()
            cur.execute("SELECT * FROM serverinfo")
            cur.execute("UPDATE serverinfo SET cultureid = ?, culturepw = ?",(cultureid,culturepw))
            con.commit()
            cur.close()
            return 'ok'
        else:
            return f"{req['result']}"
    else:
        return "로그인이 해제되었습니다. 다시 로그인해주세요."

        


@app.route("/manageuser", methods=["GET"])  
def manageuser():
    if ("id" in session):
        con = sqlite3.connect("../DB/" + session["id"] + ".db")
        cur = con.cursor()
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
        con.close()
        return render_template("manage_user.html", users=users)
    else:
        return redirect(url_for("login"))

@app.route("/manageuser_detail", methods=["GET", "POST"])  
def manageuser_detail():
    if (request.method == "GET"):
        if ("id" in session):
            user_id = request.args.get("id", "")
            if (user_id != ""):
                con = sqlite3.connect("../DB/" + session["id"] + ".db")
                cur = con.cursor()
                cur.execute("SELECT * FROM users WHERE id == ?;", (user_id,))
                user_info = cur.fetchone()
                con.close()
                if (user_info != None):
                    return render_template("manage_user_detail.html", info=user_info)
                else:
                    abort(404)
            else:
                abort(404)
        else:
            return redirect(url_for("login"))
    else:
        if ("id" in session):
            if ("money" in request.form and "bought" in request.form and "id" in request.form):
                if (request.form["money"].isdigit()):
                    if (request.form["bought"].isdigit()):
                        if (request.form["warnings"].isdigit()):
                            if (request.form["rank"] == "일반" or request.form["rank"] == "VIP" or request.form["rank"] == "VVIP" or request.form["rank"] == "리셀러"):
                                con = sqlite3.connect("../DB/" + session["id"] + ".db")
                                cur = con.cursor()
                                cur.execute("UPDATE users SET money = ?, bought = ?, warnings = ?, rank = ? WHERE id == ?;", (request.form["money"], request.form["bought"], request.form["warnings"], request.form["rank"], request.form["id"]))
                                con.commit()
                                con.close()
                                return "ok"
                            else:
                                return "등급은 일반, VIP, VVIP, 리셀러중에 선택해서 적어주세요."
                        else:
                            return "경고 수는 정수로만 적어주세요."
                    else:
                        return "누적 금액은 정수로만 적어주세요."
                else:
                    return "잔액은 정수로만 적어주세요."
            else:
                return "잘못된 접근입니다."
        else:
            return "로그인이 해제되었습니다. 다시 로그인해주세요."

@app.route("/manageprod", methods=["GET"])  
def manageprod():
    if ("id" in session):
        con = sqlite3.connect("../DB/" + session["id"] + ".db")
        cur = con.cursor()
        cur.execute("SELECT * FROM products ORDER BY position")
        products = cur.fetchall()
        lenprod=len(products)
        con.close()
        return render_template("manage_prod.html", products=products, lenprod=lenprod)
    else:
        return redirect(url_for("login"))

@app.route("/delete_product", methods=["POST"])  
def deleteprod():
    if ("id" in session):
        if ("name" in request.form):
            con = sqlite3.connect("../DB/" + session["id"] + ".db")
            cur = con.cursor()
            cur.execute("DELETE FROM products WHERE name == ?;", (request.form["name"],))
            con.commit()
            con.close()
            return "ok"
        else:
            return "fail"
    else:
        return "fail"


@app.route("/manageprod_detail", methods=["GET", "POST"])
def manageprod_detail():
    if (request.method == "GET"):
        if ("id" in session):
            product_name = request.args.get("id", "")
            if (product_name != ""):
                print(f"{product_name}:")
                con = sqlite3.connect("../DB/" + session["id"] + ".db")
                cur = con.cursor()
                cur.execute("SELECT * FROM products WHERE name == ?;", (product_name,))
                prod_info = cur.fetchone()
                con.close()
                if (prod_info != None):
                    return render_template("manage_prod_detail.html", info=prod_info)
                else:
                    abort(404)
            else:
                abort(404)
        else:
            return redirect(url_for("login"))
    else:
        if ("id" in session):
            if ("price" in request.form and "produrl" in request.form and "stock" in request.form and "name" in request.form):
                if (request.form["price"].isdigit()):
                    con = sqlite3.connect("../DB/" + session["id"] + ".db")
                    cur = con.cursor()
                    cur.execute("UPDATE products SET name = ?, money = ?, produrl = ?, stock = ?, position = ?, catagory = ? WHERE name == ?;", (request.form["name1"], request.form["price"], request.form["produrl"], request.form["stock"], request.form["position"], request.form["catagory"], request.form["name"]))
                    con.commit()
                    con.close()
                    return "ok"
                else:
                    return "가격은 숫자로만 적어주세요."
            else:
                return "잘못된 접근입니다."
        else:
            return "로그인이 해제되었습니다. 다시 로그인해주세요."

@app.route("/createprod", methods=["GET", "POST"])
def createprod():
    if (request.method == "GET"):
        if ("id" in session):
            return render_template("create_prod.html")
        else:
            return redirect(url_for("login"))
    else:
        if ("id" in session):
            if ("price" in request.form and "name" in request.form):
                if (request.form["price"].isdigit()):
                    con = sqlite3.connect("../DB/" + session["id"] + ".db")
                    cur = con.cursor()
                    cur.execute("SELECT * FROM products WHERE name == ?;", (request.form["name"],))
                    prod = cur.fetchone()
                    if (prod == None):
                        con = sqlite3.connect("../DB/" + session["id"] + ".db")
                        cur = con.cursor()
                        cur.execute("INSERT INTO products VALUES(?, ?, ?, ?, ?, ?);", (request.form["name"], request.form["price"], "", "","",""))
                        con.commit()
                        con.close()
                        return "ok"
                    else:
                        return "이미 존재하는 제품명입니다."
                else:
                    return "가격은 숫자로만 적어주세요."
            else:
                return "잘못된 접근입니다."
        else:
            return "로그인이 해제되었습니다. 다시 로그인해주세요."

@app.route("/license", methods=["GET", "POST"])
def managelicense():
    if (request.method == "GET"):
        if ("id" in session):
            con = sqlite3.connect("../DB/" + session["id"] + ".db")
            cur = con.cursor()
            cur.execute("SELECT * FROM serverinfo")
            serverinfo = cur.fetchone()
            con.close()
            if (is_expired(serverinfo[1])):
                return render_template("manage_license.html", expire="0일 0시간 (만료됨)")
            else:
                return render_template("manage_license.html", expire=get_expiretime(serverinfo[1]))
        else:
            return redirect(url_for("login"))
    else:
        if ("id" in session):
            if ("code" in request.form):
                license_key = request.form["code"]
                con = sqlite3.connect("../DB/" + "license.db")
                cur = con.cursor()
                cur.execute("SELECT * FROM license WHERE code == ?;", (license_key,))
                search_result = cur.fetchone()
                con.close()
                if (search_result != None):
                    if (search_result[2] == 0):
                        con = sqlite3.connect("../DB/" + "license.db")
                        cur = con.cursor()
                        cur.execute("UPDATE license SET isused = ?, useddate = ?, usedby = ? WHERE code == ?;", (1, nowstr(), session["id"], license_key))
                        con.commit()
                        cur = con.cursor()
                        cur.execute("SELECT * FROM license WHERE code == ?;",(license_key,))
                        key_info = cur.fetchone()
                        con.close()
                        con = sqlite3.connect("../DB/" + session["id"] + ".db")
                        cur = con.cursor()
                        cur.execute("SELECT * FROM serverinfo;")
                        server_info = cur.fetchone()
                        if (is_expired(server_info[1])):
                            new_expiretime = make_expiretime(key_info[1])
                        else:
                            new_expiretime = add_time(server_info[1], key_info[1])
                        cur.execute("UPDATE serverinfo SET expiredate = ?;", (new_expiretime,))
                        con.commit()
                        con.close()
                        return f"{key_info[1]}"
                    else:
                        return "이미 사용된 라이센스입니다."
                else:
                    return "존재하지 않는 라이센스입니다."
            else:
                return "잘못된 접근입니다."
        else:
            return "로그인이 해제되었습니다. 다시 로그인해주세요."

@app.route("/rawviewer/<docsid>", methods=["GET"])
def rawviewer(docsid):
    con = sqlite3.connect("../DB/docs.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM docs WHERE id == ?;", (docsid,))
    docs_info = cur.fetchone()
    con.close()
    if (docs_info != None):
        return docs_info[1].replace("\n", "<br>")
    else:
        return "알 수 없는 문서 ID입니다."
    
@app.route("/logout", methods=["GET"])
def logout():
    session.clear() 
    return redirect(url_for("login"))

@app.before_request 
def make_session_permanent(): 
    session.permanent = True 
    app.permanent_session_lifetime = timedelta(minutes=60) 

@app.errorhandler(404)
def not_found_error(error):
  return render_template("404.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=90) #보안 호스트 
