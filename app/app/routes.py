from flask import jsonify
# from flask import render_template, flash, redirect, url_for, jsonify, session
# from flask import make_response, request
from app import app
import subprocess
import shutil
import os
# from subprocess import PIPE, STDOUT
import multiprocessing
import time
# import datetime
# from werkzeug.urls import url_parse

remote_repo = 'https://github.com/airladon/logdrain'
project = remote_repo.split('/')[-1]
log_file = './repo/log.txt'
log_handler = None
local_repo = f'./repo/{project}'
jobs = []


def build_failed():
    pass


def build_passed():
    pass


# Pipeline related methods
def pipeline(f, callback):
    proc = subprocess.run(
        [f'{local_repo}/start_env.sh deploy_pipeline'],
        stdout=f, stderr=f, shell=True)
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
    # proc = subprocess.run(['git', 'checkout', 'file-upload'])
    # print(proc)
    start_pipline()


class proc:
    def __init__(self):
        self.returncode = 0


def clone(f, callback):
    proc = subprocess.run(
        ['git', 'clone', '--single-branch', '--branch', 'file-upload',
         remote_repo, local_repo], stdout=f, stderr=f)
    callback(proc)
    # print(f)
    # f.write('cloning started\n')
    # time.sleep(1)
    # f.write('cloning complete\n')
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
    if os.path.isdir(local_repo):
        shutil.rmtree(local_repo)
    if os.path.isdir(local_repo):
        raise Exception('Local repository not deleted')
    clone_repo()
    return jsonify({'status': 'ok'})


@app.route('/ls')
def ls():
    ls_output = subprocess.run(["ls", 'repo'], capture_output=True)
    app.logger.info(ls_output.stdout.decode('utf-8'))
    return jsonify({'status': 'ok'})
