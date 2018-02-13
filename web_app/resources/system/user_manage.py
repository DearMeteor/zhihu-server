# -*- coding: utf-8 -*-
"""
Created by Linjianhui on 2017/1/18
用户管理
"""
import json
import os

from flask_restful import Resource
from flask import request, session

from web_app import auth, app
from web_app.models.model import AdminUser, db
from . import api_path


class UserManage(Resource):
    decorators = [auth.login_required]
    api_url = [api_path + 'user_manage', api_path + 'user_manage/<int:user_id>', api_path + 'user_manage/<flag>']

    def get(self, **kwargs):
        """

        :return:
        """
        if 'user_id' in kwargs:
            user_id = kwargs['user_id']
            user_permission = db.session.query(AdminUser.permission).filter(AdminUser.id == user_id).first()
            if user_permission:
                if user_permission.permission:
                    return json.loads(user_permission.permission)
                    # return json.loads(user_permission.permission)
                else:
                    return {}
            else:
                return {'state': 400, 'msg': '用户不存在'}, 400
        else:
            if len(kwargs) == 0:
                menu_data = self.get_all_menu_tree()
                return {
                    'menu_data': menu_data
                }
            else:
                return self.get_all_user_data()

    def get_all_user_data(self):
        """
        获取所有用户
        :return:
        """
        user_list = db.session.query(
            AdminUser.id,
            AdminUser.user_name,
            AdminUser.real_name,
            AdminUser.is_admin
        ).all()
        data = [x._asdict() for x in user_list]
        return data

    def get_all_menu_tree(self):
        """
        获取所有导航菜单
        :return:
        """
        with open(os.path.join(app.root_path, '../menu_config.json')) as fs:
            return json.load(fs, encoding='utf8')

    def post(self):
        """
        post
        :return:
        """
        flag_fun_dict = {
            'change_password': self.change_password,
            'save_permission': self.save_permission,
            'create_user': self.create_user,
            'delete_user': self.delete_user,
            'changeAdmin': self.changeAdmin
        }
        form_data = request.get_json()
        flag = form_data['flag']
        fun = flag_fun_dict.get(flag)
        if fun:
            return fun(form_data)
        else:
            return {'state': 405, 'msg': '未知操作'}

    def change_password(self, form_data):
        """
        修改密码
        :param form_data:
        :return:
        """
        user_id = form_data['user_id']
        new_password = form_data['new_password']
        user = AdminUser.query.filter(AdminUser.id == user_id).first()
        user.hash_password(new_password)
        db.session.commit()
        return {'state': 0, 'msg': '密码修改成功'}

    def save_permission(self, form_data):
        """
        保存权限
        :param form_data:
        :return:
        """
        permission = form_data['permission']
        permission_str = json.dumps(permission, separators=(',', ':'))
        user_id = form_data['user_id']
        AdminUser.query.filter(AdminUser.id == user_id).update({
            AdminUser.permission: permission_str
        })
        db.session.commit()
        user = session['user']
        user['permission'] = permission_str
        session['user'] = user
        return {'state': 0, 'msg': '权限修改成功'}

    def create_user(self, form_data):
        """
        创建用户
        :param form_data:
        :return:
        """
        new_user = AdminUser(
            user_name=form_data['user_name'],
            real_name=form_data['real_name']
        )
        new_user.hash_password(form_data['password'])

        db.session.add(new_user)
        db.session.commit()
        res = {'state': 0, 'msg': '用户创建成功'} if new_user.id else {'state': 1, 'msg': '用户创建失败'}
        return res

    def changeAdmin(self, form_data):
        """
        修改管理员权限changeAdmin
        Anson
        :param form_data:
        :return:
        """
        user_id = form_data['id']
        is_admin = form_data['is_admin']
        user = AdminUser.query.filter(AdminUser.id == user_id).first()
        user.is_admin = is_admin
        db.session.commit()
        return {'state': 0, 'msg': '修改成功'}

    def delete_user(self, form_data):
        """
        删除用户
        :param form_data:
        :return:
        """
        user_id = form_data['user_id']
        if AdminUser.query.count() > 1:
            AdminUser.query.filter(AdminUser.id == user_id).delete()
            db.session.commit()
            res = {'state': 0, 'msg': '删除用户成功'}
        else:
            res = {'state': 1, 'msg': '至少保留一个用户'}
        return res
