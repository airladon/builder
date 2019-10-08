
import pytest  # noqa: F401
# import sys
# sys.path.insert(0, './app/')
# from app.models import db, Users  # noqa E402
# from app.tools import hash_str_with_pepper  # noqa E402


def test_root(client):
    res = client.get('/').get_json()
    assert res['status'] == 'ok'
