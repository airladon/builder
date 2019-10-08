import pytest  # noqa: F401
import os
import sys
basedir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, './app/')
from app import app  # noqa


@pytest.fixture(scope="module")
def client(request):
    # app.config['SQLALCHEMY_DATABASE_URI'] = \
    #     'sqlite:///' + os.path.join(basedir, 'app_test.db')
    # Setup app config variables here

    client = app.test_client()

    yield client

    # # Run on test finish
    # def fin():
    #     print('unload stuff here')
    # request.addfinalizer(fin)
