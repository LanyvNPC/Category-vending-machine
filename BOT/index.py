# -*- coding: utf-8 -*-
from unicodedata import category
from discord import user
from discord_components import DiscordComponents, ComponentsBot, Select, SelectOption, Button, ButtonStyle, ActionRow
import discord, sqlite3, randomstring, os, setting, random
from discord_components.ext.filters import user_filter
import asyncio, requests, json
from setting import admin_id, domain, bot_name
import datetime as dt
from datetime import timedelta
from discord_webhook import DiscordEmbed, DiscordWebhook
from discord_buttons_plugin import ButtonType
from asyncio import futures
from functools import partial
import time
from twilio.rest import Client
import traceback

bot = discord.Client()
charginguser = []
buyinguser = []
bankchanginguser = []
license_master_ids = [958013583386619984]
total_master_ids = [958013583386619984]
prefix = '!'

def get_roleid(serverid):
    con = sqlite3.connect("../DB/" + str(serverid) + ".db")
    cur = con.cursor()
    cur.execute("SELECT roleid FROM serverinfo;")
    data = cur.fetchone()[0]
    con.close()
    if (str(data).isdigit()):
        return int(data)
    else:
        return data

def get_logwebhk(serverid):
    con = sqlite3.connect("../DB/" + str(serverid) + ".db")
    cur = con.cursor()
    cur.execute("SELECT logwebhk FROM serverinfo;")
    data = cur.fetchone()[0]
    con.close()
    return data

def get_buylogwebhk(serverid):
    con = sqlite3.connect("../DB/" + str(serverid) + ".db")
    cur = con.cursor()
    cur.execute("SELECT buylogwebhk FROM serverinfo;")
    data = cur.fetchone()[0]
    con.close()
    return data

def add_time(now_days, add_days):
    ExpireTime = dt.datetime.strptime(now_days, '%Y-%m-%d %H:%M')
    ExpireTime_STR = (ExpireTime + timedelta(days=add_days)).strftime('%Y-%m-%d %H:%M')
    return ExpireTime_STR

def is_expired(time):
    ServerTime = dt.datetime.now()
    ExpireTime = dt.datetime.strptime(time, '%Y-%m-%d %H:%M')
    if ((ExpireTime - ServerTime).total_seconds() > 0):
        return False
    else:
        return True

def get_logwebhk(serverid):
    con = sqlite3.connect("../DB/" + str(serverid) + ".db")
    cur = con.cursor()
    cur.execute("SELECT logwebhk FROM serverinfo;")
    data = cur.fetchone()[0]
    con.close()
    return data

def make_expiretime(days):
    ServerTime = dt.datetime.now()
    ExpireTime = ServerTime + timedelta(days=days)
    ExpireTime_STR = (ServerTime + timedelta(days=days)).strftime('%Y-%m-%d %H:%M')
    return ExpireTime_STR

def nowstr():
    return dt.datetime.now().strftime('%Y-%m-%d %H:%M')

@bot.event
async def on_ready():
    DiscordComponents(bot)
    print(f"Login: {bot.user}\nInvite Link: https://discord.com/oauth2/authorize?bot_id={bot.user.id}&permissions=8&scope=bot")
    while True:
        await bot.change_presence(activity=discord.Game(f"STAR SERVICE | {len(bot.guilds)}서버 사용중"),status=discord.Status.online)
        await asyncio.sleep(5)

        

