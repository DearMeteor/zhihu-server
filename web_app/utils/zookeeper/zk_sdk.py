# -*- coding: utf-8 -*-
"""
Created on 2017-01-16

@author: Cheng Shangguan
"""

from kazoo.client import KazooClient, KazooState
from kazoo.exceptions import ZookeeperError, NoNodeError, BadVersionError, NodeExistsError


class DLock(object):
    def __init__(self, zk, path, identifier, timeout=None):
        """
        分布式锁
        :param zk: Zookeeper客户端
        :param path: 路由
        :param identifier: 锁标识
        """
        self._zk = zk
        self._timeout = timeout
        self._lock = self._zk.Lock(path, identifier)
        self.state = KazooState.CONNECTED

    def __enter__(self):
        self._zk.add_listener(self.listener)
        self.lock()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unlock()
        self._zk.remove_listener(self.listener)

    def listener(self, state):
        self.state = state
        if self.state == KazooState.LOST:
            self._zk.restart()
            self._lock.acquire()
        elif self.state == KazooState.SUSPENDED:
            self._zk.restart()
            self._lock.acquire()

    def lock(self):
        self._lock.acquire(timeout=self._timeout)

    def unlock(self):
        if self.state == KazooState.LOST:
            return
        if self.state == KazooState.SUSPENDED:
            self._zk.restart()
        self._lock.release()


class ServiceRegister(object):
    def __init__(self, hosts="127.0.0.1:2181", read_only=True, logger=None):
        """
        服务注册
        :param hosts: Zookeeper集群地址列表
        :param read_only: 是否只读
        :param logger: 日志对象
        """
        if not logger:
            import logging
            logging.basicConfig()
        self._zk = KazooClient(hosts, read_only=read_only, logger=logger)
        self._zk.start()

    def restart(self):
        self._zk.restart()

    def retry_get(self, path, watcher=None):
        """
        重读
        :param path: 节点路由
        :param watcher: 观察者回调函数
        :return: 成功：节点值，版本号；失败：异常信息，异常代码。
        """
        return self._zk.retry(self.get, path, watcher)

    def lock(self, path, identifier, timeout=None):
        """
        分布式锁
        :param path: 路由
        :param identifier: 锁标识
        :param timeout: 超时时间
        :return: 锁对象
        """
        return DLock(self._zk, path, identifier, timeout)

    def exist(self, path):
        """
        节点是否存在
        :param path: 路由
        :return: 存在返回True，不存在返回False。
        """
        state = self._zk.exists(path)
        return state is not None

    def create(self, path, value=""):
        """
        创建节点
        :param path: 节点路由
        :param value: 节点值
        :return: 节点路由
        """
        try:
            res_path = self._zk.create(path, value, makepath=True)
        except NodeExistsError:
            return path
        except NoNodeError as e:
            return e.message
        except ZookeeperError as e:
            return e.message
        else:
            return res_path

    def get(self, path, watcher=None):
        """
        查节点值
        :param path: 节点路由
        :param watcher: 观察者回调函数
        :return: 成功：节点值，版本号；失败：异常信息，异常代码。
        """
        try:
            data, state = self._zk.get(path)
            self._zk.DataWatch(path, watcher)
        except NoNodeError as e:
            return e.message, -2
        except ZookeeperError as e:
            return e.message, -3
        else:
            return data, state.version

    def get_children(self, path, watcher=None):
        """
        查子节点列表
        :param path: 节点路由
        :param watcher: 观察者回调函数
        :return: 子节点列表
        """
        try:
            data = self._zk.get_children(path)
            self._zk.DataWatch(path, watcher)
        except NoNodeError as e:
            return [], -2
        except ZookeeperError as e:
            return [], -3
        else:
            return data, 0

    def set(self, path, value, version=-1):
        """
        改节点值
        :param path: 节点路由
        :param value: 节点值
        :param version: 成功：版本号；失败：异常信息。
        """
        try:
            state = self._zk.set(path, value, version)
        except BadVersionError as e:
            return e.message
        except NoNodeError as e:
            return e.message
        except ZookeeperError as e:
            return e.message
        else:
            return state.version
