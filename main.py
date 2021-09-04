import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests as r
import sqlite3 as sql

dbfile="userlar.db"
with sql.connect(dbfile) as con:
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users(
    id INTEGER,
    name TEXT,
    link TEXT)""")
    con.commit()
def insert(userid, name, link):
    con = sql.connect(dbfile)
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (userid,))
    if cur.fetchone() is None:
        cur.execute("INSERT INTO users(id, name, link) VALUES(?,?,?)", (userid, name, link))
    con.commit()

buttons = InlineKeyboardMarkup(
    [[
        InlineKeyboardButton("📹 Video", callback_data='video')
    ],[
        InlineKeyboardButton("🔈 Audio", callback_data='audio')
    
    ]]
    )
token = "bot token"

bot = telebot.TeleBot(token, parse_mode="markdown")

@bot.message_handler(commands=['start'])
def start(msg):
    chat_id = msg.chat.id
    u_name = msg.from_user.first_name
    link = 0
    insert(chat_id, u_name, link)
    
    bot.send_message(chat_id, "Salom\nMenga youtube video linkini yuboring.")
@bot.message_handler(content_types=['text'])
def get_dl(msg):
    chat_id = msg.chat.id
    try:
        txt1="https://youtu.be/"
        txt2="http://www.youtube.com/"
        url = msg.text
        if txt1 in url or txt2 in url:
            con = sql.connect(dbfile)
            cur = con.cursor()
            cur.execute("SELECT link FROM users WHERE id = ?", (chat_id,))
            res_url = cur.fetchall()
            for u in res_url:
                urli = u[0]
            cur.execute("UPDATE users SET link = ? WHERE link = ?", (url, urli))
            con.commit()
            bot.send_message(msg.chat.id, "Formatni tanlang:", reply_markup=buttons)
        else:
            bot.send_message(msg.chat.id, "Video havolasida xatolik")
    except Exception as ex:
        bot.send_message(msg.chat.id, f"Video hajmi 50 mb dan katta!")
@bot.callback_query_handler(func = lambda call: True)
def calls(call):
    chat_id = call.message.chat.id
    msg_id = call.message.message_id
    data = call.data
    if data == 'video':
        try:
            con = sql.connect(dbfile)
            cur = con.cursor()
            cur.execute("SELECT link FROM users WHERE id = ?", (chat_id,))
            res = cur.fetchall()
            for ur in res:
                urli = ur[0]
                con.commit()
            rl = r.get(f"https://freerestapi.herokuapp.com/api/ytmp4?url={urli}").json()
            title = rl['title']
            channel = rl['channel']
            pub = rl['published']
            views = rl['views']
            cap = f"✅ Video yuklandi\n\n📹 Video nomi: *{title}*\n\n📡 Kanal: *{channel}*\n\n🕰 Yuklangan vaqti: *{pub}*\n\n👁 Koʻrishlar soni: *{views}*"
            url = rl['url']
            bot.delete_message(chat_id,msg_id)
            bot.send_video(chat_id, url, caption=cap)
        except Exception as ex:
            print(f"Video yuborish: {ex}")
    if data == 'audio':
        try:
            con = sql.connect(dbfile)
            cur = con.cursor()
            cur.execute("SELECT link FROM users WHERE id = ?", (chat_id,))
            res = cur.fetchall()
            for ur in res:
            	urli=ur[0]
            	con.commit()
            rl = r.get(f"https://freerestapi.herokuapp.com/api/ytmp3?url={urli}").json()
            title = rl['title']
            channel = rl['channel']
            pub = rl['published']
            views = rl['views']
            cap = f"✅ Audio yuklandi\n\n🎧 Audio nomi: *{title}*\n\n📡 Kanal: *{channel}*\n\n🕰 Yuklangan vaqti: *{pub}* Koʻrishlar soni: *{views}*"
            url = rl['url']
            bot.delete_message(chat_id,msg_id)
            #bot.send_message(chat_id, f"{url}")
            bot.send_audio(chat_id, url, caption=cap)
        except Exception as ex:
            print(f"Audio yuborish: {ex}")
        
        
        
bot.polling()