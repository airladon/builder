from flask import jsonify, request
# from flask import render_template, flash, redirect, url_for, jsonify, session
from flask import make_response, send_file
from app import app
import subprocess
import shutil
import os
import requests
import json
# from subprocess import PIPE, STDOUT
import multiprocessing
import time
# import datetime
# from werkzeug.urls import url_parse

remote_repo = 'https://github.com/airladon/thisiget'
project = remote_repo.split('/')[-1]
log_file = './repo/log.txt'
log_handler = None
local_repo = f'./repo/clone'
jobs = []
github_token = os.environ.get('GITHUB_TOKEN') or ''
github_username = os.environ.get('GITHUB_USERNAME') or ''
host_url = os.environ.get('HOST_URL') or ''


def send_status(status, repository, owner, sha):
    end_point = \
        f'https://api.github.com/repos/{owner}/{repository}/statuses/{sha}'
    response = requests.post(
        url=end_point,
        auth=(github_username, github_token),
        json={
            'state': status,
            'target_url': f'{host_url}/sha/log.txt',
            'description': 'This is a description',
            'context': 'Test, Build and Deploy Server',
        })
    app.logger.info(response)


class Commit:
    def __init__(self, data):
        self.url = data['repository']['html_url']
        self.owner = data['repository']['owner']['login']
        self.name = data['repository']['name']
        self.local_repo = f'./repo/{self.name}'
        self.sha = data['pull_request']['head']['sha']
        self.from_branch = data['pull_request']['head']['ref']
        self.to_branch = data['pull_request']['base']['ref']
        self.pr_number = data['pull_request']['number']
        if (os.path.isdir(f'./repo/{self.sha}')):
            shutil.rmtree(f'./repo/{self.sha}')
        self.log_file_name = f'./logs/{self.sha}/log.txt'
        self.log_file_handler = None

    def send_success(self):
        send_status('success', self.name, self.owner, self.sha)

    def send_pending(self):
        send_status('pending', self.name, self.owner, self.sha)

    def send_fail(self):
        send_status('failure', self.name, self.owner, self.sha)

    def send_error(self):
        send_status('error', self.name, self.owner, self.sha)

    # def clone(f, callback):
    #     if os.path.isdir(local_repo):
    #         shutil.rmtree(local_repo)
    #     if os.path.isdir(local_repo):
    #         raise Exception('Local repository not deleted')
    #     proc = subprocess.run(
    #         ['git', 'clone', '--single-branch', '--branch', 'build-integration',
    #          remote_repo, local_repo], stdout=f, stderr=f)
    #     callback(proc)

    def start(self):
        app.logger.info(
            f'Starting job for PR: {self.pr_number}, commit: {self.sha}')
        self.send_pending()
        self.log_file_handler = open(self.log_file_name, 'w')
        self.log_file_handler.write(f'Start of log file for {self.sha}')
        time.sleep(20)
        self.send_fail()
        # job = multiprocessing.Process(
        #     target=clone, args=())
        # clone_job.start()
        # global jobs
        # jobs.append(clone_job)
        # app.logger.info(f'job: {clone_job}')


def build_failed():
    pass


def build_passed():
    pass


# Pipeline related methods
def pipeline(f, callback):
    proc = subprocess.run(
        [f'./start_env.sh deploy_pipeline'],
        stdout=f, stderr=f, shell=True, cwd=local_repo)
    callback(proc)


def pipeline_finished(process_completion):
    if log_handler is not None:
        log_handler.close()
    if process_completion.returncode != 0:
        app.logger.error('Deploy pipline failed')
        build_failed()
        return
    app.logger.info('Pipeline finished successfully')
    build_passed()


def start_pipline():
    log_handler = open(log_file, 'a')
    clone_job = multiprocessing.Process(
        target=pipeline, args=(log_handler, pipeline_finished))
    clone_job.start()
    global jobs
    jobs.append(clone_job)
    app.logger.info('starting pipline')


