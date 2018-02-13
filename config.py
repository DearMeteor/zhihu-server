# -*- coding: utf-8 -*-
import pylru
import os
import json

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore


def get_local_config():
    """
    获取本地文件配置
    """
    DirPath = os.path.abspath(os.path.dirname(__file__))
    defaultConfig = DirPath + "/conf/config-base.json"
    ConfigFile = os.getenv("CONFIG_FILE", defaultConfig)

    with open(defaultConfig, 'r') as fd:
        defaultJsonConfig = json.load(fd, encoding="utf8")
    try:
        with open(ConfigFile, 'r') as fd:
            JsonConf = json.load(fd, encoding="utf8")
        for key in JsonConf:
            defaultJsonConfig[key] = JsonConf[key]
        JsonConfig = defaultJsonConfig
    except:
        JsonConfig = defaultJsonConfig
    return JsonConfig


def get_zk_config():
    """
    获取zk远程配置
    """
    from kazoo.client import KazooClient
    ZK_HOSTS = os.getenv('ZK_HOSTS', '192.168.5.30:2181,192.168.5.30:2182,192.168.5.30:2183')
    ZK_PATH = os.getenv('ZK_PATH', '/platform/operation_wansuiye')
    # ZK_AUTH = os.getenv('ZK_AUTH', 'user:password')
    try:
        zk = KazooClient(ZK_HOSTS, read_only=True, logger=None)
        zk.start()
        data, state = zk.get(ZK_PATH)
        zk.stop()
        JsonConfig = json.loads(data)
    except:
        JsonConfig = get_local_config()
    return JsonConfig


if os.getenv("config_function", "local") == "zk":
    JsonConfig = get_zk_config()
else:
    JsonConfig = get_local_config()

print(JsonConfig)


class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'operation_yp'
    # 数据库连接
    SQLALCHEMY_DATABASE_URI = JsonConfig['SQLALCHEMY_DATABASE_URI']
    SQLALCHEMY_BINDS = JsonConfig['SQLALCHEMY_BINDS']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    CACHE_LRU = pylru.lrucache(200)
    CACHE_TIMEOUT = 7200000

    JOBS = []
    SCHEDULER_JOBSTORES = {
        'default': SQLAlchemyJobStore(url=JsonConfig['SQLALCHEMY_DATABASE_URI'])
    }
    SCHEDULER_EXECUTORS = {
        'default': {'type': 'threadpool', 'max_workers': 20}
    }
    SCHEDULER_JOB_DEFAULTS = {
        'coalesce': False,
        'max_instances': 3
    }
    SCHEDULER_API_ENABLED = True

    @staticmethod
    def init_app(app):
        pass


class ProductionConfig(Config):
    SQLALCHEMY_ECHO = False


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}

ISBASE64 = 0

URLS = JsonConfig['URLS']

SERVER_VERSION = JsonConfig['SERVER_VERSION']

GAME_ID = "105"
