# -*- coding: utf-8 -*-
"""
Created by Linjianhui on 2017/1/16
"""
from flask_restful import Resource

from web_app import auth
from . import api_path


class ItemTree(Resource):
    decorators = [auth.login_required]
    api_url = api_path + 'item_tree/<int:item_type>'

    def get(self, item_type):
        """
        :param item_type:
        :return:
        """
        pass
