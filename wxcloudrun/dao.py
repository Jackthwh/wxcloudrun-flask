import logging

from sqlalchemy.exc import OperationalError

from wxcloudrun import db
from wxcloudrun.model import Counters, Demos, AccessToken

# 初始化日志
logger = logging.getLogger('log')


def query_counterbyid(id):
    """
    根据ID查询Counter实体
    :param id: Counter的ID
    :return: Counter实体
    """
    try:
        return Counters.query.filter(Counters.id == id).first()
    except OperationalError as e:
        logger.info("query_counterbyid errorMsg= {} ".format(e))
        return None


def delete_counterbyid(id):
    """
    根据ID删除Counter实体
    :param id: Counter的ID
    """
    try:
        counter = Counters.query.get(id)
        if counter is None:
            return
        db.session.delete(counter)
        db.session.commit()
    except OperationalError as e:
        logger.info("delete_counterbyid errorMsg= {} ".format(e))


def insert_counter(counter):
    """
    插入一个Counter实体
    :param counter: Counters实体
    """
    try:
        db.session.add(counter)
        db.session.commit()
    except OperationalError as e:
        logger.info("insert_counter errorMsg= {} ".format(e))


def update_counterbyid(counter):
    """
    根据ID更新counter的值
    :param counter实体
    """
    try:
        counter = query_counterbyid(counter.id)
        if counter is None:
            return
        db.session.flush()
        db.session.commit()
    except OperationalError as e:
        logger.info("update_counterbyid errorMsg= {} ".format(e))

# Demos table

def query_demobyuser(user):
    try:
        return Demos.query.filter(Demos.user == user).first()
    except OperationalError as e:
        logger.info("query_demobyuser errorMsg= {} ".format(e))
        raise e

def delete_demobyuser(user):
    try:
        demo = Demos.query.filter(Demos.user == user).first()
        if demo is None:
            return
        db.session.delete(demo)
        db.session.commit()
    except OperationalError as e:
        logger.info("delete_demobyuser errorMsg= {} ".format(e))
        raise e

def update_demobyuser(demo):
    try:
        demo = query_demobyuser(demo.user)
        if demo is None:
            return
        db.session.flush()
        db.session.commit()
    except OperationalError as e:
        logger.error("update_demobyuser errorMsg= {} ".format(e))
        raise e

def insert_demo(demo):
    try:
        db.session.add(demo)
        db.session.commit()
    except OperationalError as e:
        logger.error("insert_demo errorMsg= {} ".format(e))
        raise e

def upsert_demo(demo):
    try:
        demo = query_demobyuser(demo.user)
        if demo is None:
            db.session.add(demo)
            db.session.commit()
        else:
            db.session.flush()
            db.session.commit()
    except OperationalError as e:
        logger.error("upsert_demo errorMsg= {} ".format(e))
        raise e

def update_thread_id_of_demo(user, thread_id):
    try:
        demo = query_demobyuser(user)
        # assert demo is not None
        demo.thread_id = thread_id
        update_demobyuser(demo)
    except OperationalError as e:
        logger.error("update_thread_id_of_demo errorMsg= {} ".format(e))
        raise e

# AccessToken table

def query_accesstoken():
    try:
        return AccessToken.query.filter().first()
    except OperationalError as e:
        logger.info("query_accesstoken errorMsg= {} ".format(e))
        raise e

def delete_accesstoken():
    try:
        token = AccessToken.query.filter().first()
        if token is None:
            return
        db.session.delete(token)
        db.session.commit()
    except OperationalError as e:
        logger.info("delete_accesstoken errorMsg= {} ".format(e))
        raise e

def update_accesstoken(token):
    try:
        token = query_accesstoken()
        if token is None:
            return
        db.session.flush()
        db.session.commit()
    except OperationalError as e:
        logger.error("update_demobyuser errorMsg= {} ".format(e))
        raise e

def insert_accesstoken(token):
    try:
        db.session.add(token)
        db.session.commit()
    except OperationalError as e:
        logger.error("insert_demo errorMsg= {} ".format(e))
        raise e
