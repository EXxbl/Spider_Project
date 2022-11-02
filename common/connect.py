import redis
import pymysql

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
