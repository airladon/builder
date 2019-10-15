# import subprocess
import re
from shutil import copyfile
import os
from itertools import chain
import pathlib
import json
# from app import app


def copy_diff_snapshots(copy_path):
    pathlib.Path(copy_path).mkdir(parents=True, exist_ok=True)

    files = []

    # r=root, d=directories, f = files
    for r, d, f in chain.from_iterable(
            os.walk(path) for path in [
            './repo/clone/src', './repo/clone/tests']):
        for file in f:
            if r.endswith('__diff_output__') and file.endswith('png'):
                files.append(os.path.join(r, file))

    for f in files:
        file_name = re.sub('^./', '', f)
        file_name = re.sub('repo/clone', '', file_name)
        file_name = re.sub(
            '__image_snapshots__/__diff_output__/', '', file_name)
        file_name = re.sub('/', '--', file_name)
        copyfile(f, f'{copy_path}/{file_name}')


def get_diffs(sha):
    files = []
    for r, d, f in os.walk(f'/opt/app/logs/{sha}'):
        for file in f:
            if file.endswith('png'):
                files.append(file)
    return files


def create_row(status):
    out_str = f'''<div class="{status['status']} test_item">
    <div class="title">
        PR {status["pr"]}
    </div>
    <div class="subtitle">
        {status["repository"]}
    </div>
    <table>
    <tr class="key_value">
        <td class="key">Commit:</td>
        <td class="value">{status["commit"]}</td>
    </tr>
    <tr class="key_value">
        <td class="key">Started:</td>
        <td class="value">{status["start"]}</td>
    </tr>
    <tr class="key_value">
        <td class="key">Status:</td>
        <td class="value">{status["status"]}</td>
    </tr>
    <tr class="key_value">
        <td class="key">Run Time:</td>
        <td class="value">{status["run_time"]}</td>
    </tr>
    </table>
    <div class="log">
        <a href="/log/{status['commit']}">Log</a>
    </div>'''

    diffs = get_diffs(status['commit'])
    for diff in diffs:
        out_str = f'''{out_str}
            <div class="diff">
                <a href="/diff/{status['commit']}/{diff}">{diff}</a>
            </div>'''

    out_str = f'{out_str}</div>'
    return out_str


header = '''<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="/static/styles.css">
  </head>

<body>
'''

tail = '''
</body>
</html>
'''


def status_page():
    files = []
    for r, d, f in os.walk('./logs'):
        for file in f:
            if file == 'status.txt':
                files.append(os.path.join(r, file))
    out_str = header
    for f in files:
        with open(f, 'r') as status_file:
            status = json.loads(status_file.read())
            out_str = f'{out_str}{create_row(status)}'
        # app.logger.info(status)
    out_str = f'{out_str}{tail}'
    return out_str
