# -*- coding: utf-8 -*-
"""
Created by Linjianhui on 2017/1/3
"""
import random
import string


def generate_id(len=10):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(len))
