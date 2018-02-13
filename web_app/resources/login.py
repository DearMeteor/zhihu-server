# -*- coding: utf-8 -*-
from flask import session, request
from flask_restful import Resource

from web_app.models.model import AdminUser
from . import api_path


class Login(Resource):
    api_url = api_path + 'login'

    def post(self):
        form_data = request.get_json()
        name = form_data.get('username')
        password = form_data.get('password')
        user = AdminUser.query.filter(AdminUser.user_name == name).first()
        if user:
            if password == user.password:
                session['user'] = user.to_dict()
            else:
                return {'status': 401, 'message': '密码错误'}, 401
        else:
            return {'status': 401, 'message': '该用户不存在'}, 401
        return {'status': 200, 'user_name': user.user_name}

    def get(self):
        """
        用户退出
        :return:
        """
        session['user'] = None
        session['token'] = None
        return {'status': 'ok'}
