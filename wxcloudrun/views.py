from datetime import datetime
import hashlib
from flask import render_template, request
from run import app
from wxcloudrun.dao import delete_counterbyid, query_counterbyid, insert_counter, update_counterbyid
from wxcloudrun.model import Counters
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response, make_msg_response, make_text_response
from wxcloudrun import receive, reply
import config

@app.route('/')
def index():
    """
    :return: 返回index页面
    """
    return render_template('index.html')


@app.route('/api/count', methods=['POST'])
def count():
    """
    :return:计数结果/清除结果
    """

    # 获取请求体参数
    params = request.get_json()

    # 检查action参数
    if 'action' not in params:
        return make_err_response('缺少action参数')

    # 按照不同的action的值，进行不同的操作
    action = params['action']

    # 执行自增操作
    if action == 'inc':
        counter = query_counterbyid(1)
        if counter is None:
            counter = Counters()
            counter.id = 1
            counter.count = 1
            counter.created_at = datetime.now()
            counter.updated_at = datetime.now()
            insert_counter(counter)
        else:
            counter.id = 1
            counter.count += 1
            counter.updated_at = datetime.now()
            update_counterbyid(counter)
        return make_succ_response(counter.count)

    # 执行清0操作
    elif action == 'clear':
        delete_counterbyid(1)
        return make_succ_empty_response()

    # action参数错误
    else:
        return make_err_response('action参数错误')


@app.route('/api/count', methods=['GET'])
def get_count():
    """
    :return: 计数的值
    """
    counter = Counters.query.filter(Counters.id == 1).first()
    return make_succ_response(0) if counter is None else make_succ_response(counter.count)

@app.route('/wx', methods=['POST'])
def reply_msg():
    """
    """
    try:
        webData = request.data # Note: empty when body is a form
        print(f"post data: {webData}")
        recMsg = receive.parse_xml(webData)
        if isinstance(recMsg, receive.Msg):
            toUser = recMsg.FromUserName
            fromUser = recMsg.ToUserName
            if recMsg.MsgType == 'text':
                content = "test"
                replyMsg = reply.TextMsg(toUser, fromUser, content)
                msg = replyMsg.send()
            elif recMsg.MsgType == 'image':
                mediaId = recMsg.MediaId
                replyMsg = reply.ImageMsg(toUser, fromUser, mediaId)
                msg = replyMsg.send()
            else:
                msg = reply.Msg().send()
        elif isinstance(recMsg, receive.EventMsg):
            toUser = recMsg.FromUserName
            fromUser = recMsg.ToUserName
            content = "Not implemented"
            if recMsg.Event == 'CLICK':
                if recMsg.Eventkey == 'mpGuide':
                    content = u"编写中，尚未完成".encode('utf-8')

            replyMsg = reply.TextMsg(toUser, fromUser, content)
            msg = replyMsg.send()
        else:
            print("暂且不处理")
            msg = reply.Msg().send()

        return make_msg_response(msg)
    except Exception as e:
        print(e)
        return make_text_response("system error!")

@app.route('/wx', methods=['GET'])
def get_wx():
    try:
        data = request.args()
        if len(data) == 0:
            return make_text_response('hello, this is handle view')
        signature = data.signature
        timestamp = data.timestamp
        nonce = data.nonce
        echostr = data.echostr
        token = config.wx_token

        li = [token, timestamp, nonce]
        li.sort()
        sha1 = hashlib.sha1()
        for s in li:
            sha1.update(s.encode('utf-8'))
        hashcode = sha1.hexdigest()
        print("handle/GET func: hashcode, signature: ", hashcode, signature)
        msg = ''
        if hashcode == signature:
            msg = echostr
        return make_text_response(msg)

    except Exception as e:
        print(e)
        return make_text_response("system error!")
