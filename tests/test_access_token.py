
from wxcloudrun.atoken import AccessTokenHelper


def test_access_token():
    at = AccessTokenHelper().sync_db()
    assert at.get_access_token()