import re
import redis
import email
import imaplib
import pymysql
import traceback
from functools import wraps
from email.header import decode_header

# 创建redis连接对象
def redis_conect(host,port,password='',db=0):
    redis_config = {
        'host':host,
        'port':port,
        'password':password
    }
    conn = redis.Redis(**redis_config,db=db)
    return conn

# 创建mysql连接对象
def mysql_conect(host,password,database,charset='utf8',user='root',port=3306):
    db = pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        port=port,
        charset=charset
    )
    return db

def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value

def trydecorator(fun):
    @wraps(fun)
    def wrapper(*args, **kwargs):
        try:
            try_result = fun(*args, **kwargs)
            return try_result
        except:
            return traceback.format_exc()

    return wrapper

# 连接邮箱
@trydecorator
def qqemail_conect(title,user_email='2757221248@qq.com',password='yyxwyuaetpjvdccd'):
    # 选择服务器
    server = imaplib.IMAP4_SSL('imap.qq.com')
    try:
        server.login(user_email, password)
    except Exception as e:
        print(e)
        return None
    inbox = server.select("INBOX")
    # 搜索匹配的所有邮件，如果要搜索未读邮件则使用UNSEEN
    email_type, data = server.search(None, "ALL")
    # 邮件列表，使用空格分割得到邮件索引
    msglist = data[0].split()
    msglist.reverse()
    # 只取前50个邮件
    if len(msglist) > 50:
        msglist = msglist[:50]
    if len(msglist) != 0:
        for latest in msglist:
            email_type, datas = server.fetch(latest, '(RFC822)') # 通过邮箱编号和选择获取什么数据
            text = datas[0][1].decode('utf-8')
            message = email.message_from_string(text) # 用email库获取解析数据
            subject = decode_str(message.get("Subject"))
            # 判断是否和主题一致
            if subject == title:
                message = str(message).replace("=\n", "").replace("3D", "")
                return message
            else:
                continue
    return None

