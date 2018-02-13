# -*- coding: utf-8 -*-
"""
Created by Linjianhui on 2017/1/3
"""
import logging
import sys
import os

from flask import Flask, request
from flask_apscheduler import APScheduler
from werkzeug.utils import import_string
from flask_httpauth import HTTPTokenAuth
from flask_restful import Api
# from flask_apscheduler import APScheduler
from flask import send_from_directory

from config import config, JsonConfig
from .models.model import db

try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except NameError:
    pass

bps = [
]


def create_app(config_name):
    app_ = Flask(__name__)
    app_.config.from_object(config[config_name])
    db.init_app(app_)
    for path in bps:
        bp = import_string(path['import_path'])
        app_.register_blueprint(bp, url_prefix=path['url_prefix'])
    return app_


app = create_app(JsonConfig['ENV'])
api = Api(app)
auth = HTTPTokenAuth()
scheduler = APScheduler()
scheduler.init_app(app)
if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
    scheduler.start()


@app.errorhandler(404)
def error_handler(err):
    if request.path.startswith('/static'):
        return '{"status": 404}', 404
    return send_from_directory(app.root_path, 'admin.html')


from . import api_router
