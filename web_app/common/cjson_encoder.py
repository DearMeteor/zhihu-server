# _*_ coding:utf-8 _*_
"""
Created by chenyuanyi on 2017/7/5
"""

import json

from datetime import datetime, date, timedelta


class CJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, timedelta):
            return str(obj)
        elif isinstance(obj, long):
            return int(obj)
        else:
            return json.JSONEncoder.default(self, obj)
