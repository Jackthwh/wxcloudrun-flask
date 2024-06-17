import os

# 是否开启debug模式
DEBUG = True

# 读取数据库环境变量
username = os.environ.get("MYSQL_USERNAME", 'root')
password = os.environ.get("MYSQL_PASSWORD", 'root')
db_address = os.environ.get("MYSQL_ADDRESS", '127.0.0.1:3306')

# WX
wx_token = os.environ.get("WX_TOKEN", 'thisisatoken')
appId = os.environ.get("WX_APPID", 'myAppId')
appSecret = os.environ.get("WX_APPSECRET", 'myAppSecret')