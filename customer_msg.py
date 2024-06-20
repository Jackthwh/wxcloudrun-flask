# -*- coding: utf-8 -*-
# filename: media.py

import logging
import requests # type: ignore
import sys

from wxcloudrun.atoken import AccessTokenHelper
from wxcloudrun.dao import query_demobyuser
from wxcloudrun.inbrace import Inbrace
from wxcloudrun.views import INBRACE_MSG # type: ignore

logger = logging.getLogger('customer_msg')

class CustomerMessage():
    def __init__(self):
        pass

    def send(self, accessToken: str, user: str, content: str) -> None:
        fields={
            "touser": user,
            "msgtype": "text",
            "text":
            {
                "content": content[:600] # wechat limit
            }
        }
        logger.warning(f"sending customer message: {fields}")

        postUrl = "https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=%s" % (
            accessToken)
        urlResp = requests.post(postUrl, json=fields)

        respJson = urlResp.json()
        if respJson['errcode'] != 0:
            logger.error(respJson)
        return

user = sys.argv[1]

accessToken = AccessTokenHelper().sync_db().get_access_token()
demo = query_demobyuser(user)
if demo and demo.demo == INBRACE_MSG and demo.thread_id:
    content = Inbrace(demo).run_thread()
    CustomerMessage().send(accessToken, user, content)
else:
    logger.error(f'wrong demo status: {demo}')