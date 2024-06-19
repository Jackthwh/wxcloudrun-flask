# -*- coding: utf-8 -*-
# filename: inbrace.py

import logging
from wxcloudrun.atoken import AccessTokenHelper
from wxcloudrun.customer_msg import CustomerMessage
from wxcloudrun.dao import delete_demobyuser, update_thread_id_of_demo
from wxcloudrun.media import Media
from wxcloudrun.open_ai import OpenAIClient

logger = logging.getLogger('inbrace')

tip = "发送new开始一轮新对话，或者一张之前咨询过的图片来继续上一次的对话。"

class Inbrace():
    def __init__(self, demo):
        self.__demo = demo
        self.__open_ai = OpenAIClient()
        if demo and demo.thread_id:
            self.__current_thread = self.__open_ai.get_thread(demo.thread_id)
        else:
            self.__current_thread = None
        self.__previous_demo_thread_id = 'thread_FD77xJtVZveAbyNPzFviBoNn' # hardcode for demo

    def dup_predefined_thread(self):
        prev_thread = self.__open_ai.get_thread(self.__previous_demo_thread_id)
        self.__current_thread = self.__open_ai.dup_thread(prev_thread)
        return self.__current_thread

    def get_current_thread(self):
        return self.__current_thread

    def handle(self, recMsg):
        if recMsg.MsgType == "text" and recMsg.Content == "new":
            self.__current_thread = self.__open_ai.get_thread(None)
            update_thread_id_of_demo(recMsg.FromUserName, self.__current_thread.id)
            return self.__open_ai.get_last_msg(self.__current_thread)
        elif recMsg.MsgType == "text" and recMsg.Content == "end":
            delete_demobyuser(recMsg.FromUserName)
            self.__demo = None
            self.__current_thread = None
            return "Demo session is over."
        elif recMsg.MsgType == "image":
            if self.__current_thread:
                accessToken = AccessTokenHelper().sync_db().get_access_token()
                buffer, image_type = Media().get(accessToken=accessToken, mediaId=recMsg.MediaId)
                self.__open_ai.append_image_msg(
                    self.__current_thread, buffer, image_type
                )
                return "" # waiting for text msg
            else:
                self.dup_predefined_thread()
                update_thread_id_of_demo(recMsg.FromUserName, self.__current_thread.id)
                return self.__open_ai.get_last_msg(self.__current_thread)
        elif recMsg.MsgType == "text":
            if not self.__current_thread:
                return tip
            self.__open_ai.append_text_msg(self.__current_thread, recMsg.Content)
            accessToken = AccessTokenHelper().sync_db().get_access_token()
            CustomerMessage(accessToken, recMsg.FromUserName, self).run()
            logger.info("early return")
            return ""
        else:
            return 'not implemented'

    def run_thread(self):
        return self.__open_ai.run_thread(self.__current_thread)