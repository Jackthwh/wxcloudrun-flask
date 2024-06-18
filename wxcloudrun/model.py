from datetime import datetime

from wxcloudrun import db

# 计数表
class Counters(db.Model): # type: ignore
    # 设置结构体表格名称
    __tablename__ = 'Counters'

    # 设定结构体对应表格的字段
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, default=1)
    created_at = db.Column('createdAt', db.TIMESTAMP, nullable=False, default=datetime.now())
    updated_at = db.Column('updatedAt', db.TIMESTAMP, nullable=False, default=datetime.now())


class Demos(db.Model): # type: ignore
    # 设置结构体表格名称
    __tablename__ = 'Demos'

    # 设定结构体对应表格的字段
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String)
    demo = db.Column(db.String)
    thread_id = db.Column(db.String)
    created_at = db.Column('createdAt', db.TIMESTAMP, nullable=False, default=datetime.now())
    updated_at = db.Column('updatedAt', db.TIMESTAMP, nullable=False, default=datetime.now())

class AccessToken(db.Model): # type: ignore
    # 设置结构体表格名称
    __tablename__ = 'AccessToken'

    # 设定结构体对应表格的字段
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String)
    expire_at =db.Column(db.Integer)
    created_at = db.Column('createdAt', db.TIMESTAMP, nullable=False, default=datetime.now())
    updated_at = db.Column('updatedAt', db.TIMESTAMP, nullable=False, default=datetime.now())