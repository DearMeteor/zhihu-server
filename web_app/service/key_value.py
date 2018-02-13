# -*- coding: utf-8 -*-
from sqlalchemy import func

from ..models.model import KeyValue, db


class KeyValueService(object):
    def get_by_type(self, types):
        """
        根据类型获取数据
        :param types: 
        :return: 
        """
        query = KeyValue.query.filter(
            KeyValue.types == types
        ).order_by(
            KeyValue.orders
        ).all()
        return query

    def get_select_by_type(self, types):
        """
        根据类型获取下拉列表
        :param types: 
        :return: 
        """
        data = self.get_by_type(types)
        res = [{'label': x.s_value, 'value': x.s_key} for x in data]
        return res

    def get_dict_by_type(self, types):
        """
        获取字典数据
        :param types: 
        :return: 
        """
        data = self.get_by_type(types)
        res = {x.s_key: x.s_value for x in data}
        return res

    def add_section(self, section):
        """
        添加版块
        :param section: 
        :return: 
        """
        query = KeyValue.query.filter(
            KeyValue.types == 'section',
            KeyValue.s_value == section
        ).all()
        max_order_query = db.session.query(
            func.max(KeyValue.orders).label('max_order')
        ).filter(
            KeyValue.types == 'section'
        ).first()
        if query:
            return {'status': 1, 'message': '已存在改版块，请不要重复添加!'}
        else:
            max_order = max_order_query.max_order + 1 if max_order_query.max_order is not None else 1
            k_v_obj = KeyValue()
            k_v_obj.types = 'section'
            k_v_obj.s_value = section
            k_v_obj.s_key = 'section_%d' % max_order
            k_v_obj.orders = max_order
            db.session.add(k_v_obj)
            db.session.commit()
            return {'status': 0, 'message': '添加成功'}
