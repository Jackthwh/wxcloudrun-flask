from datetime import datetime
import time
from wxcloudrun.dao import delete_accesstoken, delete_demobyuser, insert_accesstoken, insert_demo, query_accesstoken, query_demobyuser, update_accesstoken, update_demobyuser
from wxcloudrun.model import Demos, AccessToken

username = 'Jack'

# Demos

def test_insert_demo():
    demo = Demos()
    demo.id = 1
    demo.user = username
    demo.demo = 'Inbrace'
    demo.created_at = datetime.now()
    demo.updated_at = datetime.now()
    insert_demo(demo)
    assert query_demobyuser(username) is not None

def test_update_demo():
    demo = query_demobyuser(username)
    demo.demo = 'Again'
    demo.updated_at = datetime.now()
    update_demobyuser(demo)
    updated = query_demobyuser(username)
    assert updated.demo == 'Again'

def test_delete_demo():
    delete_demobyuser(username)
    assert query_demobyuser(username) is None

# Access Token

def test_insert_token():
    token = AccessToken()
    token.token = 'a_token'
    token.expire_at = int(time.time())
    token.created_at = datetime.now()
    token.updated_at = datetime.now()
    insert_accesstoken(token)
    assert query_accesstoken() is not None

def test_update_token():
    token = query_accesstoken()
    token.token = 'Again'
    token.updated_at = datetime.now()
    update_accesstoken(token)
    updated = query_accesstoken()
    assert updated.token == 'Again'

def test_delete_token():
    delete_accesstoken()
    assert query_accesstoken() is None