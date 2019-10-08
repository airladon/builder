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

# class thread_with_exception(threading.Thread):
#     def __init__(self, name):
#         threading.Thread.__init__(self)
#         self.name = name

#     def get_id(self):
#         # returns id of the respective thread
#         if hasattr(self, '_thread_id'):
#             return self._thread_id
#         for id, thread in threading._active.items():
#             if thread is self:
#                 return id

#     def raise_exception(self):
#         thread_id = self.get_id()
#         res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
#             thread_id,
#             ctypes.py_object(SystemExit))
#         if res > 1:
#             ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
#             print('Exception raise failure')


# def start(callback, *popenArgs, **pOpenKWArgs):
#     def runInThread(callback, popenArgs):
#         proc = subprocess.Popen(*popenArgs, **pOpenKWArgs)
#         proc.wait()
#         callback(proc)
#         return
#     clone_job = thread_with_exception(
#         target=runInThread, args=(callback, popenArgs))
#     clone_job.start()
#     return clone_job

def build_failed():
    pass


def build_passed():
    pass


# Pipeline related methods
def pipeline(f, callback):
    proc = subprocess.run(
        ['./repo/runner.sh'], stdout=f, stderr=f, shell=True)
    callback(proc)


def pipeline_finished(process_completion):
    if log_handler is not None:
        log_handler.close()
    if process_completion.returncode != 0:
        app.logger.error('Deploy pipline failed')
        build_failed()
        return
    app.logger.info('Pipline finished successfully')
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
    proc = subprocess.run(
        ['git', 'clone', remote_repo, local_repo], stdout=f, stderr=f)
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
            # app.logger.info(f'Terminating {job}, {job.is_alive()}')
            job.terminate()
    jobs = []
    # app.logger.info('Starting')
    if os.path.isdir(local_repo):
        shutil.rmtree(local_repo)
    if os.path.isdir(local_repo):
        raise Exception('Local repository not deleted')
    clone_repo()
    # app.logger.info(f'job2: {jobs}')
    # app.logger.info('Build Started')
    return jsonify({'status': 'ok'})


@app.route('/ls')
def ls():
    # f = open('./log.txt', 'w')
    ls_output = subprocess.run(["ls", 'repo'], capture_output=True)
    app.logger.info(ls_output.stdout.decode('utf-8'))
    # f.close()
    # if not os.path.isfile('./log.txt'):
    #     return jsonify({'status': 'no log file'})

    # f = open('./log.txt', 'r')
    # print(f.readlines())

    return jsonify({'status': 'ok'})
