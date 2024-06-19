from datetime import datetime
import traceback
import hashlib
from flask import render_template, request, g
from wxcloudrun import app
from wxcloudrun.dao import delete_counterbyid, insert_demo, query_counterbyid, insert_counter, query_demobyuser, update_counterbyid, update_demobyuser
from wxcloudrun.inbrace import Inbrace
from wxcloudrun.model import Counters, Demos
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response, make_msg_response, make_text_response
from wxcloudrun import receive, reply
import config

INBRACE_MSG = "inbrace"

GREETING = """
    欢迎访问智慧泉源公众号！我们从事AI应用开发、设计和咨询。就您关心的任何问题，敬请留言。我们会尽快给你回复。
"""

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
    try:
        # TODO: verify sig
        webData = request.data # Note: empty when body is a form
        app.logger.info(f"post data: {webData}")
        recMsg = receive.parse_xml(webData)
        if isinstance(recMsg, receive.Msg):
            toUser = recMsg.FromUserName
            fromUser = recMsg.ToUserName
            if recMsg.MsgType == 'text':
                tip = "你可以发送new开始一轮新对话，或者一张之前咨询过的图片来继续上一次的对话。"
                demo = query_demobyuser(toUser)
                content = ""
                if recMsg.Content == INBRACE_MSG:
                    if not demo:
                        demo = Demos()
                        demo.user = toUser
                        demo.demo = INBRACE_MSG
                        insert_demo(demo)
                        content = "欢迎来到Inbrace演示！" + tip
                    elif demo.demo != INBRACE_MSG:
                        demo.demo = INBRACE_MSG
                        demo.thread_id = ''
                        update_demobyuser(demo)
                        content = "欢迎来到Inbrace演示！" + tip
                    else:
                        content = "Inbrace演示进行中……" + tip
                    return make_resp_msg(toUser, fromUser, content)
                else:
                    if demo and demo.demo == INBRACE_MSG:
                        content = Inbrace(demo).handle(recMsg)
                    else:
                        content = GREETING
                    return make_resp_msg(toUser, fromUser, content)

            elif recMsg.MsgType == 'image':
                demo = query_demobyuser(toUser)
                if demo and demo.demo == INBRACE_MSG:
                    content = Inbrace(demo).handle(recMsg)
                else:
                    content = GREETING
                return make_resp_msg(toUser, fromUser, content)
            else:
                return make_resp_msg(toUser, fromUser)

        elif isinstance(recMsg, receive.EventMsg):
            toUser = recMsg.FromUserName
            fromUser = recMsg.ToUserName
            content = "Not implemented"
            if recMsg.Event == 'CLICK':
                if recMsg.Eventkey == 'mpGuide':
                    content = u"编写中，尚未完成".encode('utf-8')

            return make_resp_msg(toUser, fromUser, content)
        else:
            app.logger.info("暂且不处理")
            return make_resp_msg(toUser, fromUser)

    except Exception as e:
        app.logger.error(e)
        app.logger.error(traceback.format_exc())
        return make_resp_msg(toUser, fromUser, "system error!")

@app.route('/wx', methods=['GET'])
def get_wx():
    try:
        data = request.args
        if len(data) == 0:
            return make_text_response('hello, this is handle view')
        signature = data['signature']
        timestamp = data['timestamp']
        nonce = data['nonce']
        echostr = data['echostr']
        token = config.wx_token

        li = [token, timestamp, nonce]
        li.sort()
        sha1 = hashlib.sha1()
        for s in li:
            sha1.update(s.encode('utf-8'))
        hashcode = sha1.hexdigest()
        app.logger.info("handle/GET func: hashcode, signature: ", hashcode, signature)
        msg = ''
        if hashcode == signature:
            msg = echostr
        return make_text_response(msg)

    except Exception as e:
        app.logger.error(e)
        return make_text_response("system error!")

def make_resp_msg(toUser, fromUser, content="success"):
    replyMsg = reply.TextMsg(toUser, fromUser, content)
    msg = replyMsg.send()
    return make_text_response(msg)