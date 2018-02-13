# -*- coding: utf-8 -*-
import json
import os

from flask import session
from flask_restful import Resource
from ..service.game_info import GameInfoService
from .. import auth
from .. import app
from . import api_path


class Menu(Resource):
    decorators = [auth.login_required]
    api_url = api_path + 'menu'
    game_service = GameInfoService()

    def get(self):
        with open(os.path.join(app.root_path, '../menu_config.json')) as fs:
            menu_data = json.load(fs, encoding='utf8')
        user = session.get('user')
        if user:
            if user['permission']:
                menu_permission = json.loads(user['permission']).get('menu')
            else:
                menu_permission = []
            menu_list = self.menu_filter(menu_data, menu_permission)
            game_data = self.game_service.get_game_select()
            return {'menu_data': menu_list, 'game_data': game_data}
        else:
            return {'state': 401, 'msg': '用户未登陆'}, 401

    def menu_filter(self, menu_data, menu_permission):
        """
        递归去除导航
        :param menu_data:
        :param menu_permission:
        :return:
        """
        new_menu_data = []
        for menu_item in menu_data:
            if menu_item['index'] in menu_permission:
                new_menu_data.append(menu_item)
            elif 'children' in menu_item:
                new_children = self.menu_filter(menu_item['children'], menu_permission)
                if len(new_children) > 0:
                    menu_item['children'] = new_children
                    new_menu_data.append(menu_item)
        return new_menu_data
