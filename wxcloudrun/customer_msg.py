# -*- coding: utf-8 -*-
# filename: media.py

import logging
import threading
from time import sleep
import requests # type: ignore

logger = logging.getLogger('customer_msg')

class CustomerMessage(threading.Thread):
    def __init__(self, accessToken, user, inbrace):
        threading.Thread.__init__(self)
        self.accessToken = accessToken
        self.user = user
        self.inbrace = inbrace

    def send(self, accessToken, user, content):
        logger.info("sending customer message: " + content)
        fields={
            "touser": user,
            "msgtype": "text",
            "text":
            {
                "content": content
            }
        }

        postUrl = "https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=%s" % (
            accessToken)
        urlResp = requests.post(postUrl, data=fields,
                  headers={'Content-Type': 'application/json'})

        respJson = urlResp.json()
        if respJson['errcode'] != 0:
            logger.error(respJson)
        return

    def run(self):
        sleep(0)
        content = self.inbrace.run_thread()
        self.send(self.accessToken, self.user, content)