# Clone repo related methods
def repository_cloned(process_completion):
    if log_handler is not None:
        log_handler.close()
    if process_completion.returncode != 0:
        app.logger.error('Clone failed')
        return
    app.logger.info('Cloning complete')
    start_pipline()


class proc:
    def __init__(self):
        self.returncode = 0


def clone(f, callback):
    if os.path.isdir(local_repo):
        shutil.rmtree(local_repo)
    if os.path.isdir(local_repo):
        raise Exception('Local repository not deleted')
    proc = subprocess.run(
        ['git', 'clone', '--single-branch', '--branch', 'build-integration',
         remote_repo, local_repo], stdout=f, stderr=f)
    callback(proc)

    # time.sleep(2)
    # p = proc()
    # callback(p)


def clone_repo():
    log_handler = open(log_file, 'w')
    clone_job = multiprocessing.Process(
        target=clone, args=(log_handler, repository_cloned))
    clone_job.start()
    global jobs
    jobs.append(clone_job)
    app.logger.info(f'job: {clone_job}')


@app.route('/')
def home():
    app.logger.info('hello')
    return jsonify({'status': 'ok'})


@app.route('/build')
def start_build():
    # Clean existing repository
    # Git clone
    # ./start_env.sh deploy_pipeline.sh
    # Check for error
    # If running, cancel and restart
    global jobs
    if jobs is not None:
        for job in jobs:
            job.terminate()
    jobs = []
    clone_repo()
    return jsonify({'status': 'ok'})


@app.route('/ls')
def ls():
    # ls_output = subprocess.run(["ls"], capture_output=True)
    # return jsonify({'status': ls_output.stdout.decode('utf-8')})
    # app.logger.info(ls_output.stdout.decode('utf-8'))
    result = subprocess.run(['whereis', 'docker'], capture_output=True)
    app.logger.info(f'{result.stdout}, {result.stderr}')
    f = open(log_file, 'r')
    lines = f.readlines()
    for line in lines:
        app.logger.info(line.strip())
    return jsonify({'status': lines})


def build_test_deploy(
    url, repo_owner, repo_name, sha,
    from_branch='', to_branch='',
):
    send_status('pending', repo_name, repo_owner, sha)
    clone_repo(url, sha)


@app.route('/log/<sha>')
def show_log(sha):
    if os.path.isdir(f'./repo/{sha}'):
        return make_response(send_file(
            f'./repo/{sha}/log.txt', add_etags=False, cache_timeout=0))
    return jsonify({'status': f'{sha} does not exist'})


@app.route('/check', methods=['POST'])
def check():
    event = request.headers.get('X-Github-Event')
    if event == 'pull_request':
        data = request.get_json()
        to_branch = data['pull_request']['base']['ref']
        if to_branch != 'master':
            return
        commit = Commit(data)
        commit.start()
        # commit.send_pending()
        # time.sleep(20)
        # commit.send_fail()
    #     # from_branch = data['pull_request']['head']['ref']
    #     # repository = data['repository']['html_url']
    #     # repository_name = data['repository']['name']
    #     # repository_owner = data['repository']['owner']['login']
    #     # sha = data['pull_request']['head']['sha']
    #     # # app.logger.info(f'Pull Request on {repository_name} from repository {repository} from {from_branch} branch with sha {sha} to {to_branch} branch')
    #     # send_status('pending', repository_name, repository_owner, sha)
    #     # time.sleep(20)
    #     # send_status('success', repository_name, repository_owner, sha)

    # else:
    #     app.logger.info('Form:')
    #     app.logger.info(request.form)
    #     app.logger.info('Args:')
    #     app.logger.info(request.args)
    #     app.logger.info('Values:')
    #     app.logger.info(request.values)
    #     app.logger.info('JSON:')
    #     a = json.dumps(
    #         request.json, sort_keys=True, indent=4, separators=(',', ': '))
    #     app.logger.info(a)
    #     app.logger.info('Headers:')
    #     app.logger.info(request.headers)
    return jsonify({'status': 'ok'})
