# _*_ coding:utf-8 _*_
"""
Created by yueliuxin on 2018/2/9
"""

from flask import request
from flask_restful import Resource
from config import JsonConfig

from web_app import auth
from web_app.common.datamine_server import DataMineServer
from web_app.models.model import GameInfo
from . import api_path


class GameAppServerSelect(Resource):
    decorators = [auth.login_required]
    api_url = [api_path + 'game_app_server_select', api_path + 'game_app_server_select/<flag>']

    def __init__(self):
        self.datetime_format = '%Y-%m-%d %H:%M:%S'
        self.date_format = '%Y-%m-%d'

    def get(self):
        """
        获得下拉框数据
        :return:
        """
        gameInfo = [x.to_dict() for x in GameInfo.query.order_by(GameInfo.game_id).all()]
        gameList = []
        data = [{'label': x['game_name'], 'value': x['game_id']} for x in gameInfo]
        gameList.extend(data)
        gameList.insert(0, {'label': '全部游戏', 'value': 0})
        return {"status": 0, "msg": "获取下拉数据成功", "gameInfo": gameList}

    def post(self, **kwargs):
        """
        post
        :return:
        """
        fun_dict = {
            'getAppInfo': self.getAppInfo,
            'getServerInfo': self.getServerInfo

        }
        if 'flag' in kwargs:
            flag_name = kwargs.get('flag')
            form_data = request.get_json()
            fun = fun_dict.get(flag_name)
            if fun:
                return fun(form_data)
        else:
            return {'status': 1, 'msg': '网络异常'}, 401

    def getAppInfo(self, form_data):
        """
        根据游戏获取区服信息
        """
        gameId = form_data['gameId']
        if gameId == 0:
            return {'state': 0, 'msg': '', 'appInfo': []}
        serverData = DataMineServer(game_id=gameId)
        appIds = serverData.get_all_app_id()
        allAppInfo = JsonConfig['APP_INFO']
        appInfo = []
        for item in appIds:
            data = [{'label': allAppInfo[str(item)], 'value': item}]
            appInfo.extend(data)
        firstServerInfo = serverData.get_server_id_and_server_name_by_app_id(app_id=appInfo[0]['value'])
        serverInfo = []
        for item in firstServerInfo:
            serverInfo.append({'label': item[1], 'value': item[0]})
        appInfo.insert(0, {'label': '全部应用', 'value': 0})
        serverInfo.insert(0, {'label': '全部区服', 'value': 0})
        return {'state': 0, 'msg': '', 'appInfo': appInfo, 'serverInfo': serverInfo}

    def getServerInfo(self, form_data):
        """
        根据应用获取区服信息
        """
        gameId = form_data['gameId']
        appId = form_data['appId']
        serverData = DataMineServer(game_id=gameId)
        firstServerInfo = serverData.get_server_id_and_server_name_by_app_id(appId)
        serverInfo = []
        for item in firstServerInfo:
            serverInfo.append({'label': item[1], 'value': item[0]})
        serverInfo.insert(0, {'label': '全部区服', 'value': 0})
        return {'state': 0, 'msg': '', 'serverInfo': serverInfo}




