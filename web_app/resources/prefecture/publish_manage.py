# -*- coding: utf-8 -*-
"""
发布相关操作类
"""
import json
import os
import uuid
from datetime import datetime

from flask import request, session
from flask_restful import Resource
from sqlalchemy import desc, func

from web_app.common.file_tool import remove_file
from web_app.models.model import db, PublishInfo, GameInfo, KeyValue
from web_app import auth, scheduler, app
from web_app.service.key_value import KeyValueService
from . import api_path


class PublishManage(Resource):
    decorators = [auth.login_required]
    api_url = [api_path + 'publish_manage', api_path + 'publish_manage/<flag>']
    model_key = [
        "game_id",
        "title",
        "content",
        "types",
        "creator",
        "create_time",
        "publish_time",
        "status",
        "style",
        "orders",
        "info_prop",
        "info_type",
        "is_now",
        "is_top",
        "img_url",
        "section"
    ]

    def __init__(self):
        self.datetime_format = '%Y-%m-%d %H:%M:%S'
        self.date_format = '%Y-%m-%d'
        self.key_value_service = KeyValueService()

    def get(self):
        types = request.args.get('types')
        if types == 'info_center':
            info_type = self.key_value_service.get_select_by_type('info_type')
            info_prop = self.key_value_service.get_select_by_type('info_prop')
            return {'info_type': info_type, 'info_prop': info_prop}
        elif types == 'vip_system':
            section_info = self.key_value_service.get_select_by_type('section')
            return {'section_info': section_info}
        else:
            return {'status': 1, 'message': '获取下拉列表失败'}

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
            "publish_data": self.publish_data,
            "change_order": self.change_order,
            "top_data": self.top_data,
            "add_section": self.add_section
        }
        if 'flag' in kwargs:
            flag_name = kwargs.get('flag')
            form_data = request.get_json()
            fun = fun_dict.get(flag_name)
            if fun:
                return fun(form_data)
        else:
            return {'status': 1, 'message': '网络异常'}

    @staticmethod
    def get_query(types):
        """
        根据类型获取查询字段
        :param types:
        :return:
        """
        if types in ['game_privilege', 'server_privilege']:
            query = db.session.query(
                PublishInfo.id,
                PublishInfo.game_id,
                PublishInfo.orders,
                PublishInfo.title,
                PublishInfo.content,
                PublishInfo.style,
                PublishInfo.status,
                PublishInfo.creator,
                PublishInfo.create_time,
                PublishInfo.img_url,
                PublishInfo.types,
                GameInfo.game_name
            ).outerjoin(
                GameInfo, GameInfo.game_id == PublishInfo.game_id
            )
        elif types == 'info_center':
            query = db.session.query(
                PublishInfo.id,
                PublishInfo.game_id,
                PublishInfo.orders,
                PublishInfo.info_type,
                PublishInfo.info_prop,
                PublishInfo.title,
                PublishInfo.content,
                PublishInfo.style,
                PublishInfo.status,
                PublishInfo.creator,
                PublishInfo.create_time,
                PublishInfo.publish_time,
                PublishInfo.img_url,
                PublishInfo.types,
                PublishInfo.is_now,
                PublishInfo.is_top,
                GameInfo.game_name
            ).outerjoin(
                GameInfo, GameInfo.game_id == PublishInfo.game_id
            ).order_by(
                desc(PublishInfo.is_top)
            )
        elif types == 'vip_system':
            query = db.session.query(
                PublishInfo.id,
                PublishInfo.game_id,
                PublishInfo.info_type,
                PublishInfo.info_prop,
                PublishInfo.title,
                PublishInfo.content,
                PublishInfo.style,
                PublishInfo.status,
                PublishInfo.creator,
                PublishInfo.create_time,
                PublishInfo.img_url,
                PublishInfo.types,
                PublishInfo.section,
                KeyValue.s_value.label('section_name'),
                GameInfo.game_name
            ).outerjoin(
                GameInfo, GameInfo.game_id == PublishInfo.game_id
            ).outerjoin(
                KeyValue, KeyValue.s_key == PublishInfo.section
            )
        else:
            query = None
        return query

    def set_query_filter(self, query, form_data):
        """
        设置查询过滤条件
        :param query:
        :param form_data:
        :return:
        """
        game_id = form_data.get('gameId')
        search_create_date = form_data.get('createDate')
        search_title = form_data.get('title')
        search_creator = form_data.get('creator')

        if game_id:
            query = query.filter(
                PublishInfo.game_id == game_id
            )
        if search_create_date:
            start_date, end_date = search_create_date[0], search_create_date[1]
            query = query.filter(
                func.date_format(PublishInfo.create_time, self.date_format) >= start_date,
                func.date_format(PublishInfo.create_time, self.date_format) <= end_date
            )
        if search_title:
            query = query.filter(
                PublishInfo.title.like('%' + search_title + '%')
            )
        if search_creator:
            query = query.filter(
                PublishInfo.creator == search_creator
            )
        return query

    def get_table_data(self, form_data):
        """
        获取表格数据
        :param form_data:
        :return:
        """
        page = int(form_data.get('page'))
        page_size = int(form_data.get('pageSize'))
        types = form_data.get('types')

        query = self.get_query(types)
        if query is None:
            return {'status': 1, 'message': '该页面无数据!'}
        query = query.filter(
            PublishInfo.types == types
        ).order_by(
            PublishInfo.orders
        )
        query = self.set_query_filter(query, form_data)
        data = query.paginate(page=page, per_page=page_size)
        total = query.count()
        table_data = []
        if types == 'info_center':
            info_type_dict = self.key_value_service.get_dict_by_type('info_type')
            info_prop_dict = self.key_value_service.get_dict_by_type('info_prop')

        for item in data.items:
            item = item._asdict()
            item['create_time'] = item.get('create_time').strftime(self.datetime_format)
            if item.get('publish_time'):
                item['publish_time'] = item.get('publish_time').strftime(self.datetime_format)
            if types == 'info_center':
                item['info_type_name'] = info_type_dict.get(item.get('info_type'))
                item['info_prop_name'] = info_prop_dict.get(item.get('info_prop'))
            table_data.append(item)
        return {'status': 0, 'message': 'ok', 'total': total, 'table_data': table_data}

    def add_new_data(self, form_data):
        pub_obj = PublishInfo()
        user = session.get('user')
        types = form_data.get('types')
        try:
            for key in self.model_key:
                value = form_data.get(key)
                if key == 'orders':
                    value = self.get_max_order(types)
                elif key == 'style':
                    if value:
                        value = json.dumps(value)
                    else:
                        value = json.dumps({"title_size": "", "title_color": ""})
                if value is not None:
                    setattr(pub_obj, key, value)
            pub_obj.creator = user.get('user_name')
            pub_obj.create_time = datetime.now()
            pub_obj.status = 1
            db.session.add(pub_obj)
            db.session.commit()
            if pub_obj.id and form_data.get('is_now', -1) == 2 and pub_obj.publish_time:  # 定时发布
                # misfire_grace_time 过期不超过misfire_grace_time时间的任务都将被执行 单位秒
                job_time = pub_obj.publish_time if pub_obj.publish_time > datetime.now() else datetime.now()
                scheduler.add_job('publish_job_%d' % pub_obj.id, publish_info_job, args=[pub_obj.id], trigger='date',
                                  run_date=job_time, replace_existing=True, misfire_grace_time=1000)
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
        query = PublishInfo.query.filter(
            PublishInfo.id == _id
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
                elif key == 'style':
                    if value:
                        value = json.dumps(value)
                    else:
                        value = json.dumps({"title_size": "", "title_color": ""})
                if value is not None:
                    updata_dict[getattr(PublishInfo, key)] = value
            data = query.first()
            query.update(updata_dict)
            db.session.commit()
            if form_data.get('is_now', -1) == 2 and data.status == 1 and form_data.get('publish_time', None):  # 定时发布
                publish_time = datetime.strptime(form_data['publish_time'], "%Y-%m-%d %H:%M:%S")
                job_time = publish_time if publish_time > datetime.now() else datetime.now()
                scheduler.add_job('publish_job_%d' % _id, publish_info_job, args=[_id], trigger='date',
                                  run_date=job_time, replace_existing=True, misfire_grace_time=1000)
            return {'status': 0, 'message': '修改成功'}

    def get_max_order(self, types):
        """
        获取最大排序
        :return:
        """
        query = db.session.query(
            func.max(PublishInfo.orders).label('orders')
        ).filter(
            PublishInfo.types == types
        ).first()
        max_order = query.orders + 1 if query.orders is not None else 1
        return max_order

    def delete_data(self, form_data):
        """
        删除一条数据
        :param form_data:
        :return:
        """
        _id = form_data.get('_id')
        query = PublishInfo.query.filter(
            PublishInfo.id == _id
        )
        if query.first():
            data = query.first()
            if data.img_url:
                remove_file(data.img_url)
            if data.is_now == 2 and data.status == 1:
                job_id = 'publish_job_%d' % _id
                if scheduler.get_job(job_id):
                    scheduler.delete_job(job_id)
            query.delete()
            db.session.commit()
            return {'status': 0, 'message': '删除成功'}
        else:
            return {'status': 1, 'message': '查不到此条记录'}

    def publish_data(self, form_data):
        """
        发布
        :param form_data:
        :return:
        """
        _id = form_data.get('_id')
        query = PublishInfo.query.filter(
            PublishInfo.id == _id
        ).first()
        if query:
            query.status = 2
            query.publish_time = datetime.now()
            db.session.commit()
            return {'status': 0, 'message': '发布成功'}
        else:
            return {'status': 1, 'message': '查不到此条记录'}

    def top_data(self, form_data):
        """
        置顶
        :param form_data:
        :return:
        """
        _id = form_data.get('_id')
        is_top = int(form_data.get('is_top'))
        query = PublishInfo.query.filter(
            PublishInfo.id == _id
        ).first()
        if query:
            query.is_top = is_top
            db.session.commit()
            message = '置顶成功' if is_top == 2 else '取消置顶成功'
            return {'status': 0, 'message': message}
        else:
            return {'status': 1, 'message': '查不到此条记录'}

    def change_order(self, form_data):
        """
        移动排序
        :param form_data:
        :return:
        """
        key = form_data.get('key')
        data = form_data.get('data')
        try:
            for item in data:
                _id = item.get('id')
                orders = item.get('orders')
                query = PublishInfo.query.filter(
                    PublishInfo.types == key,
                    PublishInfo.id == _id
                )
                if query.first():
                    query.update({
                        "orders": orders
                    })
                    db.session.flush()
                else:
                    return {'status': 1, 'message': '查不到相关记录'}
        except Exception as e:
            db.session.rollback()
            return {'status': 1, 'message': '移动失败'}
        db.session.commit()
        return {'status': 0, 'message': '移动成功'}

    def add_section(self, form_data):
        """
        添加版块
        :param form_data:
        :return:
        """
        section = form_data.get('section')
        return self.key_value_service.add_section(section)


def publish_info_job(info_id):
    with app.app_context():
        query = PublishInfo.query.filter(
            PublishInfo.id == info_id
        ).first()
        if query:
            query.status = 2
            query.publish_time = datetime.now()
            db.session.commit()
