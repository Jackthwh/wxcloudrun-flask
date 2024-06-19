# -*- coding: utf-8 -*-
# filename: inbrace.py

import logging
import subprocess
from typing import Union, cast
from openai.types.beta.thread import Thread
from wxcloudrun.atoken import AccessTokenHelper
from wxcloudrun.dao import delete_demobyuser, update_thread_id_of_demo
from wxcloudrun.media import Media
from wxcloudrun.model import Demos
from wxcloudrun.open_ai import OpenAIClient
from wxcloudrun.receive import ImageMsg, Msg, TextMsg

logger = logging.getLogger('inbrace')

tip = "发送new开始一轮新对话，或者一张之前咨询过的图片来继续上一次的对话。"

class Inbrace():
    def __init__(self, demo: Union[Demos, None]):
        self.__demo = demo
        self.__open_ai = OpenAIClient()

        self.__current_thread: Union[Thread, None] = None
        if demo and demo.thread_id:
            self.__current_thread = self.__open_ai.get_thread(demo.thread_id)

        self.__previous_demo_thread_id: str = 'thread_FD77xJtVZveAbyNPzFviBoNn' # hardcode for demo

    def dup_predefined_thread(self) -> Thread:
        prev_thread = self.__open_ai.get_thread(self.__previous_demo_thread_id)
        thread = self.__open_ai.dup_thread(prev_thread)
        self.__current_thread = thread
        return thread

    def get_current_thread(self) -> Union[Thread, None]:
        return self.__current_thread

    def handle(self, recMsg: Msg) -> str:
        textMsg = cast(TextMsg, recMsg)
        imageMsg = cast(ImageMsg, recMsg)
        if recMsg.MsgType == "text" and textMsg.Content == "new":
            self.__current_thread = self.__open_ai.get_thread(None)
            assert self.__current_thread
            update_thread_id_of_demo(recMsg.FromUserName, self.__current_thread.id)
            return self.__open_ai.get_last_msg(self.__current_thread)

        elif recMsg.MsgType == "text" and textMsg.Content == "end":
            delete_demobyuser(recMsg.FromUserName)
            self.__demo = None
            self.__current_thread = None
            return "Demo session is over."

        elif recMsg.MsgType == "image":
            if self.__current_thread:
                accessToken = AccessTokenHelper().sync_db().get_access_token()
                buffer, image_type = Media().get(accessToken=accessToken, mediaId=imageMsg.MediaId)
                self.__open_ai.append_image_msg(
                    self.__current_thread, buffer, image_type
                )
                return "" # waiting for text msg to run openai thread
            else:
                self.dup_predefined_thread()
                assert self.__current_thread
                update_thread_id_of_demo(recMsg.FromUserName, self.__current_thread.id)
                return self.__open_ai.get_last_msg(self.__current_thread)

        elif recMsg.MsgType == "text":
            if not self.__current_thread:
                return tip
            self.__open_ai.append_text_msg(self.__current_thread, textMsg.Content)
            # async run openai thread and submit customer msg back
            subprocess.Popen(f'cd $HOME/wxcloudrun-flask && source .venv/bin/activate && python customer_msg.py {textMsg.FromUserName}', shell=True)
            logger.warn("early return!")
            return ""

        else:
            return 'not implemented'

    def run_thread(self) -> str:
        return self.__open_ai.run_thread(self.__current_thread)
