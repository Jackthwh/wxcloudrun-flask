from wxcloudrun.atoken import AccessTokenHelper
from wxcloudrun.media import Media


def test_media_upload():
    accessToken = AccessTokenHelper().sync_db().get_access_token()
    id = Media().upload(accessToken=accessToken, filePath='tests/data/fig1.png', mediaType='image')
    print(id)
    assert False

def test_media_download():
    accessToken = AccessTokenHelper().sync_db().get_access_token()
    buffer = Media().get(accessToken=accessToken, mediaId='1AmxZuHw5lRlem4Uzq32vaNcNXqgNAFivBtAswc0nE-yh6Sn7XSL1v3kO6FGhXFZ')
    with open('a.png', 'w+b') as f:
        f.write(buffer)
