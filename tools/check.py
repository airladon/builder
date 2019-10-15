import requests
import sys

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
            'sha': '8c02e9ce139914e8255f91bd19bacd469cce67ad',
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
