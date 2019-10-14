from flask import jsonify, request
# from flask import render_template, flash, redirect, url_for, jsonify, session
from flask import make_response, send_file
from app import app
import subprocess
import shutil
import os
import requests
from datetime import datetime
from app.copy_diff_snapshots import copy_diff_snapshots, status_page
import json
# from subprocess import PIPE, STDOUT
import multiprocessing
# import time
# import datetime
# from werkzeug.urls import url_parse

# remote_repo = 'https://github.com/airladon/thisiget'
# project = remote_repo.split('/')[-1]
# log_file = './repo/log.txt'
# log_handler = None
# local_repo = f'./repo/clone'
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
            'target_url': f'{host_url}/log/{sha}',
            'description': 'This is a description',
            'context': 'Test, Build and Deploy Server',
        })
    app.logger.info(response)


class Commit:
    def initialize(self, data):
        self.url = data['repository']['html_url']
        self.owner = data['repository']['owner']['login']
        self.name = data['repository']['name']
        self.local_repo = f'./repo/clone'
        self.sha = data['pull_request']['head']['sha']
        self.from_branch = data['pull_request']['head']['ref']
        self.to_branch = data['pull_request']['base']['ref']
        self.pr_number = data['pull_request']['number']
        if (os.path.isdir(f'./logs/{self.sha}')):
            shutil.rmtree(f'./logs/{self.sha}')
        os.mkdir(f'./logs/{self.sha}')
        self.log_file_name = f'./logs/{self.sha}/log.txt'
        self.log_file_handler = None
        self.start = datetime.now()

    def send_success(self):
        self.update_status('success')
        app.logger.info('Posting Success')
        send_status('success', self.name, self.owner, self.sha)

    def update_progress(self):
        if self.status == 'pending':
            self.update_status('pending')

    def send_pending(self):
        self.update_status('pending')
        app.logger.info('Posting Pending')
        send_status('pending', self.name, self.owner, self.sha)

    def send_fail(self):
        self.update_status('failure')
        app.logger.info('Posting Failure')
        send_status('failure', self.name, self.owner, self.sha)

    def send_error(self):
        app.logger.info('Posting Error')
        self.update_status('error')
        send_status('error', self.name, self.owner, self.sha)

    def close_file(self):
        if self.log_file_handler is not None:
            self.log_file_handler.close()
        self.log_file_handler = None

    def clone(self):
        self.log_file_handler = open(self.log_file_name, 'w')
        self.log_file_handler.write(
            f'{self.url} PR: {self.pr_number}, sha: {self.sha}\n')

        if os.path.isdir(self.local_repo):
            shutil.rmtree(self.local_repo)
        if os.path.isdir(self.local_repo):
            self.close_file()
            raise Exception('Local repository not deleted')

        app.logger.info(f'Clone {self.url} on branch {self.from_branch}')
        result = subprocess.run(
            [
                'git', 'clone', '--single-branch',
                '--branch', self.from_branch,
                self.url, self.local_repo
            ], stdout=self.log_file_handler, stderr=self.log_file_handler)
        if result.returncode != 0:
            app.logger.error('Git clone failed')
            self.log_file_handler.close()
            self.send_fail()
            self.close_file()
            return

        app.logger.info(f'Checkout sha {self.sha}')
        result = subprocess.run(
            ['git', 'checkout', self.sha],
            stdout=self.log_file_handler, stderr=self.log_file_handler,
            cwd=self.local_repo)
        if result.returncode != 0:
            app.logger.error('Git checkout sha failed')
            self.send_fail()
            self.close_file()
            return

        app.logger.info('Run deploy pipeline script')
        result = subprocess.run(
            ['./start_env.sh deploy_pipeline'],
            stdout=self.log_file_handler, stderr=self.log_file_handler,
            shell=True, cwd=self.local_repo)
        app.logger.info(f'Return code: {result.returncode}')
        if result.returncode != 0:
            app.logger.error('Deploy Pipeline Failed')
            copy_diff_snapshots(f'./logs/{self.sha}/diff')
            self.send_fail()
            return
        app.logger.info(f'Should be sending success soon')
        self.log_file_handler.close()
        shutil.rmtree(self.local_repo)
        self.send_success()

    def stopJobs(self):
        if self.status == 'pending':
            self.update_status('cancelled')
        global jobs
        if jobs is not None:
            for job in jobs:
                app.logger.info(f'Terminating job {job}')
                job.terminate()
        jobs = []

    def start(self):
        self.stopJobs()
        app.logger.info(
            f'Starting job for PR: {self.pr_number}, commit: {self.sha}')
        self.send_pending()
        self.close_file()
        # time.sleep(20)
        # self.send_fail()
        job = multiprocessing.Process(target=self.clone)
        # target=self.clone, args=(self))
        job.start()
        global jobs
        jobs.append(job)
        app.logger.info(f'job: {job}')

    # Repository:
    # PR:
    # Commit:
    # Start:
    # Status:
    # Run Time:
    def status_file(self, status):
        self.status = status
        file = open(f'./logs/{self.sha}/status.txt', 'w')
        if file is None:
            return
        status = {
            'repository': self.url,
            'pr': self.pr_number,
            'commit': self.sha,
            'start': self.start,
            'status': self.status,
            'run_time': datetime.now() - self.start_time
        }
        file.write(json.dumps(status, indent=4, sort_keys=True))
        # file.write(f'PR: {self.pr_number}, commit: {self.sha}')
        # file.write(f'Time Running: {datetime.now() - self.start_time}')
        # if status == 'pending':
        #     file.write(
        #         f'Status: Running for {datetime.now() - self.start_time}')
        # elif status == 'success':
        #     file.write(
        #         f'Success. Run Time: {datetime.now() - self.start_time}')
        # elif status == 'failure':
        #     file.write(f'Fail. Run Time: {datetime.now() - self.start_time}')
        # elif status == 'error':
        #     file.write(f'Error. Run Time: {datetime.now() - self.start_time}')


