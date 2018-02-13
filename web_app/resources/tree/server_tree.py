# -*- coding: utf-8 -*-
"""
Created by Linjianhui on 2017/4/7
"""

from flask_restful import Resource
from flask import request

from web_app import auth
from . import api_path


class ServerTree(Resource):
    decorators = [auth.login_required]
    api_url = [api_path + 'server_tree/<int:app_id>', api_path + 'server_tree', api_path + 'server_tree/<app_id>']

    def get(self, app_id=None):
        """
        区服下拉
        :param app_id:
        :return:
        """
        pass
        # if app_id is not None:
        #     server_obj = Server()
        #     if app_id == 0:
        #         res = server_obj.get_app_group_server_select()
        #     elif app_id == "all_app":
        #         res = server_obj.get_server_select()
        #     else:
        #         res = server_obj.get_server_select(app_id)
        #     return res
        # else:
        #     server_obj = Server()
        #     app_id = request.args['app_id']
        #     res = server_obj.get_all_app_server_id(app_id)
        #     return res

