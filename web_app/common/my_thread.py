# _*_ coding:utf-8 _*_
"""
Created by Sunqi on 2017/7/19
"""

from threading import Thread

class MyThread(Thread):
    def __init__(self, fun_, *args):
        Thread.__init__(self)
        self.fun_ = fun_
        self.args = args
        self.result = None

    def run(self):
        self.result = self.fun_(*self.args)

    def get_result(self):
        return self.result

