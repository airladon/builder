import requests
import sys
import json

payload = {
    'action': 'review',
    'repository': {
        'html_url': 'https://github.com/airladon/builder',
        'owner': {
            'login': 'mock_do_not_send',
        },
        'name': 'buidler',
    },
    'pull_request': {
        'head': {
            'sha': '70e68ffaea80bcb1b3e3ccb56a191d406b40299d',
            'ref': 'temp',
        },
        'base': {
            'ref': 'master',
        },
        'number': '999',
    },
}

headers = {'X-Github-Event': 'pull_request'}

url = 'http://host.docker.internal:5020/check'
if len(sys.argv) > 1:
    url = sys.argv[1]
requests.post(url, json=payload, headers=headers)
