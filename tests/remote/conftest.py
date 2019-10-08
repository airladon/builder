import pytest  # noqa
from pathlib import Path
from yaml import safe_load
import os

yml_file = (Path().absolute() / 'addresses.yml').absolute().as_posix()
addresses = {}
with open(yml_file, 'r') as f:
    addresses = safe_load(f)

test_address = os.environ.get('HEROKU_TEST_ADDRESS') or \
    addresses['test']
prod_address = os.environ.get('HEROKU_PROD_ADDRESS') or \
    addresses['prod']
dev_address = os.environ.get('HEROKU_DEV_ADDRESS') or \
    addresses['dev']


def pytest_addoption(parser):
    parser.addoption("--server", action="store", default="dev")


def pytest_generate_tests(metafunc):
    # This is called for every test. Only get/set command line arguments
    # if the argument is specified in the list of test "fixturenames".
    server_value = metafunc.config.option.server
    if 'address' in metafunc.fixturenames:
        if server_value == 'prod':
            metafunc.parametrize("address", [prod_address])
        if server_value == 'test':
            metafunc.parametrize("address", [test_address])
        if server_value == 'dev':
            metafunc.parametrize("address", [dev_address])
