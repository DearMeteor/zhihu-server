# -*- coding: utf-8 -*-
import time

__author__ = 'Administrator'

from web_app import app


class LruTool(object):
    cache = app.config.get('CACHE_LRU')
    cache_timeout = app.config.get('CACHE_TIMEOUT')

    def add_lru(self, val, name):
        value = {
            "value": val,
            'create_time': time.time() * 1000
        }
        self.cache[name] = value

    def get_value(self, name):
        lru = self.cache[name]
        if lru:
            create_time = lru.get('create_time')
            time_now = time.time() * 1000
            diff_time = int(time_now) - int(create_time)
            if diff_time > self.cache_timeout:
                del self.cache[name]
                return {'status': 1, 'message': '缓存超时!'}
            else:
                value = lru.get('value')
                return {'status': 0, 'value': value}
        else:
            return {'status': 1, 'message': '缓存不存在'}

    def clear_lru(self, name):
        del self.cache[name]

    def clear_all_lru(self):
        self.cache.clear()
