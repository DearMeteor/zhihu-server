# -*- coding: utf-8 -*-
import json
from .zk_sdk import ServiceRegister
#from config import ZK_HOSTS, ZK_PATH, ZK_AUTH


class ZKHelper(object):
    def __init__(self, ZK_HOSTS, ZK_PATH, ZK_AUTH):
        """
        :return:
        """
        self.ZK_HOSTS = ZK_HOSTS
        self.ZK_PATH = ZK_PATH
        self.ZK_AUTH = ZK_AUTH
        self._sd = ServiceRegister(self.ZK_HOSTS, read_only=False)

    def get(self):
        """
        :return:
        """
        data, v = self._sd.get(self.ZK_PATH)
        obj = json.loads(data)
        return obj


if __name__ == '__main__':
    import os
    ZK_HOSTS = os.getenv('ZK_HOSTS', '192.168.5.30:2181,192.168.5.30:2182,192.168.5.30:2183')
    ZK_PATH = os.getenv('ZK_PATH', '/platform/operation_wansuiye')
    ZK_AUTH = os.getenv('ZK_AUTH', 'user:password')
    obj = ZKHelper(ZK_HOSTS, ZK_PATH, ZK_AUTH)
    obj.get()