@bot.event
async def on_message(message):
    if message.author.bot:
        return
        
    if message.content.startswith(prefix +'서버'):
        if message.author.id in total_master_ids:
            names = []
            for name in bot.guilds:
                names.append(name.name)
            await message.channel.send(names)
            await message.channel.send(len(bot.guilds))

    if message.content.startswith(prefix + '생성 '):
        if message.author.id in license_master_ids:
            if not isinstance(message.channel, discord.channel.DMChannel):
                try:
                    amount = int(message.content.split(" ")[1])
                except:
                    await message.channel.send("올바른 생성 갯수를 입력해주세요.")
                    return
                if 1 <= amount <= 30:
                    try:
                        license_length = int(message.content.split(" ")[2])
                    except:
                        await message.channel.send("올바른 생성 기간을 입력해주세요.")
                        return
                    codes = []
                    for _ in range(amount):
                        code = randomstring.pick(20)
                        codes.append(code)
                        con = sqlite3.connect("../DB/license.db")
                        cur = con.cursor()
                        cur.execute("INSERT INTO license Values(?, ?, ?, ?, ?);", (code, license_length, 0, "None", 0))
                        con.commit()
                        con.close()
                    await message.channel.send(embed=discord.Embed(title="생성 성공", description="디엠을 확인해주세요.", color=0x00e641))
                    await message.author.send("\n".join(codes))
        else:
            await message.channel.send(embed=discord.Embed(title="생성 실패", description="당신은 봇 관리자가 아닙니다.", color=0xe62a00))

    if message.content.startswith(prefix + '등록 '):
        if message.author.guild_permissions.administrator or message.author.id in total_master_ids:
            license_key = message.content.split(" ")[1]
            con = sqlite3.connect("../DB/license.db")
            cur = con.cursor()
            cur.execute("SELECT * FROM license WHERE code == ?;", (license_key,))
            search_result = cur.fetchone()
            con.close()
            if (search_result != None):
                if (search_result[2] == 0):
                    if not (os.path.isfile("../DB/" + str(message.guild.id) + ".db")):
                        con = sqlite3.connect("../DB/" + str(message.guild.id) + ".db")
                        cur = con.cursor()
                        cur.execute("CREATE TABLE serverinfo (id TEXT, expiredate TEXT, cultureid TEXT, culturepw TEXT, pw TEXT, roleid TEXT, logwebhk TEXT, buylogwebhk TEXT, culture_fee TEXT, bank TEXT, normaloff INTEGER, vipoff INTEGER, vvipoff INTEGER, reselloff INTEGER, color TEXT, chargeban INTEGER, vipautosetting INTEGER, vvipautosetting INTEGER, buyusernamehide TEXT, viproleid INTEGER, vviproleid INTEGER, webhookprofile TEXT, webhookname TEXT, notice TEXT, sms INTEGER, cookie TEXT);")
                        con.commit()
                        first_pw = randomstring.pick(10)
                        cur.execute("INSERT INTO serverinfo VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", (message.guild.id, make_expiretime(int(sqlite3.connect("../DB/license.db").cursor().execute("SELECT * FROM license WHERE code == ?;", (license_key,)).fetchone()[1])), "", "", first_pw, 0, "", "", 0, "", 0, 0, 0, 0, "검정", 3, 5, 10, "N", 0, 0, "https://cdn.discordapp.com/avatars/969917905380724788/4139d77286ac3c47b3519d458cd41fb1.png?size=2048", "SORRY SERVICE", "공지사항", 0, ""))
                        con.commit()
                        cur.execute("CREATE TABLE users (id INTEGER, user TEXT,money INTEGER, bought INTEGER, warnings INTEGER, rank TEXT, buycount INTEGER, sms INTEGER);")
                        con.commit()
                        cur.execute("CREATE TABLE products (name INTEGER, money INTEGER, stock TEXT, produrl TEXT, position INTEGER, catagory TEXT);")
                        con.commit()
                        cur.execute("CREATE TABLE cookie (baseInfo TEXT, appInfoConfig TEXT, JSESSIONID TEXT, _ga TEXT, LoginConfig TEXT, checkIntroAppInstall TEXT, layer_popup_mng700 TEXT, _gat TEXT, _gid TEXT, cross_site_cookie TEXT, WHATAP TEXT);")
                        con.commit()
                        cur.execute("INSERT INTO cookie VALUES(?,?,?,?,?,?,?,?,?,?,?)", ("","","","","","","","","","",""))
                        con.commit()
                        cur.execute("CREATE TABLE banklog (id INTEGER, name TEXT, money INTEGER);")
                        con.commit()
                        cur.execute("CREATE TABLE total (td INTEGER, tw INTEGER, tm INTEGER, gd INTEGER, gw INTEGER, gm INTEGER, bd INTEGER, bw INTEGER, bm INTEGER);")
                        con.commit()
                        cur.execute("INSERT INTO total VALUES(?, ?, ?, ?, ? ,?, ?, ?, ?)", (0, 0, 0, 0 ,0 ,0 ,0 ,0 ,0))
                        con.commit()
                        cur.execute("CREATE TABLE sold (name TEXT, id TEXT, product TEXT, price TEXT, time TEXT);")
                        con.commit()
                        cur.execute("INSERT INTO sold VALUES(?, ?, ?, ?, ?)", ("", "", "", "", ""))
                        con.commit()
                        con.close()
                        con = sqlite3.connect("../DB/license.db")
                        cur = con.cursor()
                        cur.execute("UPDATE license SET isused = ?, useddate = ?, usedby = ? WHERE code == ?;", (1, nowstr(), message.guild.id, license_key))
                        con.commit()
                        con.close()
                        con = sqlite3.connect("../DB/license.db")
                        cur = con.cursor()
                        cur.execute("SELECT * FROM license WHERE code == ?;", (license_key,))
                        idtxt = open("id.txt", "a", encoding="utf-8")
                        idtxt.write(f"\n{message.guild.id}")
                        await message.author.send(embed=discord.Embed(title="서버 등록 성공", description="서버가 성공적으로 등록되었습니다.\n라이센스 기간 : `" + str(sqlite3.connect("../DB/license.db").cursor().execute("SELECT * FROM license WHERE code == ?;", (license_key,)).fetchone()[1]) + "`일\n만료일 :  `" + make_expiretime(int(sqlite3.connect("../DB/license.db").cursor().execute("SELECT * FROM license WHERE code == ?;", (license_key,)).fetchone()[1])) + f"`\n웹 패널 : {domain}\n아이디 : `" +str(message.guild.id) + "`\n비밀번호 : `" + first_pw + "`", color=0x00e641),
                        components = [
                            ActionRow(
                                Button(style=ButtonType().Link,label = "웹패널",url=domain),
                            )
                        ]
                    )
                        await message.channel.send(embed=discord.Embed(title="서버 등록 성공", description="서버가 성공적으로 등록되었습니다.", color=0x00e641))
                        con.close()
                    else:
                        await message.channel.send(embed=discord.Embed(title="서버 등록 실패", description="이미 등록된 서버이므로 등록할 수 없습니다.\n기간 추가를 원하신다면 !라이센스 명령어를 이용해주세요.", color=0xe62a00))
                else:
                    await message.channel.send(embed=discord.Embed(title="서버 등록 실패", description="이미 사용된 라이센스입니다.\n관리자에게 문의해주세요.", color=0xe62a00))
            else:
                await message.channel.send(embed=discord.Embed(title="서버 등록 실패", description="존재하지 않는 라이센스입니다.", color=0xe62a00))
    
    if message.content.startswith(prefix + "서버 이전 "):
        if message.author.guild_permissions.administrator or message.author.id in total_master_ids:
            if not (os.path.isfile("../DB/" + str(message.guild.id) + ".db")):
                try:
                    server_id = message.content.split(" ")[2].split(" ")[0]
                    webpanel_pw = message.content.split(" ")[3]
                except:
                    await message.channel.send(embed=discord.Embed(title="서버 이전 실패", description="서버 아이디와 웹패널 비밀번호를 확인해주세요.", color=0xe62a00))
                if (os.path.isfile("C:/Users/Administrator/Desktop/SORRY/DB/" + server_id + ".db")):
                    con = sqlite3.connect("C:/Users/Administrator/Desktop/SORRY/DB/" + server_id + ".db")
                    cur = con.cursor()
                    cur.execute("SELECT * FROM serverinfo;", ())
                    server_info = cur.fetchone()
                    con.close()
                    if server_info[4] == webpanel_pw:
                        con = sqlite3.connect("C:/Users/Administrator/Desktop/SORRY/DB/" + server_id + ".db")
                        cur = con.cursor()
                        cur.execute("UPDATE serverinfo SET id = ?;", (str(message.guild.id),))
                        con.commit()
                        con.close()
                        os.rename("C:/Users/Administrator/Desktop/SORRY/DB/" + server_id + ".db", "../DB/" + str(message.guild.id) + ".db")
                        await message.author.send(embed=discord.Embed(title="서버 이전 성공", description="만료일: `" + server_info[1] + f"`\n웹 패널: {domain}\n아이디: `" +str(message.guild.id) + "`\n비밀번호: `" + server_info[4] + "`", color=0x00e641))
                        await message.channel.send(embed=discord.Embed(title="서버 이전 성공", description="서버가 성공적으로 이전되었습니다", color=0x00e641))
                    else:
                        await message.channel.send(embed=discord.Embed(title="서버 이전 실패", description="웹패널 비밀번호를 확인해주세요.", color=0xe62a00))
                else:
                    await message.channel.send(embed=discord.Embed(title="서버 이전 실패", description="올바른 서버 아이디를 입력해주세요.", color=0xe62a00))
            else:
                await message.channel.send(embed=discord.Embed(title="서버 이전 실패", description="이미 서버가 등록되어있습니다.", color=0xe62a00))

    if message.content == '!백업':
        if message.author.guild_permissions.administrator or message.author.id in total_master_ids:
            if (os.path.isfile("../DB/" + str(message.guild.id) + ".db")):
                try:
                    await message.delete()
                except:
                    pass
                embed = discord.Embed(title=bot_name, description='원하시는 버튼을 클릭해주세요.', color=0xe62a00)
                await message.channel.send(
                    embed=embed,
                    components = [
                        ActionRow(
                            Button(style=ButtonStyle.blue,label = "데이터베이스 백업",custom_id="디비백업"),

                        )
                    ]
                )

    if message.content.startswith(prefix + "컬쳐등록 "):
        if message.author.guild_permissions.administrator or message.author.id in total_master_ids:
            if (os.path.isfile("../DB/" + str(message.guild.id) + ".db")):
                try:
                    await message.delete()
                except:
                    pass
                cid = message.content.split(" ")[1]
                cpw = message.content.split(" ")[2]
                con = sqlite3.connect("../DB/" + str(message.guild.id) + ".db")
                cur = con.cursor()
                cur.execute("UPDATE serverinfo SET cultureid = ?, culturepw = ?;", (cid, cpw,))
                con.commit()
                con.close()
                await message.channel.send(embed=discord.Embed(title="변경 성공", description=f"성공적으로 컬쳐랜드 계정이 변경되었습니다.\n설정한 값 : {cid}, {cpw}", color=0x00e641))
            else:
                await message.channel.send(embed=discord.Embed(title="변경 실패", description="오류가 발생했습니다, 다시 시도해주세요.", color=0xe62a00))

    if message.content == "!수정 인증":
        if message.author.id in total_master_ids:
            if (os.path.isfile("../DB/" + str(message.guild.id) + ".db")):
                await message.channel.send(embed=discord.Embed(title="SMS인증 활성화여부 변경", description="SMS인증 활성화여부를 0 또는 1로 입력해주세요.\n0 = 비활성화 | 1 = 활성화",color=0x010101))
                def check(sms):
                    return (sms.author.id == message.author.id)
                sms = await bot.wait_for("message", timeout=60, check=check)
                sms = sms.content
                con = sqlite3.connect("../DB/" + str(message.guild.id) +".db")
                cur = con.cursor()
                cur.execute("UPDATE serverinfo SET sms = ?",(sms,))
                con.commit()
                cur.execute("SELECT * FROM serverinfo;")
                server_info = cur.fetchone()
                con.close()
                await message.channel.send(embed=discord.Embed(title="변경 성공", description=f"성공적으로 SMS사용여부가 변경되었습니다.",color=0x00e641))
            else:
                await message.channel.send(embed=discord.Embed(title="변경 실패", description="오류가 발생했습니다. 처음부터 다시 시도해주세요.",color=0xe62a00))

    if message.content == "!수정 웹패널비번":
        if message.author.guild_permissions.administrator or message.author.id in total_master_ids:
            if (os.path.isfile("../DB/" + str(message.guild.id) + ".db")):
                await message.channel.send(embed=discord.Embed(title="웹패널비번 변경", description="원하시는 비밀번호를 입력해주세요.",color=0x00e641))
                def check(pw):
                    return (pw.author.id == message.author.id)
                pw = await bot.wait_for("message", timeout=60, check=check)
                pw = pw.content
                con = sqlite3.connect("../DB/" + str(message.guild.id) +".db")
                cur = con.cursor()
                cur.execute("UPDATE serverinfo SET pw = ?",(pw,))
                con.commit()
                cur.execute("SELECT * FROM serverinfo;")
                server_info = cur.fetchone()
                con.close()
                await message.channel.send(embed=discord.Embed(title="변경 성공", description=f"성공적으로 웹패널 비밀번호가 변경되었습니다.",color=0x00e641))
            else:
                await message.channel.send(embed=discord.Embed(title="변경 실패", description="오류가 발생했습니다. 처음부터 다시 시도해주세요.",color=0xe62a00))

    if message.content == prefix + "수정 색깔":
        if message.author.guild_permissions.administrator or message.author.id in total_master_ids:
            if (os.path.isfile("../DB/" + str(message.guild.id) + ".db")):
                await message.channel.send(embed=discord.Embed(title="색깔 변경", description="원하시는 색깔을 입력해주세요. **( 파랑,빨강,초록,회색,검정 )**",color=0x00e641))
                def check(color):
                    return (color.author.id == message.author.id)
                color = await bot.wait_for("message", timeout=60, check=check)
                color = color.content
                con = sqlite3.connect("../DB/" + str(message.guild.id) +".db")
                cur = con.cursor()
                cur.execute("UPDATE serverinfo SET color = ?",(color,))
                con.commit()
                cur.execute("SELECT * FROM serverinfo;")
                server_info = cur.fetchone()
                con.close()
                await message.channel.send(embed=discord.Embed(title="변경 성공", description=f"성공적으로 임베드 및 버튼 색깔이 변경되었습니다.",color=0x00e641))
            else:
                await message.channel.send(embed=discord.Embed(title="변경 실패", description="오류가 발생했습니다. 처음부터 다시 시도해주세요.",color=0xe62a00))

    if message.content.startswith(prefix + "경고수 "):
        if message.author.guild_permissions.administrator or message.author.id in total_master_ids:
            if (os.path.isfile("../DB/" + str(message.guild.id) + ".db")):
                try:
                    await message.delete()
                except:
                    pass
            try:
                userId = message.mentions[0].id
            except:
                userId = int(message.content.split(" ")[1])
            try:
                warning = message.content.split(" ")[2]
            except:
                return await message.channel.send(embed=discord.Embed(title="변경 실패", description="`!경고수 @유저맨션 숫자`로 사용해주세요!", color=0xe62a00))
            con = sqlite3.connect("../DB/" + str(message.guild.id) + ".db")
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE id == ?;", (userId,))
            user_info = cur.fetchone()
            if not user_info:
                usera = await bot.fetch_user(userId)
                cur.execute("INSERT INTO users VALUES(?, ?, ?, ?, ?, ?, ?, ?);", (userId, usera, 0, 0, 0, "일반", 0, 0))
                con.commit()
                con.close()
            cur.execute("UPDATE users SET warnings = ? WHERE id == ?;", (warning, userId))
            con.commit()
            await message.channel.send(embed=discord.Embed(title="변경 성공", description=f"성공적으로 유저 경고수가 변경되었습니다.\n설정한 값 : {warning}", color=0x00e641))

    if message.content == prefix + "구매메시지":
        if message.author.guild_permissions.administrator or message.author.id in total_master_ids:
            if not isinstance(message.channel, discord.channel.DMChannel):
                if (os.path.isfile("../DB/" + str(message.guild.id) + ".db")):
                    title = await message.channel.send(embed=discord.Embed(title="구매메시지", description="제품 이름을 입력해주세요", color=0x00e641))
                    def check(msg):
                        return (not isinstance(msg.channel, discord.channel.DMChannel) and (message.author.id == msg.author.id))
                    try:
                        product_name = await bot.wait_for("message", timeout=60, check=check)
                        await title.delete()
                    except asyncio.TimeoutError:
                        try:
                            await message.channel.send(embed=discord.Embed(description="시간 초과",color=0xe62a00))
                        except:
                            pass
                        return None
                    pdes = await message.channel.send(embed=discord.Embed(title="구매메시지", description="제품 설명을 입력해주세요",color=0x00e641))
                    try:
                        product_content = await bot.wait_for("message", timeout=60, check=check)
                        await pdes.delete()
                    except asyncio.TimeoutError:
                        try:
                            await message.channel.send(embed=discord.Embed(description="시간 초과",color=0xe62a00))
                        except:
                            pass
                        return None
                    bdes = await message.channel.send(embed=discord.Embed(title="구매메시지", description="버튼 내용을 입력해주세요",color=0x00e641))
                    try:
                        button_content = await bot.wait_for("message", timeout=60, check=check)
                        await bdes.delete()
                    except asyncio.TimeoutError:
                        try:
                            await message.channel.send(embed=discord.Embed(description="시간 초과",color=0xe62a00))
                        except:
                            pass
                        return None
                    await message.channel.send(embed=discord.Embed(title=product_name.content, description=product_content.content, color=0x00e641),
                    components = [
                        ActionRow(
                            Button(style=ButtonStyle.blue,label=button_content.content,custom_id="구매")
                        )
                    ])

    if message.content == prefix + "바로가기":
        if message.author.guild_permissions.administrator or message.author.id in total_master_ids:
            if not isinstance(message.channel, discord.channel.DMChannel):
                if (os.path.isfile("../DB/" + str(message.guild.id) + ".db")):
                    title = await message.channel.send(embed=discord.Embed(title="바로가기 설정", description="제목을 입력해주세요.", color=0x00e641))
                    def check(msg):
                        return (not isinstance(msg.channel, discord.channel.DMChannel) and (message.author.id == msg.author.id))
                    try:
                        product_name = await bot.wait_for("message", timeout=60, check=check)
                        await title.delete()
                    except asyncio.TimeoutError:
                        try:
                            await message.channel.send(embed=discord.Embed(description="시간 초과",color=0xe62a00))
                        except:
                            pass
                        return None
                    des = await message.channel.send(embed=discord.Embed(title="바로가기 설정", description="내용을 입력해주세요.",color=0x00e641))
                    try:
                        product_content = await bot.wait_for("message", timeout=60, check=check)
                        await des.delete()
                    except asyncio.TimeoutError:
                        try:
                            await message.channel.send(embed=discord.Embed(description="시간 초과",color=0xe62a00))
                        except:
                            pass
                        return None
                    link = await message.channel.send(embed=discord.Embed(title="바로가기 설정", description="바로가기 링크를 입력해주세요.",color=0x00e641))
                    try:
                        link_content = await bot.wait_for("message", timeout=60, check=check)
                        await link.delete()
                    except asyncio.TimeoutError:
                        try:
                            await message.channel.send(embed=discord.Embed(description="시간 초과",color=0xe62a00))
                        except:
                            pass
                        return None
                    but = await message.channel.send(embed=discord.Embed(title="바로가기 설정", description="버튼 내용을 입력해주세요.",color=0x00e641))
                    try:
                        button_content = await bot.wait_for("message", timeout=60, check=check)
                        await but.delete()
                    except asyncio.TimeoutError:
                        try:
                            await message.channel.send(embed=discord.Embed(description="시간 초과",color=0xe62a00))
                        except:
                            pass
                        return None
                    await message.channel.send(embed=discord.Embed(title=product_name.content, description=product_content.content, color=0x00e641),
                    components = [
                        ActionRow(
                            Button(style=ButtonType().Link,label=button_content.content,url=link_content.content)
                        )
                    ])

    if message.content.startswith(prefix + "명령어"):
        await message.channel.send(embed=discord.Embed(title="버튼자판기 명령어", description="""
        !수정 웹패널비번 / 웹패널 비밀번호를 수정합니다.
        !경고수 / 누적 경고수를 수정합니다.
        !구매메시지 / 임베드 출력과 함께 구매하기 버튼이 생성됩니다.
        !바로가기 / 임베드 출력과 함께 지정한 링크 바로가기 버튼이 생성됩니다.
        """, color=0xe62a00))


    if message.content == prefix + '버튼':
        if message.author.guild_permissions.administrator or message.author.id in total_master_ids:
            if (os.path.isfile("../DB/" + str(message.guild.id) + ".db")):
                try:
                    await message.delete()
                except:
                    pass
                con = sqlite3.connect("../DB/" + str(message.guild.id) + ".db")
                cur = con.cursor()
                cur.execute("SELECT * FROM serverinfo;", ())
                server_info = cur.fetchone()
                con.close()
                color = server_info[14]
                if color == "파랑":
                    embed = discord.Embed(title=bot_name, description='원하시는 버튼을 클릭해주세요.', color=0x3b30ff)
                    await message.channel.send(
                        embed=embed,
                        components = [
                            ActionRow(
                                Button(style=ButtonStyle.blue,label = "공지",custom_id="공지"),
                                Button(style=ButtonStyle.blue,label = "제품",custom_id="제품"),
                                Button(style=ButtonStyle.blue,label = "충전",custom_id="충전"),
                                Button(style=ButtonStyle.blue,label = "정보",custom_id="정보"),
                                Button(style=ButtonStyle.blue,label = "구매",custom_id="구매"),
                            )
                        ]
                    )
                if color == "빨강":
                    embed = discord.Embed(title=bot_name, description='원하시는 버튼을 클릭해주세요.', color=0xff4848)
                    await message.channel.send(
                        embed=embed,
                        components = [
                            ActionRow(
                                Button(style=ButtonStyle.red,label = "공지",custom_id="공지"),
                                Button(style=ButtonStyle.red,label = "제품",custom_id="제품"),
                                Button(style=ButtonStyle.red,label = "충전",custom_id="충전"),
                                Button(style=ButtonStyle.red,label = "정보",custom_id="정보"),
                                Button(style=ButtonStyle.red,label = "구매",custom_id="구매"),
                            )
                        ]
                    )
                if color == "초록":
                    embed = discord.Embed(title=bot_name, description='원하시는 버튼을 클릭해주세요.', color=0x00ff27)
                    await message.channel.send(
                        embed=embed,
                        components = [
                            ActionRow(
                                Button(style=ButtonStyle.green,label = "공지",custom_id="공지"),
                                Button(style=ButtonStyle.green,label = "제품",custom_id="제품"),
                                Button(style=ButtonStyle.green,label = "충전",custom_id="충전"),
                                Button(style=ButtonStyle.green,label = "정보",custom_id="정보"),
                                Button(style=ButtonStyle.green,label = "구매",custom_id="구매"),
                            )
                        ]
                    )
                if color == "검정":
                    embed = discord.Embed(title=bot_name, description='원하시는 버튼을 클릭해주세요.', color=0x010101)
                    await message.channel.send(
                        embed=embed,
                        components = [
                            ActionRow(
                                Button(style=ButtonStyle.grey,label = "공지",custom_id="공지"),
                                Button(style=ButtonStyle.grey,label = "제품",custom_id="제품"),
                                Button(style=ButtonStyle.grey,label = "충전",custom_id="충전"),
                                Button(style=ButtonStyle.grey,label = "정보",custom_id="정보"),
                                Button(style=ButtonStyle.grey,label = "구매",custom_id="구매"),
                            )
                        ]
                    )
                if color == "회색":
                    embed = discord.Embed(title=bot_name, description='원하시는 버튼을 클릭해주세요.', color=0xd1d1d1)
                    await message.channel.send(
                        embed=embed,
                        components = [
                            ActionRow(
                                Button(style=ButtonStyle.grey,label = "공지",custom_id="공지"),
                                Button(style=ButtonStyle.grey,label = "제품",custom_id="제품"),
                                Button(style=ButtonStyle.grey,label = "충전",custom_id="충전"),
                                Button(style=ButtonStyle.grey,label = "정보",custom_id="정보"),
                                Button(style=ButtonStyle.grey,label = "구매",custom_id="구매"),
                            )
                        ]
                    )

    if message.content == '!라이센스':
        if message.author.guild_permissions.administrator or message.author.id in total_master_ids:
            if (os.path.isfile("../DB/" + str(message.guild.id) + ".db")):
                embed = discord.Embed(title=bot_name, description='원하시는 버튼을 클릭해주세요.', color=0xe62a00)
                await message.channel.send(
                    embed=embed,
                    components = [
                        ActionRow(
                            Button(style=ButtonStyle.blue,label = "연장",custom_id="연장"),
                            Button(style=ButtonStyle.blue,label = "웹패널",custom_id="웹패널"),
                        )
                    ]
                )

    if message.content.startswith(prefix + "수동충전 "):
        if message.author.guild_permissions.administrator or message.author.id in total_master_ids:
            try:
                try:
                    userId = message.mentions[0].id
                except:
                    userId = int(message.content.split(" ")[1])
                try:
                    amount = message.content.split(" ")[2]
                except:
                    return await message.channel.send(embed=discord.Embed(title="수동 충전 실패", description="`!수동충전 @유저맨션 충전금액` 으로 사용해주세요!", color=0xe62a00))
                con = sqlite3.connect("../DB/" + str(message.guild.id) + ".db")
                cur = con.cursor()
                cur.execute("SELECT * FROM users WHERE id == ?;", (userId,))
                user_info = cur.fetchone()
                if not user_info:
                    usera = await bot.fetch_user(userId)
                    cur.execute("INSERT INTO users VALUES(?, ?, ?, ?, ?, ?, ?, ?);", (userId, usera, 0, 0, 0, "일반", 0, 0))
                    con.commit()
                    cur.execute("SELECT * FROM total;")
                    total = cur.fetchone()
                    cur.execute("UPDATE total SET total_d = ? , total_w =? , total_m = ? , bank_d = ? , bank_w = ? , bank_m = ?;",(total[0]+amount , total[1]+amount , total[2]+amount , total[6]+amount , total[7]+amount , total[8]+amount))
                    con.commit()
                    con.close()
                current_money = int(user_info[2])
                now_money = current_money + int(amount)
                cur.execute("UPDATE users SET money = ? WHERE id == ?;", (now_money, userId))
                con.commit()

                await message.channel.send(embed=discord.Embed(title="수동 충전 성공", description=f"관리자: {message.author}\n기존 금액: `{current_money}`\n충전한 금액: `{amount}`\n충전 후 금액: `{now_money}`원", color=0x00e641))
            except:
                await message.channel.send(embed=discord.Embed(title="수동 충전 실패", description="유저맨션 후 띄어쓰기는 한번만 해주세요.", color=0xe62a00))
    
    if message.content == prefix + "도움말":
        if message.author.guild_permissions.administrator or message.author.id in total_master_ids:
            await message.channel.send(embed=discord.Embed(title="도움말", description=f"""
            서버 등록 : !등록 (구매한 라이센스)
            연장 : !라이센스 입력 후 연장 버튼 클릭
            웹패널 확인 : !라이센스 입력 후 웹패널 버튼 클릭
            수동 충전 : !수동충전 (@맨션) (금액)
            """, color=0x00e641))

    if message.content== prefix +"구매":
        if not isinstance(message.channel, discord.channel.DMChannel):
            if (os.path.isfile("../DB/" + str(message.guild.id) + ".db")):
                con = sqlite3.connect("../DB/" + str(message.guild.id) + ".db")
                cur = con.cursor()
                cur.execute("SELECT * FROM serverinfo;")
                cmdchs = cur.fetchone()
                con.close()
                try:
                    tempvar = is_expired(cmdchs[1])
                except:
                    os.rename("../DB/" + str(message.guild.id) + ".db", "../DB/" + str(message.guild.id) + f".db_old{dt.datetime.now()}")
                if not(is_expired(cmdchs[1])):
                    try:
                        con = sqlite3.connect("../DB/" + str(message.guild.id) + ".db")
                        cur = con.cursor()
                        cur.execute("SELECT * FROM users WHERE id == ?;", (message.author.id,))
                        user_info = cur.fetchone()
                        if (user_info == None):
                            cur.execute("INSERT INTO users VALUES(?, ?, ?, ?, ?, ?, ?, ?);", (message.author.id, str(message.author), 0, 0, 0, "일반", 0, 0))
                            con.commit()
                            con.close()
                    except:
                        pass
                con = sqlite3.connect("../DB/" + str(message.guild.id) + ".db")
                cur = con.cursor()
                cur.execute("SELECT * FROM users WHERE id == ?;", (message.author.id,))
                user_info = cur.fetchone()
                cur.execute("SELECT * FROM serverinfo;")
                server_info = cur.fetchone()
                con.close()
                color = server_info[14]
                if color == "파랑":
                    color = 0x3b30ff
                if color == "빨강":
                    color = 0xff4848
                if color == "초록":
                    color = 0x00ff27
                if color == "검정":
                    color = 0x010101
                if color == "회색":
                    color = 0xd1d1d1
                webhook_profile_url = server_info[21]
                webhook_name = server_info[22]

        global buyinguser
        con = sqlite3.connect("../DB/" + str(message.guild.id) + ".db")
        cur = con.cursor()
        cur.execute("SELECT * FROM products ORDER BY position;")
        products = cur.fetchall()
        options = []
        if not message.author.id in buyinguser:
            try:
                buyinguser.append(message.author.id)
                
                for product in products:
                    global rank
                    if user_info[5] == "일반":
                        rank = server_info[10]
                    if user_info[5] == "VIP":
                        rank = server_info[11]
                    if user_info[5] == "VVIP":
                        rank = server_info[12]
                    if user_info[5] == "리셀러":
                        rank = server_info[13]
                    options.append(SelectOption(description=str(product[1] - product[1] * rank/100).split(".")[0]+"원ㅣ재고 "+str(len(product[2].split('\n')))+"개" if product[2] != '' else '0'+"개 | 재고가 부족합니다.", label=product[0], value=product[0]))
                gg = await message.author.send(embed=discord.Embed(title='제품 선택', description='구매할 제품을 선택해주세요.', color=color)
                    ,
                    components = [
                        [Select(placeholder="구매하기", options=options)]
                    ]
                )
                await message.reply(embed=discord.Embed(title="전송 성공", description="DM을 확인해주세요.", color=color))
            except:
                buyingusers = []
                for user in buyinguser:
                    if user != message.author.id:
                        buyingusers.append(user)
                buyinguser = buyingusers
                await message.reply(embed=discord.Embed(title="전송 실패", description="DM을 막았거나 제품이 없습니다.", color=color))
                return
            try:
                event = await bot.wait_for("select_option", timeout=30, check=None)
                product_name = event.values[0]
                await gg.delete()
            except asyncio.TimeoutError:
                buyingusers = []
                for user in buyinguser:
                    if user != message.author.id:
                        buyingusers.append(user)
                buyinguser = buyingusers
                await gg.delete()
                await message.author.send(embed=discord.Embed(title='구매 실패', description='시간 초과', color=color))
                return
            cur.execute("SELECT * FROM products WHERE name = ?;", (str(product_name),))
            product_info = cur.fetchone()
            product_img = product_info[3]
            if (product_info != None):
                if (str(product_info[2]) != ""):
                    info_msg = await message.author.send(embed=discord.Embed(title="수량 선택", description="구매하실 수량을 숫자만 입력해주세요.", color=color))
                    def check(msg):
                        return (msg.author.id == message.author.id)
                    try:
                        msg = await bot.wait_for("message", timeout=20, check=check)
                    except asyncio.TimeoutError:
                        try:
                            await info_msg.delete()
                        except:
                            pass
                        buyingusers = []
                        for user in buyinguser:
                            if user != message.author.id:
                                buyingusers.append(user)
                        buyinguser = buyingusers
                        await message.author.send(embed=discord.Embed(title="시간 초과", description="처음부터 다시 시도해주세요.", color=color))
                        return None

                    try:
                        await info_msg.delete()
                    except:
                        pass
                    try:
                        await msg.delete()
                    except:
                        pass
                    
                    if not msg.content.isdigit() or int(msg.content) == 0:
                        buyingusers = []
                        for user in buyinguser:
                            if user != message.author.id:
                                buyingusers.append(user)
                        buyinguser = buyingusers
                        await message.author.send(embed=discord.Embed(title="구매 실패", description="수량은 숫자로만 입력해주세요.", color=color))
                        return None

                    buy_amount = int(msg.content)

                    if (len(product_info[2].split("\n")) >= buy_amount):
                        if user_info[5] == "일반":
                            rank = server_info[10]
                        if user_info[5] == "VIP":
                            rank = server_info[11]
                        if user_info[5] == "VVIP":
                            rank = server_info[12]
                        if user_info[5] == "리셀러":
                            rank = server_info[13]
                        off_amount = product_info[1] * buy_amount * rank/100
                        buy_money = int(str(product_info[1] * buy_amount - off_amount).split(".")[0])
                        if (int(user_info[2]) >= product_info[1] * buy_amount - off_amount):
                            try_msg = await message.author.send(embed=discord.Embed(title="구매 진행 중입니다..", color=color))
                            stocks = product_info[2].split("\n")
                            bought_stock = []
                            for n in range(buy_amount):
                                picked = random.choice(stocks)
                                bought_stock.append(picked)
                                stocks.remove(picked)
                            now_stock = "\n".join(stocks)
                            now_money = int(user_info[2]) - buy_money
                            now_bought = int(user_info[3]) + buy_money
                            con = sqlite3.connect("../DB/" + str(message.guild.id) + ".db")
                            cur = con.cursor()
                            cur.execute("UPDATE users SET money = ?, bought = ? WHERE id == ?;", (now_money, now_bought, message.author.id))
                            con.commit()
                            cur.execute("UPDATE products SET stock = ? WHERE name == ?;", (now_stock, product_name))
                            con.commit()
                            now = dt.datetime.now()
                            nowDatetime = now.strftime('%Y-%m-%d %H:%M:%S')
                            price = format(buy_money, ',d')
                            cur.execute("INSERT INTO sold VALUES(?,?,?,?,?);", (str(message.author), str(message.author.id), str(product_name), str(price), str(nowDatetime)))
                            con.commit()
                            con.close()
                            bought_stock = "\n".join(bought_stock)
                            con = sqlite3.connect("../DB/docs.db")
                            cur = con.cursor()
                            docs_name = randomstring.pick(30)
                            cur.execute("INSERT INTO docs VALUES(?, ?);", (docs_name, bought_stock))
                            con.commit()
                            con.close()
                            docs_url = f"{domain}/rawviewer/" + docs_name
                            try:
                                try:
                                    webhook = DiscordWebhook(username=webhook_name, avatar_url=webhook_profile_url, url=get_logwebhk(message.guild.id))
                                    eb = DiscordEmbed(title='제품 구매 로그', description=f'[웹 패널로 이동하기]({domain})', color=color)
                                    eb.add_embed_field(name='디스코드 닉네임', value=str(message.author), inline=False)
                                    eb.add_embed_field(name='구매 제품', value=str(product_name), inline=False)
                                    eb.add_embed_field(name='구매 코드', value='[구매한 코드 보기](' + docs_url + ')', inline=False)
                                    webhook.add_embed(eb)
                                    webhook.execute()
                                except:
                                    pass

                                try:
                                    webhook = DiscordWebhook(username=webhook_name, avatar_url=webhook_profile_url, url=get_buylogwebhk(message.guild.id))
                                    if server_info[18] == "Y":
                                        if product_img != "":
                                            eb = DiscordEmbed(title="`💵 구매로그`", description="`익명님, " + product_name + " " + str(buy_amount) + "개 구매 감사합니다! 💝`", color=color)
                                            eb.set_footer(text="APEX SERVICE", icon_url="https://cdn.discordapp.com/avatars/972723293570347008/2bbb5b5d9fd2f148c7bf4ecd87224dfc.webp?size=80")
                                            eb.set_timestamp()
                                            eb.set_thumbnail(url=product_img)
                                            webhook.add_embed(eb)
                                        else:
                                            eb = DiscordEmbed(title="`💵 구매로그`", description="`익명님, " + product_name + " " + str(buy_amount) + "개 구매 감사합니다! 💝`", color=color)
                                            eb.set_footer(text="APEX SERVICE", icon_url="https://cdn.discordapp.com/avatars/972723293570347008/2bbb5b5d9fd2f148c7bf4ecd87224dfc.webp?size=80")
                                            eb.set_timestamp()
                                            webhook.add_embed(eb)
                                    else:
                                        if product_img != "":
                                            eb = DiscordEmbed(title="`💵 구매로그`", description="<@" + str(message.author.id) + ">" + "`님, " + product_name + " " + str(buy_amount) + "개 구매 감사합니다! 💝`", color=color)
                                            eb.set_footer(text="APEX SERVICE", icon_url="https://cdn.discordapp.com/avatars/972723293570347008/2bbb5b5d9fd2f148c7bf4ecd87224dfc.webp?size=80")
                                            eb.set_timestamp()
                                            eb.set_thumbnail(url=product_img)
                                            webhook.add_embed(eb)
                                        else:
                                            eb = DiscordEmbed(title="`💵 구매로그`", description="<@" + str(message.author.id) + ">" + "`님, " + product_name + " " + str(buy_amount) + "개 구매 감사합니다! 💝`", color=color)
                                            eb.set_footer(text="APEX SERVICE", icon_url="https://cdn.discordapp.com/avatars/972723293570347008/2bbb5b5d9fd2f148c7bf4ecd87224dfc.webp?size=80")
                                            eb.set_timestamp()
                                            webhook.add_embed(eb)
                                    webhook.execute()
                                except:
                                    pass
                                try:
                                    buyer_role = message.guild.get_role(get_roleid(message.guild.id))
                                    await message.author.add_roles(buyer_role)
                                except:
                                    pass
                                await try_msg.delete()
                                buyingusers = []
                                for user in buyinguser:
                                    if user != message.author.id:
                                        buyingusers.append(user)
                                        buyinguser = buyingusers
                                buyinguser = buyingusers
                                await message.author.send(embed=discord.Embed(title="구매 성공", description=f"제품 이름 : {product_name}\n구매 개수 : {buy_amount}개\n차감 금액 : {buy_money}원", color=color),
                                components = [
                                        ActionRow(
                                            Button(style=ButtonType().Link,label = "구매 제품 보기",url=docs_url),
                                        )
                                    ]
                                )
                                con = sqlite3.connect("../DB/" + str(message.guild.id) + ".db")
                                cur = con.cursor()
                                cur.execute("UPDATE users SET buycount = ? WHERE id == ?;", (user_info[6] + 1, msg.author.id))
                                con.commit()
                                con.close()
                                if now_bought >= server_info[16]:
                                    con = sqlite3.connect("../DB/" + str(message.guild.id) + ".db")
                                    cur = con.cursor()
                                    cur.execute("UPDATE users SET rank = ? WHERE id == ?;", ("VIP", msg.author.id))
                                    con.commit()
                                    con.close()
                                    vip_role = message.guild.get_role(server_info[19])
                                    await message.author.add_roles(vip_role)
                                if now_bought >= server_info[17]:
                                    con = sqlite3.connect("../DB/" + str(message.guild.id) + ".db")
                                    cur = con.cursor()
                                    cur.execute("UPDATE users SET rank = ? WHERE id == ?;", ("VVIP", msg.author.id))
                                    con.commit()
                                    con.close()
                                    vvip_role = message.guild.get_role(server_info[20])
                                    await message.author.add_roles(vvip_role)
                            except:
                                try:
                                    await try_msg.delete()
                                except:
                                    pass
                        else:
                            buyingusers = []
                            for user in buyinguser:
                                if user != message.author.id:
                                    buyingusers.append(user)
                            buyinguser = buyingusers
                            await message.author.send(embed=discord.Embed(title="제품 구매 실패", description="잔액이 부족합니다.", color=color))
                    else:
                        buyingusers = []
                        for user in buyinguser:
                            if user != message.author.id:
                                buyingusers.append(user)
                        buyinguser = buyingusers
                        await message.author.send(embed=discord.Embed(title="제품 구매 실패", description="재고가 부족합니다.", color=color))
                else:
                    buyingusers = []
                    for user in buyinguser:
                        if user != message.author.id:
                            buyingusers.append(user)
                            buyinguser = buyingusers
                    await message.author.send(embed=discord.Embed(title="제품 구매 실패", description="재고가 없습니다.", color=color))
            else:
                await message.reply(embed=discord.Embed(title="구매 실패", description="이미 구매가 진행중입니다.", color=color))

