# _*_ coding:utf-8 _*_
"""
Created by Chenyuanyi on 2018/1/29
banner管理
"""
import json
from datetime import datetime

from flask import request, session
from flask_restful import Resource
from sqlalchemy import desc, func

from web_app import auth
from web_app.common.cjson_encoder import CJsonEncoder
from web_app.common.file_tool import remove_file
from web_app.models.model import GameInfo, BannerInfo, AdminUser, db
from . import api_path


class BannerManage(Resource):
    decorators = [auth.login_required]
    api_url = [api_path + 'banner_manage', api_path + 'banner_manage/<flag>']

    def __init__(self):
        self.datetime_format = '%Y-%m-%d %H:%M:%S'
        self.date_format = '%Y-%m-%d'
        self.model_key = [
            "game_id",
            "title",
            "creator",
            "create_time",
            "start_time",
            "end_time",
            "active_date",
            "style",
            "status",
            "link_url",
            "img_url"
    ]
    def get(self):
        """
        获得下拉框数据
        :return:
        """
        gameInfo = [x.to_dict() for x in GameInfo.query.order_by(GameInfo.game_id).all()]
        game_list = [{'label': x['game_name'], 'value': x['game_id']} for x in gameInfo]
        return {"status": 0, "message": "获取下拉数据成功", "game_list": game_list}

    def post(self, **kwargs):
        """
        post
        :return:
        """
        fun_dict = {
            'get_table_data': self.get_table_data,
            'modify_data': self.modify_data,
            'add_new_data': self.add_new_data,
            'delete_data': self.delete_data,
            'publish_data': self.publish_data
        }
        if 'flag' in kwargs:
            flag_name = kwargs.get('flag')
            form_data = request.get_json()
            fun = fun_dict.get(flag_name)
            if fun:
                return fun(form_data)
        else:
            return {'status': 1, 'message': '网络异常'}, 401

    def get_table_data(self, form_data):
        """
        获得表格数据
        :return:
        """
        page = int(form_data.get('page'))
        page_size = int(form_data.get('pageSize'))
        query = db.session.query(
            BannerInfo,
            GameInfo.game_name
        ).outerjoin(
            GameInfo, GameInfo.game_id == BannerInfo.game_id
        ).order_by(
            BannerInfo.game_id,
            desc(BannerInfo.create_time)
        )
        # 过滤查询条件
        query = self.set_query_filter(query, form_data)
        data = query.paginate(page=page, per_page=page_size)
        count = query.count()
        table_data = []
        for x in data.items:
            x = x._asdict()
            tmp = json.loads(json.dumps(x['BannerInfo'].to_dict(), cls=CJsonEncoder))
            tmp['status_name'] = u'已发布' if tmp['status'] == 2 else u'待发布'
            tmp['game_name'] = x['game_name']
            table_data.append(tmp)
        return {'status': 0, 'message': '成功获取banner数据', 'total': count, 'tableData': table_data}

    def set_query_filter(self, query, form_data):
        """
        设置查询过滤条件
        :param query:
        :param form_data:
        :return:
        """
        game_id = form_data.get('game_id')
        search_create_date = form_data.get('createDate')
        search_title = form_data.get('title')
        search_creator = form_data.get('creator')

        if game_id:
            query = query.filter(
                BannerInfo.game_id == game_id
            )
        if search_create_date:
            start_date, end_date = search_create_date[0], search_create_date[1]
            query = query.filter(
                func.date_format(BannerInfo.create_time, self.date_format) >= start_date,
                func.date_format(BannerInfo.create_time, self.date_format) <= end_date
            )
        if search_title:
            query = query.filter(
                BannerInfo.title.like('%' + search_title + '%')
            )
        if search_creator:
            query = query.filter(
                BannerInfo.creator == search_creator
            )
        return query

    def add_new_data(self,form_data):
        """
        添加数据
        :return:
        """
        banner_obj = BannerInfo()
        user = session.get('user')
        try:
            for key in self.model_key:
                value = form_data.get(key)
                if key == 'style':
                    if value:
                        value = json.dumps(value)
                    else:
                        value = json.dumps({"title_size": "", "title_color": ""})
                elif key == 'active_date':
                    start_date, end_date = value[0], value[1]
                    banner_obj.start_time = start_date
                    banner_obj.end_time = end_date
                if value is not None:
                    setattr(banner_obj, key, value)
            banner_obj.creator = user.get('user_name')
            banner_obj.create_time = datetime.now()
            banner_obj.status = 1
            db.session.add(banner_obj)
            db.session.commit()
            if banner_obj.id:
                return {'status': 0, 'message': '添加成功'}
            else:
                return {'status': 1, 'message': '添加失败'}
        except Exception as e:
            return {'status': 1, 'message': '添加失败'}

    def delete_data(self,form_data):
        """
        删除数据
        :return:
        """
        _id = form_data.get('_id')
        query = BannerInfo.query.filter(
            BannerInfo.id == _id
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

    def modify_data(self,form_data):
        """
        修改数据
        :return:
        """
        _id = form_data.get('id')
        query = BannerInfo.query.filter(
            BannerInfo.id == _id
        )
        data = query.first()
        if not data:
            return {'status': 1, 'message': '找不到该数据'}
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
            elif key == 'active_date':
                start_date, end_date = value[0], value[1]
                updata_dict['start_time'] = start_date
                updata_dict['end_time'] = end_date
                continue
            if value is not None:
                updata_dict[getattr(BannerInfo, key)] = value
        query.update(updata_dict)
        db.session.commit()
        return {'status': 0, 'message': '修改成功'}

    def publish_data(self,form_data):
        """
        发布数据
        :return:
        """
        _id = form_data.get('_id')
        query = BannerInfo.query.filter(
            BannerInfo.id == _id
        ).first()
        if query:
            query.status = 2
            db.session.commit()
            return {'status': 0, 'message': '发布成功'}
        else:
            return {'status': 1, 'message': '查不到此条记录'}
