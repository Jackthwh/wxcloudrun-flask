# -*- coding: utf-8 -*-
# filename: media.py

import requests # type: ignore
from requests_toolbelt.multipart.encoder import MultipartEncoder # type: ignore
from pprint import pprint

class Media(object):
    def __init__(self):
        pass

    # 上传图片
    def upload(self, accessToken, filePath, mediaType):
        multipart_data = MultipartEncoder(
        fields={
                'media': ('WechatIMG280.jpeg', open(filePath, 'rb'))
            }
        )

        postUrl = "https://api.weixin.qq.com/cgi-bin/media/upload?access_token=%s&type=%s" % (
            accessToken, mediaType)
        urlResp = requests.post(postUrl, data=multipart_data,
                  headers={'Content-Type': multipart_data.content_type})

        respJson = urlResp.json()
        pprint(respJson)
        return respJson['media_id']

    def get(self, accessToken, mediaId):
        getUrl = "https://api.weixin.qq.com/cgi-bin/media/get?access_token=%s&media_id=%s" % (
            accessToken, mediaId)
        urlResp = requests.get(getUrl)
        headers = urlResp.headers
        if ('Content-Type' in headers and (headers['Content-Type'] == 'application/json' or headers['Content-Type'] == 'text/plain')):
            pprint(urlResp.json())
        else:
            buffer = urlResp.content  # 素材的二进制
            return buffer