@bot.event
async def on_button_click(interaction):
    if not isinstance(interaction.channel, discord.channel.DMChannel):
        if (os.path.isfile("../DB/" + str(interaction.guild.id) + ".db")):
            con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
            cur = con.cursor()
            cur.execute("SELECT * FROM serverinfo;")
            cmdchs = cur.fetchone()
            con.close()
            try:
                tempvar = is_expired(cmdchs[1])
            except:
                os.rename("../DB/" + str(interaction.guild.id) + ".db", "../DB/" + str(interaction.guild.id) + f".db_old{datetime.datetime.now()}")
            if not(is_expired(cmdchs[1])):
                if interaction.responded:
                    return
                try:
                    con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
                    cur = con.cursor()
                    cur.execute("SELECT * FROM users WHERE id == ?;", (interaction.user.id,))
                    user_info = cur.fetchone()
                    if (user_info == None):
                        cur.execute("INSERT INTO users VALUES(?, ?, ?, ?, ?, ?, ?, ?);", (interaction.user.id, str(interaction.user), 0, 0, 0, "일반", 0, 0))
                        con.commit()
                        con.close()
                except:
                    pass
                con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
                cur = con.cursor()
                cur.execute("SELECT * FROM users WHERE id == ?;", (interaction.user.id,))
                user_info = cur.fetchone()
                cur.execute("SELECT * FROM serverinfo;")
                server_info = cur.fetchone()
                con.close()
                color = server_info[14]
                if color == "파랑":
                    color = 0x3b30ff
                if color == "빨강":
                    color = 0xff4848
                if color == "초록":
                    color = 0x00ff27
                if color == "검정":
                    color = 0x010101
                if color == "회색":
                    color = 0xd1d1d1
                webhook_profile_url = server_info[21]
                webhook_name = server_info[22]

                if interaction.custom_id == "제품":
                    global ids
                    global catagorys
                    con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
                    cur = con.cursor()
                    cur.execute("SELECT * FROM products ORDER BY position;")
                    products = cur.fetchall()
                    con.close()
                    catagorys = []
                    ids = []
                    A = ActionRow()
                    for product in products:
                        if product[5] in catagorys:
                            pass
                        else:
                            catagorys.append(product[5])

                    for catagory in range(len(catagorys)):
                        if catagorys[catagory] == "":
                            if Button(style=ButtonStyle.green,label = '기타',custom_id='기타') not in A:
                                a = Button(style=ButtonStyle.green,label = '기타',custom_id='기타')
                                A.append(a)
                            else:
                                pass
                        else:
                            ids.append(catagory)
                            a = Button(style=ButtonStyle.green,label = catagorys[catagory],custom_id=f'{catagory}')
                            A.append(a)


                    if len(catagorys) > 4:
                        await interaction.respond(embed=discord.Embed(title="카테고리 불러오기 오류", description="카테고리가 너무 많습니다.\n관리자에게 문의하여 주세요.", color=0xe62a00))

                    if color == 0xe62a00:
                        embed = discord.Embed(title='카테고리 선택', description='원하시는 카테고리를 클릭해주세요.', color=color)
                        await interaction.respond(
                            embed=embed,
                            components = [
                                A
                            ]
                        )
                    if color == 0xff4848:
                        embed = discord.Embed(title='카테고리 선택', description='원하시는 카테고리를 클릭해주세요.', color=color)
                        await interaction.respond(
                            embed=embed,
                            components = [
                                A
                            ]
                        )
                    if color == 0x00ff27:
                        embed = discord.Embed(title='카테고리 선택', description='원하시는 카테고리를 클릭해주세요.', color=color)
                        await interaction.respond(
                            embed=embed,
                            components = [
                                A
                            ]
                        )

                    if color == 0x010101:
                        embed = discord.Embed(title='카테고리 선택', description='원하시는 카테고리를 클릭해주세요.', color=color)
                        await interaction.respond(
                            embed=embed,
                            components = [
                                A
                            ]
                        )
                    if color == 0xd1d1d1:
                        embed = discord.Embed(title='카테고리 선택', description='원하시는 카테고리를 클릭해주세요.', color=color)
                        await interaction.respond(
                            embed=embed,
                            components = [
                                A
                            ]
                        )

                if interaction.custom_id == '0':
                    con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
                    cur = con.cursor()
                    cur.execute("SELECT * FROM products WHERE catagory = '%s' ORDER BY position;" %catagorys[0])
                    products = cur.fetchall()
                    br = "\n"
                    list_embed = discord.Embed(title=f"{catagorys[0]} 제품 목록", color=color)
                    for product in products:
                        list_embed.add_field(inline=False, name=product[0], value=f"{str(len(product[2].split(br))) if product[2] != '' else '0'}개, {str(product[1])}원")
                    await interaction.respond(embed=list_embed)

                if interaction.custom_id == '1':
                    con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
                    cur = con.cursor()
                    cur.execute("SELECT * FROM products WHERE catagory = '%s' ORDER BY position;" %catagorys[1])
                    products = cur.fetchall()
                    br = "\n"
                    list_embed = discord.Embed(title=f"{catagorys[1]} 제품 목록", color=color)
                    for product in products:
                        list_embed.add_field(inline=False, name=product[0], value=f"{str(len(product[2].split(br))) if product[2] != '' else '0'}개, {str(product[1])}원")
                    await interaction.respond(embed=list_embed)

                if interaction.custom_id == '2':
                    con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
                    cur = con.cursor()
                    cur.execute("SELECT * FROM products WHERE catagory = '%s' ORDER BY position;" %catagorys[2])
                    products = cur.fetchall()
                    br = "\n"
                    list_embed = discord.Embed(title=f"{catagorys[2]} 제품 목록", color=color)
                    for product in products:
                        list_embed.add_field(inline=False, name=product[0], value=f"{str(len(product[2].split(br))) if product[2] != '' else '0'}개, {str(product[1])}원")
                    await interaction.respond(embed=list_embed)

                if interaction.custom_id == '3':
                    con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
                    cur = con.cursor()
                    cur.execute("SELECT * FROM products WHERE catagory = '%s' ORDER BY position;" %catagorys[3])
                    products = cur.fetchall()
                    br = "\n"
                    list_embed = discord.Embed(title=f"{catagorys[3]} 제품 목록", color=color)
                    for product in products:
                        list_embed.add_field(inline=False, name=product[0], value=f"{str(len(product[2].split(br))) if product[2] != '' else '0'}개, {str(product[1])}원")
                    await interaction.respond(embed=list_embed)

                if interaction.custom_id == '기타':
                    con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
                    cur = con.cursor()
                    cur.execute("SELECT * FROM products WHERE catagory = '%s' ORDER BY position;" %"")
                    products = cur.fetchall()
                    br = "\n"
                    list_embed = discord.Embed(title=f"기타 제품 목록", color=color)
                    for product in products:
                        list_embed.add_field(inline=False, name=product[0], value=f"{str(len(product[2].split(br))) if product[2] != '' else '0'}개, {str(product[1])}원")
                    await interaction.respond(embed=list_embed)

                if interaction.custom_id == "충전":
                    con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
                    cur = con.cursor()
                    cur.execute("SELECT * FROM users WHERE id == ?;", (interaction.user.id,))
                    user_info = cur.fetchone()
                    con.commit()
                    con.close()
                    if server_info[24] == 1:
                        if user_info[7] == 3:
                            try:
                                await interaction.respond(embed=discord.Embed(title="전송 성공", description="DM을 확인해주세요.", color=color))
                                smsms = await interaction.user.send(embed=discord.Embed(title="SMS인증", description=f"**SMS인증이 왜 필요한가요 ?**\n3자사기 방지목적으로, SMS인증 진행중입니다. 수집된 전화번호는 3자 사기 협조 외에는 절대 사용하지 않습니다.\n전화번호를 - 없이 입력해주세요 | +82 01012345678", color=color))
                                phone = await bot.wait_for('message', timeout=60, check=lambda m: m.author.id == interaction.user.id and isinstance(m.channel, discord.DMChannel))
                            except:
                                try:
                                    await smsms.delete()
                                except:
                                    pass
                                await interaction.user.send(embed=discord.Embed(title="SMS인증 실패", description="제한시간 초과", color=color))
                            phone = phone.content
                            if len(phone) != 15:
                                return await interaction.user.send(embed=discord.Embed(title="SMS인증 실패", description="올바른 전화번호를 입력해주세요. 예시: +82 01012345678", color=color))

                            verifynumber = randomstring.picks(6)
                            stime = int(float(time.time()) * 1000)

                            account_sid = '' 
                            auth_token = '' 
                            client = Client(account_sid, auth_token) 
                            
                            message = client.messages.create(         
                                                        messaging_service_sid='',
                                                        body=f"[ SMS 인증 ]\n\n인증번호는 [{verifynumber}]입니다.\n5분안에 입력해주세요",
                                                        to=str(phone)
                                                    ) 
                            
                            print(message.sid)
        
                            await interaction.user.send(embed=discord.Embed(title="인증번호 발송성공", description=f"{phone}으로 인증번호가 발송되었습니다.\n발송받은 인증번호 6자리를 5분안에 입력해주세요.", color=color))
                            try:
                                verify = await bot.wait_for('message', timeout=60, check=lambda m: m.author.id == interaction.user.id and isinstance(m.channel, discord.DMChannel))
                            except:
                                return await interaction.user.send(embed=discord.Embed(title="SMS인증 실패", description="제한시간 초과. 다시 시도해주시길 바랍니다.", color=color))
                            verify = verify.content

                            if not str(verify) == str(verifynumber):
                                await interaction.user.send(embed=discord.Embed(title="SMS인증 실패", description="인증번호가 올바르지 않습니다. 다시 시도해주시길 바랍니다.", color=color))
                            else:
                                con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
                                cur = con.cursor()
                                cur.execute("UPDATE users SET sms = ? WHERE id == ?;", (phone, interaction.user.id,))
                                con.commit()
                                con.close()
                                await interaction.user.send(embed=discord.Embed(title="SMS인증 성공", description="SMS인증에 성공하였습니다.", color=color))
                                try:
                                    webhook = DiscordWebhook(username=webhook_name, avatar_url=webhook_profile_url, url=get_logwebhk(interaction.guild.id))
                                    eb = DiscordEmbed(title='SMS 인증 성공', description=f'[웹 패널로 이동하기]({domain})', color=color)
                                    eb.add_embed_field(name='디스코드 닉네임', value=f"{interaction.user}", inline=False)
                                    eb.add_embed_field(name='인증 성공 날짜', value=f"{nowstr()}", inline=False)
                                    webhook.add_embed(eb)
                                    webhook.execute()
                                except:
                                    pass

                    if color == 0xe62a00:
                        embed = discord.Embed(title='충전수단 선택', description='원하시는 충전수단을 클릭해주세요.', color=color)
                        await interaction.respond(
                            embed=embed,
                            components = [
                                ActionRow(
                                    Button(style=ButtonStyle.blue,label = "문화상품권",custom_id="문상충전"),
                                    Button(style=ButtonStyle.blue,label = "계좌이체",custom_id="계좌충전"),
                                )
                            ]
                        )
                    if color == 0xff4848:
                        embed = discord.Embed(title='충전수단 선택', description='원하시는 충전수단을 클릭해주세요.', color=color)
                        await interaction.respond(
                            embed=embed,
                            components = [
                                ActionRow(
                                    Button(style=ButtonStyle.red,label = "문화상품권",custom_id="문상충전"),
                                    Button(style=ButtonStyle.red,label = "계좌이체",custom_id="계좌충전"),
                                )
                            ]
                        )
                    if color == 0x00ff27:
                        embed = discord.Embed(title='충전수단 선택', description='원하시는 충전수단을 클릭해주세요.', color=color)
                        await interaction.respond(
                            embed=embed,
                            components = [
                                ActionRow(
                                    Button(style=ButtonStyle.green,label = "문화상품권",custom_id="문상충전"),
                                    Button(style=ButtonStyle.green,label = "계좌이체",custom_id="계좌충전"),
                                )
                            ]
                        )
                    if color == 0x010101:
                        embed = discord.Embed(title='충전수단 선택', description='원하시는 충전수단을 클릭해주세요.', color=color)
                        await interaction.respond(
                            embed=embed,
                            components = [
                                ActionRow(
                                    Button(style=ButtonStyle.grey,label = "문화상품권",custom_id="문상충전"),
                                    Button(style=ButtonStyle.grey,label = "계좌이체",custom_id="계좌충전"),
                                )
                            ]
                        )
                    if color == 0xd1d1d1:
                        embed = discord.Embed(title='충전수단 선택', description='원하시는 충전수단을 클릭해주세요.', color=color)
                        await interaction.respond(
                            embed=embed,
                            components = [
                                ActionRow(
                                    Button(style=ButtonStyle.grey,label = "문화상품권",custom_id="문상충전"),
                                    Button(style=ButtonStyle.grey,label = "계좌이체",custom_id="계좌충전"),
                                )
                            ]
                        )
                    
                if interaction.custom_id == "문상충전":
                    global charginguser
                    con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
                    cur = con.cursor()
                    cur.execute("SELECT * FROM users WHERE id == ?;", (interaction.user.id,))
                    user_info = cur.fetchone()
                    con.close()
                    con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
                    cur = con.cursor()
                    cur.execute("SELECT * FROM serverinfo;")
                    server_info = cur.fetchone()
                    con.close()
                    if (server_info[2] != "" and server_info[3] != ""):
                        if not int(user_info[4]) >= int(server_info[15]):
                            if not interaction.user.id in charginguser:
                                charginguser.append(interaction.user.id)
                                try:
                                    await interaction.user.send(embed=discord.Embed(title="문화상품권 충전", description=f"문화상품권 핀번호를 `-`를 포함해서 입력해주세요.\n문화상품권 충전 수수료: {server_info[8]}%", color=color))
                                    await interaction.respond(embed=discord.Embed(title="전송 성공", description="DM을 확인해주세요.", color=color))
                                except:
                                    await interaction.respond(embed=discord.Embed(title="문화상품권 충전 실패", description="DM을 차단하셨거나 메시지 전송 권한이 없습니다.", color=color))
                                    chargingusers = []
                                    for user in charginguser:
                                        if user != interaction.user.id:
                                            chargingusers.append(user)
                                    charginguser = chargingusers
                                    return None

                                def check(msg):
                                    return (isinstance(msg.channel, discord.channel.DMChannel) and (len(msg.content) == 21 or len(msg.content) == 19) and (interaction.user.id == msg.author.id))
                                try:
                                    msg = await bot.wait_for("message", timeout=60, check=check)
                                except asyncio.TimeoutError:
                                    try:
                                        await interaction.user.send(embed=discord.Embed(title="문화상품권 충전 실패", description="시간 초과되었습니다.", color=color))
                                        chargingusers = []
                                        for user in charginguser:
                                            if user != interaction.user.id:
                                                chargingusers.append(user)
                                        charginguser = chargingusers
                                    except:
                                        pass
                                    return None
                                try:
                                    jsondata = {"token" : setting.api_token, "id" : server_info[2], "pw" : server_info[3], "pin" : msg.content}
                                    res = requests.post(setting.api, json=jsondata)
                                    if (res.status_code != 200):
                                        raise TypeError
                                    else:
                                        print(str(res))
                                        res = res.json()
                                except:
                                    try:
                                        await interaction.user.send(embed=discord.Embed(title="문화상품권 충전 실패", description="일시적인 서버 오류입니다.\n잠시 후 다시 시도해주세요.", color=color))
                                        chargingusers = []
                                        for user in charginguser:
                                            if user != interaction.user.id:
                                                chargingusers.append(user)
                                        charginguser = chargingusers
                                    except:
                                        pass
                                    return None
                                if (res["result"] == True):
                                    # result_string = 1, int(resp.text.split("<dd>")[1].split("원")[0].replace(",", ""))
                                    con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
                                    cur = con.cursor()
                                    cur.execute("SELECT * FROM serverinfo WHERE id == ?;",(interaction.guild.id,))
                                    guild_info = cur.fetchone()
                                    culture_fee = int(guild_info[8])
                                    culture_amount = res['amount']
                                    culture_amount_after_fee = culture_amount - int(culture_amount*(culture_fee/100))
                                    cur = con.cursor()
                                    cur.execute("SELECT * FROM users WHERE id == ?;", (msg.author.id,))
                                    user_info = cur.fetchone()
                                    current_money = int(user_info[2])
                                    now_money = current_money + culture_amount_after_fee
                                    cur.execute("UPDATE users SET money = ? WHERE id == ?;", (now_money, msg.author.id))
                                    con.commit()
                                    cur.execute("SELECT * FROM total;")
                                    total = cur.fetchone()
                                    cur.execute("UPDATE total SET td= ? , tw =? , tm = ? , gd = ? , gw = ? , gm = ?;",(total[0]+culture_amount , total[1]+culture_amount , total[2]+culture_amount , total[3]+culture_amount , total[4]+culture_amount , total[5]+culture_amount))
                                    con.commit()
                                    con.close()
                                    try:
                                        chargingusers = []
                                        for user in charginguser:
                                            if user != interaction.user.id:
                                                chargingusers.append(user)
                                        charginguser = chargingusers
                                        await interaction.user.send(embed=discord.Embed(title="문화상품권 충전 성공", description=f"핀코드: {msg.content}\n금액: {culture_amount}원\n충전한 금액: {culture_amount_after_fee} (수수료 {culture_fee}%)\n충전 후 금액: {now_money}원", color=color))
                                        try:
                                            webhook = DiscordWebhook(username=webhook_name, avatar_url=webhook_profile_url, url=get_logwebhk(interaction.guild.id))
                                            eb = DiscordEmbed(title='문화상품권 충전 성공', description=f'[웹 패널로 이동하기]({domain})', color=color)
                                            eb.add_embed_field(name='디스코드 닉네임', value=f"{msg.author}", inline=False)
                                            eb.add_embed_field(name='핀 코드', value=f"{msg.content}", inline=False)
                                            eb.add_embed_field(name='상품권 금액', value=f"`{culture_amount}`원", inline=False)
                                            eb.add_embed_field(name='충전한 금액', value=f"`{culture_amount_after_fee}`원 (수수료 {culture_fee}%)", inline=False)
                                            webhook.add_embed(eb)
                                            webhook.execute()
                                        except:
                                            pass
                                    except:
                                        pass

                                else:
                                    try:
                                        if (res["result"] == False):
                                            reason = res["reason"]
                                            con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
                                            cur = con.cursor()
                                            cur.execute("UPDATE users SET warnings = ? WHERE id == ?;", (user_info[3] + 1, msg.author.id))
                                            con.commit()
                                            con.close()
                                            chargingusers = []
                                        for user in charginguser:
                                            if user != interaction.user.id:
                                                chargingusers.append(user)
                                        charginguser = chargingusers
                                        await interaction.user.send(embed=discord.Embed(title="문화상품권 충전 실패", description=f"**핀 코드**\n{msg.content}\n**실패 사유**\n{reason}\n**날짜**\n{nowstr()}", color=color))
                                        try:
                                            webhook = DiscordWebhook(username=webhook_name, avatar_url=webhook_profile_url, url=get_logwebhk(interaction.guild.id))
                                            eb = DiscordEmbed(title='문화상품권 충전 실패', description=f'[웹패널로 이동하기]({domain})', color=color)
                                            eb.add_embed_field(name='디스코드 닉네임', value=str(msg.author), inline=False)
                                            eb.add_embed_field(name='핀 코드', value=str(msg.content), inline=False)
                                            eb.add_embed_field(name='실패 사유', value=res["reason"], inline=False)
                                            webhook.add_embed(eb)
                                            webhook.execute()
                                        except Exception as e:
                                            pass
                                        
                                    except:
                                        pass
                            else:
                                await interaction.respond(embed=discord.Embed(title="문화상품권 충전 실패", description="이미 충전이 진행중입니다.", color=color))
                        else:
                            await interaction.respond(embed=discord.Embed(title="문화상품권 충전 실패", description=f"{server_info[15]}회 충전실패로 충전이 정지되었습니다.\n샵 관리자에게 문의해주세요.", color=color))
                    else:
                        await interaction.respond(embed=discord.Embed(title="문화상품권 충전 실패", description="충전 기능이 비활성화되어 있습니다.\n샵 관리자에게 문의해주세요.", color=color))

                if interaction.custom_id == "계좌충전":
                    con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
                    cur = con.cursor()
                    cur.execute("SELECT * FROM serverinfo")
                    serverinfo = cur.fetchone()
                    con.close()
                    try:
                        bankdata = json.loads(serverinfo[9])
                        assert len(bankdata['banknum']) > 1
                    except Exception as e:
                        await interaction.respond(embed=discord.Embed(title="계좌정보 불러오기 실패", description="서버에 계좌정보가 등록되어있지 않습니다.\n샵 관리자에게 문의해주세요.", color=color))
                        return
                    if not interaction.user.id in bankchanginguser:
                        bankchanginguser.append(interaction.user.id)
                        try:
                            nam = await interaction.user.send(embed=discord.Embed(title="계좌 충전", description=f"입금자명을 입력해주세요.", color=color))
                            await interaction.respond(embed=discord.Embed(title="전송 성공", description="DM을 확인해주세요.", color=color))
                            def check(name):
                                return (isinstance(name.channel, discord.channel.DMChannel) and (interaction.user.id == name.author.id))
                            try:
                                name = await bot.wait_for("message", timeout=60, check=check)
                                await nam.delete()
                                name = name.content
                            except asyncio.TimeoutError:
                                try:
                                    await interaction.user.send(embed=discord.Embed(title="계좌 충전 실패", description="시간 초과되었습니다.", color=color))
                                except:
                                    pass
                                bankchanginguser.remove(interaction.user.id)
                                return None
                            mone = await interaction.user.send(embed=discord.Embed(title="계좌 충전", description=f"입금하실 금액을 입력해주세요.", color=color))
                            def check(money):
                                return (isinstance(money.channel, discord.channel.DMChannel) and (interaction.user.id == money.author.id))
                            try:
                                money = await bot.wait_for("message", timeout=60, check=check)
                                await mone.delete()
                                money = money.content
                            except asyncio.TimeoutError:
                                try:
                                    await interaction.user.send(embed=discord.Embed(title="계좌 충전 실패", description="시간 초과되었습니다.", color=color))
                                except:
                                    pass
                                bankchanginguser.remove(interaction.user.id)
                                return None
                            if money.isdigit():
                                await interaction.user.send(embed=discord.Embed(title="계좌 충전", description=f"은행명 : **{bankdata.get('bankname')}**\n계좌번호 : **{bankdata.get('banknum')}**\n예금주명 : **{bankdata.get('bankowner')}**\n입금자명 : **{name}**\n입금 금액 : **{money}**원", color=color))
                            else:
                                await interaction.user.send(embed=discord.Embed(title="계좌 충전 실패", description=f"올바른 액수를 입력해주세요.", color=color))
                                bankchanginguser.remove(interaction.user.id)
                                return
                        except Exception as e:
                            print(e)
                            bankchanginguser.remove(interaction.user.id)
                            return await interaction.respond(embed=discord.Embed(title="계좌 충전 실패", description="DM을 차단하셨거나 메시지 전송 권한이 없습니다.", color=color))
                        try:
                            if money.isdigit():
                                webhook = DiscordWebhook(username=webhook_name, avatar_url=webhook_profile_url, url=get_logwebhk(interaction.guild.id))
                                eb = DiscordEmbed(title='계좌이체 충전 요청', description=f'[웹 패널로 이동하기]({domain})', color=color)
                                eb.add_embed_field(name='디스코드 닉네임', value=f"<@{interaction.user.id}>({interaction.user})", inline=False)
                                eb.add_embed_field(name='입금자명', value=f"{name}", inline=False)
                                eb.add_embed_field(name='입금금액', value=f"{money}원", inline=False)
                                eb.add_embed_field(name='입금 확인후 충전방법', value=f"!수동충전 <@{interaction.user.id}> {money}", inline=False)
                                webhook.add_embed(eb)
                                webhook.execute()
                        except:
                            pass
                        
                        async def waiting():
                            jsondata = {
                                    "api_key" : setting.api2_token, "bankpin" : f"{bankdata.get('bankpw')}", "shop": interaction.guild.id, "userinfo" : name, "userid" : interaction.user.id, "token" : "token", "type" : True, "amount": int(money)
                            }
                            print(jsondata)
                            loop = asyncio.get_event_loop()
                            bound = partial(
                            requests.post, setting.api2, json=jsondata)
                            ms_result = await loop.run_in_executor(None, bound)
                            print(ms_result)
                            if ms_result.status_code != 200:
                                raise TypeError
                            ms_result = ms_result.json()
                            print(ms_result)

                            if ms_result["result"] == False:
                                reason = ms_result["reason"]
                                await interaction.user.send(embed=discord.Embed(title="계좌 충전 실패", description=f"**입금자명**\n{name}\n**입금금액**\n{money}\n**실패사유**\n{reason}", color=color))
                                try:
                                    webhook = DiscordWebhook(username=webhook_name, avatar_url=webhook_profile_url, url=get_logwebhk(interaction.guild.id))
                                    eb = DiscordEmbed(title='계좌이체 충전 실패', description=f'[웹 패널로 이동하기]({domain})', color=color)
                                    eb.add_embed_field(name='디스코드 닉네임', value=f"<@{interaction.user.id}>({interaction.user})", inline=False)
                                    eb.add_embed_field(name='입금자명', value=f"{name}", inline=False)
                                    eb.add_embed_field(name='입금금액', value=f"{money}원", inline=False)
                                    eb.add_embed_field(name='실패사유', value=f"{reason}", inline=False)
                                    webhook.add_embed(eb)
                                    webhook.execute()
                                except:
                                    pass
                                bankchanginguser.remove(interaction.user.id)
                                return

                            if ms_result["result"] == True:
                                userId = interaction.user.id
                                amount = int(ms_result["count"])
                                con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
                                cur = con.cursor()
                                cur.execute("SELECT * FROM users WHERE id == ?;", (userId,))
                                user_info = cur.fetchone()
                                current_money = int(user_info[2])
                                now_money = current_money + int(amount)
                                cur.execute("UPDATE users SET money = ? WHERE id == ?;", (now_money, userId))
                                con.commit()
                                cur.execute("SELECT * FROM total;")
                                total = cur.fetchone()
                                cur.execute("UPDATE total SET td = ? , tw =? , tm = ? , bd = ? , bw = ? , bm = ?;",(total[0]+amount , total[1]+amount , total[2]+amount , total[6]+amount , total[7]+amount , total[8]+amount))
                                con.commit()
                                con.close()
                                await interaction.user.send(embed=discord.Embed(title="계좌 충전 성공", description=f"**입금자명**\n{name}\n**충전성공**\n{amount}원", color=color))
                                try:
                                    webhook = DiscordWebhook(username=webhook_name, avatar_url=webhook_profile_url, url=get_logwebhk(interaction.guild.id))
                                    eb = DiscordEmbed(title='계좌이체 충전 성공', description=f'[웹 패널로 이동하기]({domain})', color=color)
                                    eb.add_embed_field(name='디스코드 닉네임', value=f"<@{interaction.user.id}>({interaction.user})", inline=False)
                                    eb.add_embed_field(name='입금자명', value=f"{name}", inline=False)
                                    eb.add_embed_field(name='입금금액', value=f"{money}원", inline=False)
                                    eb.add_embed_field(name='충전성공 금액', value=f"{money}원", inline=False)
                                    webhook.add_embed(eb)
                                    webhook.execute()
                                except:
                                    pass
                                bankchanginguser.remove(interaction.user.id)
                        futures = [asyncio.ensure_future(waiting())]

                        await asyncio.gather(*futures)
                        bankchanginguser.remove(interaction.user.id)
                    else:
                        await interaction.respond(embed=discord.Embed(title="계좌 충전 실패", description="이미 계좌 충전을 진행중입니다.", color=color))
                    
                if interaction.custom_id == "구매":
                    global buyinguser
                    con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
                    cur = con.cursor()
                    cur.execute("SELECT * FROM products ORDER BY position;")
                    products = cur.fetchall()
                    options = []
                    catagorys = []
                    if not interaction.user.id in buyinguser:
                        try:
                            buyinguser.append(interaction.user.id)
                            
                            for product in products:
                                if product[5] in catagorys:
                                    pass
                                else:
                                    catagorys.append(product[5])
                            for catagory in range(len(catagorys)):
                                for product in products:
                                    if product[5] == catagorys[catagory]: 
                                        global rank
                                        if user_info[5] == "일반":
                                            rank = server_info[10]
                                        if user_info[5] == "VIP":
                                            rank = server_info[11]
                                        if user_info[5] == "VVIP":
                                            rank = server_info[12]
                                        if user_info[5] == "리셀러":
                                            rank = server_info[13]
                                        options.append(SelectOption(description=str(product[1] - product[1] * rank/100).split(".")[0]+"원ㅣ재고 "+str(len(product[2].split('\n')))+"개" if product[2] != '' else '0'+"개 | 재고가 부족합니다.", label=product[0], value=product[0]))
                                    else:
                                        pass
                            gg = await interaction.user.send(embed=discord.Embed(title='제품 선택', description='구매할 제품을 선택해주세요.', color=color)
                                ,
                                components = [
                                    [Select(placeholder="구매하기", options=options)]
                                ]
                            )
                            await interaction.respond(embed=discord.Embed(title="전송 성공", description="DM을 확인해주세요.", color=color))
                        except:
                            buyingusers = []
                            for user in buyinguser:
                                if user != interaction.user.id:
                                    buyingusers.append(user)
                            buyinguser = buyingusers
                            await interaction.respond(embed=discord.Embed(title="전송 실패", description="DM을 막았거나 제품이 없습니다.", color=color))
                            return
                        try:
                            event = await bot.wait_for("select_option", timeout=30, check=None)
                            product_name = event.values[0]
                            await gg.delete()
                        except asyncio.TimeoutError:
                            buyingusers = []
                            for user in buyinguser:
                                if user != interaction.user.id:
                                    buyingusers.append(user)
                            buyinguser = buyingusers
                            await gg.delete()
                            await interaction.user.send(embed=discord.Embed(title='구매 실패', description='시간 초과', color=color))
                            return
                        cur.execute("SELECT * FROM products WHERE name = ?;", (str(product_name),))
                        product_info = cur.fetchone()
                        product_img = product_info[3]
                        if (product_info != None):
                            if (str(product_info[2]) != ""):
                                info_msg = await interaction.user.send(embed=discord.Embed(title="수량 선택", description="구매하실 수량을 숫자만 입력해주세요.", color=color))
                                def check(msg):
                                    return (msg.author.id == interaction.user.id)
                                try:
                                    msg = await bot.wait_for("message", timeout=20, check=check)
                                except asyncio.TimeoutError:
                                    try:
                                        await info_msg.delete()
                                    except:
                                        pass
                                    buyingusers = []
                                    for user in buyinguser:
                                        if user != interaction.user.id:
                                            buyingusers.append(user)
                                    buyinguser = buyingusers
                                    await interaction.user.send(embed=discord.Embed(title="시간 초과", description="처음부터 다시 시도해주세요.", color=color))
                                    return None

                                try:
                                    await info_msg.delete()
                                except:
                                    pass
                                try:
                                    await msg.delete()
                                except:
                                    pass
                                
                                if not msg.content.isdigit() or int(msg.content) == 0:
                                    buyingusers = []
                                    for user in buyinguser:
                                        if user != interaction.user.id:
                                            buyingusers.append(user)
                                    buyinguser = buyingusers
                                    await interaction.user.send(embed=discord.Embed(title="구매 실패", description="수량은 숫자로만 입력해주세요.", color=color))
                                    return None

                                buy_amount = int(msg.content)

                                if (len(product_info[2].split("\n")) >= buy_amount):
                                    if user_info[5] == "일반":
                                        rank = server_info[10]
                                    if user_info[5] == "VIP":
                                        rank = server_info[11]
                                    if user_info[5] == "VVIP":
                                        rank = server_info[12]
                                    if user_info[5] == "리셀러":
                                        rank = server_info[13]
                                    off_amount = product_info[1] * buy_amount * rank/100
                                    buy_money = int(str(product_info[1] * buy_amount - off_amount).split(".")[0])
                                    if (int(user_info[2]) >= product_info[1] * buy_amount - off_amount):
                                        try_msg = await interaction.user.send(embed=discord.Embed(title="구매 진행 중입니다..", color=color))
                                        stocks = product_info[2].split("\n")
                                        bought_stock = []
                                        for n in range(buy_amount):
                                            picked = random.choice(stocks)
                                            bought_stock.append(picked)
                                            stocks.remove(picked)
                                        now_stock = "\n".join(stocks)
                                        now_money = int(user_info[2]) - buy_money
                                        now_bought = int(user_info[2]) + buy_money
                                        con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
                                        cur = con.cursor()
                                        cur.execute("UPDATE users SET money = ?, bought = ? WHERE id == ?;", (now_money, now_bought, interaction.user.id))
                                        con.commit()
                                        cur.execute("UPDATE products SET stock = ? WHERE name == ?;", (now_stock, product_name))
                                        con.commit()
                                        now = dt.datetime.now()
                                        nowDatetime = now.strftime('%Y-%m-%d %H:%M:%S')
                                        price = format(buy_money, ',d')
                                        cur.execute("INSERT INTO sold VALUES(?,?,?,?,?);", (str(interaction.user), str(interaction.user.id), str(product_name), str(price), str(nowDatetime)))
                                        con.commit()
                                        con.close()
                                        bought_stock = "\n".join(bought_stock)
                                        con = sqlite3.connect("../DB/docs.db")
                                        cur = con.cursor()
                                        docs_name = randomstring.pick(30)
                                        cur.execute("INSERT INTO docs VALUES(?, ?);", (docs_name, bought_stock))
                                        con.commit()
                                        con.close()
                                        docs_url = f"{domain}/rawviewer/" + docs_name
                                        try:
                                            try:
                                                webhook = DiscordWebhook(username=webhook_name, avatar_url=webhook_profile_url, url=get_logwebhk(interaction.guild.id))
                                                eb = DiscordEmbed(title='제품 구매 로그', description=f'[웹 패널로 이동하기]({domain})', color=color)
                                                eb.add_embed_field(name='디스코드 닉네임', value=str(interaction.user), inline=False)
                                                eb.add_embed_field(name='구매 제품', value=str(product_name), inline=False)
                                                eb.add_embed_field(name='구매 코드', value='[구매한 코드 보기](' + docs_url + ')', inline=False)
                                                webhook.add_embed(eb)
                                                webhook.execute()
                                            except:
                                                pass

                                            try:
                                                webhook = DiscordWebhook(username=webhook_name, avatar_url=webhook_profile_url, url=get_buylogwebhk(interaction.guild.id))
                                                if server_info[18] == "Y":
                                                    if product_img != "":
                                                        eb = DiscordEmbed(title="`💵 구매로그`", description="`익명님, " + product_name + " " + str(buy_amount) + "개 구매 감사합니다! 💝`", color=color)
                                                        eb.set_footer(text="APEX SERVICE", icon_url="https://cdn.discordapp.com/avatars/972723293570347008/2bbb5b5d9fd2f148c7bf4ecd87224dfc.webp?size=80")
                                                        eb.set_timestamp()
                                                        eb.set_thumbnail(url=product_img)
                                                        webhook.add_embed(eb)
                                                    else:
                                                        eb = DiscordEmbed(title="`💵 구매로그`", description="`익명님, " + product_name + " " + str(buy_amount) + "개 구매 감사합니다! 💝`", color=color)
                                                        eb.set_footer(text="APEX SERVICE", icon_url="https://cdn.discordapp.com/avatars/972723293570347008/2bbb5b5d9fd2f148c7bf4ecd87224dfc.webp?size=80")
                                                        eb.set_timestamp()
                                                else:
                                                    if product_img != "":
                                                        eb = DiscordEmbed(title="`💵 구매로그`", description="<@" + str(interaction.author.id) + ">" + "`님, " + product_name + " " + str(buy_amount) + "개 구매 감사합니다! 💝`", color=color)
                                                        eb.set_footer(text="APEX SERVICE", icon_url="https://cdn.discordapp.com/avatars/972723293570347008/2bbb5b5d9fd2f148c7bf4ecd87224dfc.webp?size=80")
                                                        eb.set_timestamp()
                                                        eb.set_thumbnail(url=product_img)
                                                        webhook.add_embed(eb)
                                                    else:
                                                        eb = DiscordEmbed(title="`💵 구매로그`", description="<@" + str(interaction.author.id) + ">" + "`님, " + product_name + " " + str(buy_amount) + "개 구매 감사합니다! 💝`", color=color)
                                                        eb.set_footer(text="APEX SERVICE", icon_url="https://cdn.discordapp.com/avatars/972723293570347008/2bbb5b5d9fd2f148c7bf4ecd87224dfc.webp?size=80")
                                                        eb.set_timestamp()
                                                        webhook.add_embed(eb)
                                                webhook.execute()
                                            except Exception as e:
                                                print(e)
                                            try:
                                                buyer_role = interaction.guild.get_role(get_roleid(interaction.guild.id))
                                                await interaction.user.add_roles(buyer_role)
                                            except:
                                                pass
                                            await try_msg.delete()
                                            buyingusers = []
                                            for user in buyinguser:
                                                if user != interaction.user.id:
                                                    buyingusers.append(user)
                                                    buyinguser = buyingusers
                                            buyinguser = buyingusers
                                            await interaction.user.send(embed=discord.Embed(title="구매 성공", description=f"제품 이름 : {product_name}\n구매 개수 : {buy_amount}개\n차감 금액 : {buy_money}원", color=color),
                                            components = [
                                                    ActionRow(
                                                        Button(style=ButtonType().Link,label = "구매 제품 보기",url=docs_url),
                                                    )
                                                ]
                                            )
                                            con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
                                            cur = con.cursor()
                                            cur.execute("UPDATE users SET buycount = ? WHERE id == ?;", (user_info[6] + 1, msg.author.id))
                                            con.commit()
                                            con.close()
                                            if now_bought >= server_info[16]:
                                                con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
                                                cur = con.cursor()
                                                cur.execute("UPDATE users SET rank = ? WHERE id == ?;", ("VIP", msg.author.id))
                                                con.commit()
                                                con.close()
                                                vip_role = interaction.guild.get_role(server_info[19])
                                                await interaction.user.add_roles(vip_role)
                                            if now_bought >= server_info[17]:
                                                con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
                                                cur = con.cursor()
                                                cur.execute("UPDATE users SET rank = ? WHERE id == ?;", ("VVIP", msg.author.id))
                                                con.commit()
                                                con.close()
                                                vvip_role = interaction.guild.get_role(server_info[20])
                                                await interaction.user.add_roles(vvip_role)
                                        except Exception as e:
                                            

                                            try:
                                                await try_msg.delete()
                                            except Exception as e:
                                                
                                                pass
                                    else:
                                        buyingusers = []
                                        for user in buyinguser:
                                            if user != interaction.user.id:
                                                buyingusers.append(user)
                                        buyinguser = buyingusers
                                        await interaction.user.send(embed=discord.Embed(title="제품 구매 실패", description="잔액이 부족합니다.", color=color))
                                else:
                                    buyingusers = []
                                    for user in buyinguser:
                                        if user != interaction.user.id:
                                            buyingusers.append(user)
                                    buyinguser = buyingusers
                                    await interaction.user.send(embed=discord.Embed(title="제품 구매 실패", description="재고가 부족합니다.", color=color))
                            else:
                                buyingusers = []
                                for user in buyinguser:
                                    if user != interaction.user.id:
                                        buyingusers.append(user)
                                        buyinguser = buyingusers
                                await interaction.user.send(embed=discord.Embed(title="제품 구매 실패", description="재고가 없습니다.", color=color))
                        else:
                            await interaction.respond(embed=discord.Embed(title="구매 실패", description="이미 구매가 진행중입니다.", color=color))

                if interaction.custom_id == "정보":
                    con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
                    cur = con.cursor()
                    cur.execute("SELECT * FROM users WHERE id == ?;", (interaction.author.id,))
                    user_info = cur.fetchone()
                    con.close()
                    if user_info[5] == "일반":
                        rank = server_info[10]
                    if user_info[5] == "VIP":
                        rank = server_info[11]
                    if user_info[5] == "VVIP":
                        rank = server_info[12]
                    if user_info[5] == "리셀러":
                        rank = server_info[13]
                    await interaction.respond(embed=discord.Embed(title=str(interaction.user.name) + "님의 정보", description="보유 금액 : " + str(user_info[2]) + "원\n누적 금액 : " + str(user_info[2]) + f"원\n등급 : {user_info[5]}\n할인율 : {rank}%\n구매 수 : {user_info[6]}회\n경고 수 : {user_info[4]}회", color=color))

                if interaction.custom_id == "공지":
                    con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
                    cur = con.cursor()
                    cur.execute("SELECT * FROM serverinfo WHERE id == ?;",(interaction.guild.id,))
                    server_info = cur.fetchone()
                    con.close
                    await interaction.respond(embed=discord.Embed(title="공지사항", description=server_info[23], color=color))

                if interaction.custom_id == "연장":
                    if interaction.user.guild_permissions.administrator or interaction.author.id in total_master_ids:
                        await interaction.user.send(embed=discord.Embed(description="라이센스를 입력해주세요.", color=color))
                        await interaction.respond(embed=discord.Embed(description="DM을 확인해주세요.", color=color))
                        def check(license_key):
                            return (license_key.author.id == interaction.user.id and isinstance(license_key.channel, discord.channel.DMChannel))
                        license_key = await bot.wait_for("message", timeout=30, check=check)
                        license_key = license_key.content
                        con = sqlite3.connect("../DB/license.db")
                        cur = con.cursor()
                        cur.execute("SELECT * FROM license WHERE code == ?;", (license_key,))
                        search_result = cur.fetchone()
                        con.close()
                        if (search_result != None):
                            if (search_result[2] == 0):
                                con = sqlite3.connect("../DB/license.db")
                                cur = con.cursor()
                                cur.execute("UPDATE license SET isused = ?, useddate = ?, usedby = ? WHERE code == ?;", (1, nowstr(), str(interaction.guild.id), license_key))
                                con.commit()
                                cur = con.cursor()
                                cur.execute("SELECT * FROM license WHERE code == ?;",(license_key,))
                                key_info = cur.fetchone()
                                con.close()
                                con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
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
                                await interaction.user.send(embed=discord.Embed(description=f"`{key_info[1]}`일이 연장되었습니다.", color=color))
                            else:
                                await interaction.user.send(embed=discord.Embed(description="이미 사용된 라이센스입니다.", color=color))
                        else:
                            await interaction.user.send(embed=discord.Embed(description="존재하지 않는 라이센스입니다.", color=color))

                if interaction.custom_id == "웹패널":
                    if interaction.user.guild_permissions.administrator or interaction.author.id in total_master_ids:
                        con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
                        cur = con.cursor()
                        cur.execute("SELECT * FROM serverinfo;")
                        server_info = cur.fetchone()
                        await interaction.respond(embed=discord.Embed(title="웹패널 정보", description="만료일: `" + server_info[1] + f"`\n웹 패널: {domain}\n아이디: `" +str(interaction.guild.id) + "`\n비밀번호: `" + server_info[4] + "`", color=color))

                if interaction.custom_id == "디비백업":
                    if interaction.user.guild_permissions.administrator or interaction.author.id in total_master_ids:
                        await interaction.send(file=discord.File("../DB/" + str(interaction.guild.id) + ".db"))

bot.run(setting.token)
