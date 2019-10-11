import json
import requests
import pytest  # noqa: F401


def test_root(address):
    r = json.loads(requests.get(f'{address}/').content)
    assert r['status'] == 'ok'
