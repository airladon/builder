# import subprocess
import re
from shutil import copyfile
import os
from itertools import chain
import pathlib
import json


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
        file_name = re.sub('/', '--', file_name)
        copyfile(f, f'{copy_path}/{file_name}')


def status_page():
    files = []
    for r, d, f in os.walk('./logs'):
        for file in f:
            if file == 'status.txt':
                files.append(os.path.join(r, file))
    for f in file:
        with open(f, 'r') as status_file:
            status = json.loads(status_file.read())
        print(status)
    return 'asdf'
