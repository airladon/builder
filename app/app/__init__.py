from flask import Flask
from app.config import Config
from flask_talisman import Talisman
import os
import logging

app = Flask(__name__)
app.config.from_object(Config)
SELF = "'self'"
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

if not os.environ.get('LOCAL_PRODUCTION') \
   or os.environ.get('LOCAL_PRODUCTION') != 'DISABLE_SECURITY':
    talisman = Talisman(app)

from app import routes  # noqa
