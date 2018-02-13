# -*- coding: utf-8 -*-
"""
Created by Linjianhui on 2017/1/3
"""
import os
from flask import session, request
from flask_restful import Resource
from jinja2.utils import import_string

from web_app.models.model import AdminUser
from . import auth, api


# @auth.verify_password
# def verify_password(name, passwd):
#     """
#     密码认证
#     :return:
#     """
#     is_login = session.get('is_login', False)
#     if is_login and name == '':
#         return True
#     user = AdminUser.query.filter(AdminUser.name == name).first()
#     if user:
#         if user.verify_password(passwd):
#             session['is_login'] = True
#             session['user'] = user.to_dict()
#             return True
#     return False

def login_out():
    try:
        session['user'] = None
        session['token'] = None
    except:
        pass


@auth.verify_token
def verify_token(token):
    token = request.headers.get('Accept-Token')
    # is_login = session.get('token', False)
    if token:
        user_id = AdminUser.verify_auth_token(token)
        if user_id:
            if session['user']['id'] == user_id:
                return True
            else:
                login_out()
        else:
            login_out()
    return False


def ischildof(obj, cls):
    try:
        for i in obj.__bases__:
            if i is cls or isinstance(i, cls):
                return True
        for i in obj.__bases__:
            if ischildof(i, cls):
                return True
    except AttributeError:
        return ischildof(obj.__class__, cls)
    return False


view_set = set()
names = {
    'Resource',
    '__all__',
    '__builtins__',
    '__doc__',
    '__file__',
    '__name__',
    '__package__',
    'api_path',
    'request',
    'session',
    'json',
    'os',
    'auth',
    'app',
    '',
    None
}


def generator_router(dir_name, module_join):
    """
    自动导入路由
    :return:
    """
    for name in os.listdir(dir_name):
        file_name = os.path.join(dir_name, name)
        if os.path.isfile(file_name):
            if (
                                name.endswith('.py')
                            and not name.endswith('not_import.py')
                        and not name.endswith('router.py')
                    and not name.endswith('route.py')
                and name != '__init__.py'
            ):
                module_name = name[:name.rfind('.')]
                module_path = module_join + '.' + module_name
                module = import_string(module_path)
                for child in dir(module):
                    if child not in names:
                        child_module = getattr(module, child)
                        if ischildof(child_module, Resource):
                            child_module_name = module_path + '.' + child
                            if child_module_name not in view_set:
                                view_set.add(child_module_name)
                                try:
                                    if isinstance(child_module.api_url, basestring):
                                        api.add_resource(child_module, child_module.api_url)
                                    else:
                                        api.add_resource(child_module, *child_module.api_url)
                                except AssertionError:
                                    print('has: ' + child_module_name)

        elif name != '__pycache__':
            # pass
            generator_router(file_name, module_join + '.' + name)


dir_name = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'resources')
module_join = 'web_app.resources'
generator_router(dir_name, module_join)

from .resources import resources_router
