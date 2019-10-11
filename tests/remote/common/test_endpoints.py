import json
import requests
import pytest  # noqa: F401


def test_root(address):
    # address = os.environ.get('HEROKU_ADDRESS')
    # assert address is not None
    r = json.loads(requests.get(f'{address}/').content)
    assert r['status'] == 'ok'
