# _*_ coding:utf-8 _*_
"""
Created by yueliuxin on 2018/2/7
登录管理
"""

from flask import request
from flask_restful import Resource
from sqlalchemy import text
from config import JsonConfig

from web_app import auth
from web_app.common.datamine_server import DataMineServer
from web_app.models.model import GameInfo, db, Account, UserInfo
from . import api_path


class PersonalCentre(Resource):
    decorators = [auth.login_required]
    api_url = [api_path + 'personal_centre', api_path + 'personal_centre/<flag>']

    def __init__(self):
        self.datetime_format = '%Y-%m-%d %H:%M:%S'
        self.date_format = '%Y-%m-%d'

    def get(self):
        """
        获得下拉框数据
        :return:
        """
        gameInfo = [{'game_id': 102, 'game_config': u'', 'id': 1,
                     'game_name': u'\u6211\u5728\u5927\u6e05\u5f53\u7687\u5e1d'},
                    {'game_id': 104, 'game_config': None, 'id': 2, 'game_name': u'\u53eb\u6211\u4e07\u5c81\u7237'}]
        gameList = []
        data = [{'label': x['game_name'], 'value': x['game_id']} for x in gameInfo]
        gameList.extend(data)
        gameList.insert(0, {'label': '全部游戏', 'value': 0})
        return {"status": 0, "msg": "获取下拉数据成功", "gameList": gameList}

    def post(self, **kwargs):
        """
        post
        :return:
        """
        fun_dict = {
            'get_table_data': self.get_table_data,
            'getPersonalInfo': self.getPersonalInfo,
            'editInfo': self.editInfo,
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

    def get_table_data(self, form_data):
        """
        获得表格数据
        :return:
        """
        form_data = form_data.get('search_form')
        gameId = form_data['gameId']
        appId = form_data['appId']
        serverId = form_data['serverId']
        account = form_data['account']
        number = form_data['number']
        phoneNumber = form_data['phoneNumber']

        query = Account.query.filter(
            Account.account == account if account else text('')
        ).filter(
            Account.service_id == number if number else text('')
        ).filter(
            Account.phone == phoneNumber if phoneNumber else text('')
        )
        if gameId != 0:
            query = query.filter(Account.game_id == gameId)
        if appId != 0:
            query = query.filter(Account.appId == appId)
        if serverId != 0:
            query = query.filter(Account.serverId == serverId)
        data = query.order_by(
            Account.id.desc()
        ).all()

        table_data = []
        for x in data:
            item = x.to_dict()
            gameId = item['game_id']
            gameName = GameInfo.query.filter(GameInfo.game_id == item['game_id']).first().game_name
            account = item['account']
            serverName = 1
            serviceId = item['service_id']
            vipLv = item['vip_lv']
            vipExp = item['vip_exp']
            table_data.append({'gameId': gameId, 'gameName': gameName, 'account': account, 'serverName': serverName,
                               'serviceId': serviceId, 'vipLv': vipLv, 'vipExp': vipExp})
        return {'status': 0, 'msg': '', 'tableData': table_data}

    def getPersonalInfo(self, form_data):
        """
        获取个人信息
        """
        account = form_data['account']
        if account:
            data = db.session.query(
                UserInfo
            ).filter(
                UserInfo.account == int(account)
            ).first()
            if data:
                data = data.to_dict()
                self.personalInfo = data
                return {'state': 0, 'msg': '', 'data': data}
        return {'state': 1, 'msg': '账号信息错误'}

    def editInfo(self, form_data):
        """
        修改个人信息
        """
        form_data = form_data['info']
        account = form_data['account']

        data = db.session.query(
            UserInfo
        ).filter(
            UserInfo.account == int(account)
        ).first()
        if data:
            item = data.to_dict()
            UserInfo.query.filter(
                UserInfo.id == item['id']
            ).update({
                'name': form_data['name'],
                'birthdate': form_data['birthdate'],
                'identity_number': form_data['identity_number'],
                'phone': form_data['phone'],
                'wechat': form_data['wechat'],
                'qq': form_data['qq'],
                'mail': form_data['mail'],
                'address': form_data['address'],
            })
            db.session.commit()
        return {'state': 0, 'msg': ''}

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
