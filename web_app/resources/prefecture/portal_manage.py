# -*- coding: utf-8 -*-
"""
发布相关操作类
"""
import json
import os
from datetime import datetime

from flask import request, session
from flask_restful import Resource
from sqlalchemy import desc, func

from web_app.common.file_tool import remove_file
from web_app.models.model import db, PublishInfo, GameInfo, KeyValue, Portal
from web_app import auth
from web_app.service.key_value import KeyValueService
from . import api_path


class PortalManage(Resource):
    decorators = [auth.login_required]
    api_url = [api_path + 'portal', api_path + 'portal/<flag>']
    model_key = [
        "game_id",
        "portal_name",
        "link_url",
        "img_url",
        "status"
    ]

    def __init__(self):
        self.datetime_format = '%Y-%m-%d %H:%M:%S'
        self.date_format = '%Y-%m-%d'
        self.key_value_service = KeyValueService()

    def get(self):
        pass

    def post(self, **kwargs):
        """
        POST
        :return: 
        """
        fun_dict = {
            'get_table_data': self.get_table_data,
            "add_new_data": self.add_new_data,
            "modify_data": self.modify_data,
            "delete_data": self.delete_data,
            "change_status": self.change_status
        }
        if 'flag' in kwargs:
            flag_name = kwargs.get('flag')
            form_data = request.get_json()
            fun = fun_dict.get(flag_name)
            if fun:
                return fun(form_data)
        else:
            return {'status': 1, 'message': '网络异常'}

    def get_table_data(self, form_data):
        """
        获取表格数据
        :param form_data: 
        :return: 
        """
        data = db.session.query(
            Portal.id,
            Portal.game_id,
            GameInfo.game_name,
            Portal.portal_name,
            Portal.link_url,
            Portal.img_url,
            Portal.status
        ).outerjoin(
            GameInfo, GameInfo.game_id == Portal.game_id
        ).all()
        table_data = [x._asdict() for x in data]
        return {'status': 0, 'message': 'ok', 'table_data': table_data}

    def add_new_data(self, form_data):
        portal_obj = Portal()
        try:
            for key in self.model_key:
                value = form_data.get(key)
                if value is not None:
                    setattr(portal_obj, key, value)
            portal_obj.status = 2
            db.session.add(portal_obj)
            db.session.commit()
            return {'status': 0, 'message': '添加成功'}
        except Exception as e:
            return {'status': 1, 'message': '添加失败'}

    def modify_data(self, form_data):
        """
        修改一条数据
        :param form_data: 
        :return: 
        """
        _id = form_data.get('id')
        query = Portal.query.filter(
            Portal.id == _id
        )
        data = query.first()
        if data:
            old_img_url = data.img_url
            updata_dict = {}
            for key in self.model_key:
                value = form_data.get(key)
                if key == 'img_url':
                    if str(old_img_url) != str(value):
                        remove_file(old_img_url)
                if value is not None:
                    updata_dict[getattr(Portal, key)] = value
            query.update(updata_dict)
            db.session.commit()
            return {'status': 0, 'message': '修改成功'}

    def delete_data(self, form_data):
        """
        删除一条数据
        :param form_data: 
        :return: 
        """
        _id = form_data.get('_id')
        query = Portal.query.filter(
            Portal.id == _id
        )
        if query.first():
            data = query.first()
            if data.img_url:
                remove_file(data.img_url)
            query.delete()
            db.session.commit()
            return {'status': 0, 'message': '删除成功'}
        else:
            return {'status': 1, 'message': '查不到此条记录'}

    def change_status(self, form_data):
        """
        置顶
        :param form_data: 
        :return: 
        """
        _id = form_data.get('_id')
        status = int(form_data.get('status'))
        query = Portal.query.filter(
            Portal.id == _id
        ).first()
        if query:
            query.status = status
            db.session.commit()
            message = '失效成功' if status == 2 else '生效成功'
            return {'status': 0, 'message': message}
        else:
            return {'status': 1, 'message': '查不到此条记录'}