commit = Commit()

# def build_failed():
#     pass


# def build_passed():
#     pass


# # Pipeline related methods
# def pipeline(f, callback):
#     proc = subprocess.run(
#         [f'./start_env.sh deploy_pipeline'],
#         stdout=f, stderr=f, shell=True, cwd=local_repo)
#     callback(proc)


# def pipeline_finished(process_completion):
#     if log_handler is not None:
#         log_handler.close()
#     if process_completion.returncode != 0:
#         app.logger.error('Deploy pipline failed')
#         build_failed()
#         return
#     app.logger.info('Pipeline finished successfully')
#     build_passed()


# def start_pipline():
#     log_handler = open(log_file, 'a')
#     clone_job = multiprocessing.Process(
#         target=pipeline, args=(log_handler, pipeline_finished))
#     clone_job.start()
#     global jobs
#     jobs.append(clone_job)
#     app.logger.info('starting pipline')


# # Clone repo related methods
# def repository_cloned(process_completion):
#     if log_handler is not None:
#         log_handler.close()
#     if process_completion.returncode != 0:
#         app.logger.error('Clone failed')
#         return
#     app.logger.info('Cloning complete')
#     start_pipline()


# class proc:
#     def __init__(self):
#         self.returncode = 0

# def clone_repo():
#     log_handler = open(log_file, 'w')
#     clone_job = multiprocessing.Process(
#         target=clone, args=(log_handler, repository_cloned))
#     clone_job.start()
#     global jobs
#     jobs.append(clone_job)
#     app.logger.info(f'job: {clone_job}')


@app.route('/')
def home():
    app.logger.info('hello')
    return jsonify({'status': 'ok'})


# @app.route('/build')
# def start_build():
#     # Clean existing repository
#     # Git clone
#     # ./start_env.sh deploy_pipeline.sh
#     # Check for error
#     # If running, cancel and restart
#     global jobs
#     if jobs is not None:
#         for job in jobs:
#             job.terminate()
#     jobs = []
#     clone_repo()
#     return jsonify({'status': 'ok'})


# @app.route('/ls')
# def ls():
#     # ls_output = subprocess.run(["ls"], capture_output=True)
#     # return jsonify({'status': ls_output.stdout.decode('utf-8')})
#     # app.logger.info(ls_output.stdout.decode('utf-8'))
#     result = subprocess.run(['whereis', 'docker'], capture_output=True)
#     app.logger.info(f'{result.stdout}, {result.stderr}')
#     f = open(log_file, 'r')
#     lines = f.readlines()
#     for line in lines:
#         app.logger.info(line.strip())
#     return jsonify({'status': lines})


# def build_test_deploy(
#     url, repo_owner, repo_name, sha,
#     from_branch='', to_branch='',
# ):
#     send_status('pending', repo_name, repo_owner, sha)
#     clone_repo(url, sha)

@app.route('/restart')
def restart():
    commit.start()


@app.route('/status')
def status():
    return status_page()
    # Get all status files
    # Sort by time
    # Show


@app.route('/log/<sha>')
def show_log(sha):
    if os.path.isdir(f'./logs/{sha}'):
        return make_response(send_file(
            f'/opt/app/logs/{sha}/log.txt', add_etags=False, cache_timeout=0))
    return jsonify({'status': f'{sha} does not exist'})


@app.route('/check', methods=['POST'])
def check():
    event = request.headers.get('X-Github-Event')
    if event == 'pull_request':
        data = request.get_json()
        to_branch = data['pull_request']['base']['ref']
        action = data['action']
        if (to_branch != 'master' and to_branch != 'build-integration') \
                or action == 'closed':
            return jsonify({'status': 'no action'})
        commit.initialize(data)
        commit.start()
    return jsonify({'status': 'ok'})
