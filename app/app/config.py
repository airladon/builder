import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    # Database
    SECRET_KEY = os.environ.get('SECRET_KEY') or \
        'LHKiusdfuhiDkjhsdf7834897h8y7923'
    PREFERRED_URL_SCHEME = 'https'
