# -*- coding: utf-8 -*-

import logging
import logging.config
import yaml
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def log_init():
    try:
        from log_output_py import log_adapter
        with open(os.path.join(BASE_DIR, 'conf.yml')) as fd:
            yml = yaml.load(fd)
            conf = yml['logging']

        logging.setLoggerClass(log_adapter.EventLogger)
        logging.config.dictConfig(conf)
    except:
        pass
    return logging.getLogger('operation_vip')


logger = log_init()
