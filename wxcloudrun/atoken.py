# -*- coding: utf-8 -*-
# filename: atoken.py

import logging
import urllib
import time
import json
import config
from wxcloudrun.model import AccessToken
from wxcloudrun.dao import query_accesstoken, insert_accesstoken, update_accesstoken

logger = logging.getLogger('AccessTokenHelper')

class AccessTokenHelper():
    def __init__(self):
        self.__accessToken = None
        self.__leftTime = 0

    def __real_get_access_token(self):
        appId = config.appId
        appSecret = config.appSecret

        postUrl = ("https://api.weixin.qq.com/cgi-bin/token?grant_type="
                   "client_credential&appid=%s&secret=%s" % (appId, appSecret))
        urlResp = urllib.request.urlopen(postUrl)
        urlResp = json.loads(urlResp.read())
        if 'errcode' in urlResp and urlResp['errcode'] != 0:
            logger.error(urlResp)
            raise ValueError(urlResp)

        self.__accessToken = urlResp['access_token']
        self.__leftTime = urlResp['expires_in']
        token = query_accesstoken()
        if not token:
            token = AccessToken()
            token.token = self.__accessToken
            token.expire_at = int(time.time()) + self.__leftTime
            insert_accesstoken(token)
        else:
            token.token = self.__accessToken
            token.expire_at = int(time.time()) + self.__leftTime
            update_accesstoken(token)


    def get_access_token(self):
        if self.__leftTime < 600:
            self.__real_get_access_token()
        return self.__accessToken

    def sync_db(self):
        token = query_accesstoken()
        if token:
            self.__accessToken = token.token
            self.__leftTime = token.expire_at - int(time.time())
        else:
            self.__real_get_access_token()
        return self
