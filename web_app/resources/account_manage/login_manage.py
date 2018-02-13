# _*_ coding:utf-8 _*_
"""
Created by yueliuxin on 2018/2/7
登录管理
"""

from flask import request
from flask_restful import Resource

from web_app import auth
from . import api_path


class LoginManage(Resource):
    decorators = [auth.login_required]
    api_url = [api_path + 'login_manage', api_path + 'login_manage/<flag>']

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
            'changeStatus': self.changeStatus
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
        account = form_data['account']
        phoneNumber = form_data['phoneNumber']

        """
        query = LoginInfo.query.filter(
            LoginInfo.account == account if account else text('')
        ).filter(
            LoginInfo.phone == phoneNumber if phoneNumber else text('')
        )
        if gameId != 0:
            query = query.filter(LoginInfo.game_id == gameId)
        data = query.order_by(
            LoginInfo.id.desc()
        ).all()
        """

        data = [{'account': u'987', 'last_login_time': '2018-08-08 10:10:10',
                 'ip': u'22.22.22.22', 'phone': u'13311111111', 'game_id': 104, 'id': 3},
                {'account': u'321', 'last_login_time': '2018-01-01 10:10:10',
                 'ip': u'11.11.11.11', 'phone': u'13387654321', 'game_id': 104, 'id': 2},
                {'account': u'123', 'last_login_time': '2018-02-07 15:23:36',
                 'ip': u'12.12.12.12', 'phone': u'13312345678', 'game_id': 102, 'id': 1}]

        table_data = []
        for item in data:
            if item['game_id'] == 102:
                gameName = '我在大清当皇帝'
            elif item['game_id'] == 104:
                gameName = '叫我万岁爷'
            else:
                gameName = '未知'
            account = item['account']
            isFrozen = True
            isIpBlocked = True
            gameId = item['game_id']
            phoneNumber = item['phone']
            lastLoginTime = item['last_login_time']
            lastLoginIp = item['ip']
            table_data.append({'gameId': gameId, 'gameName': gameName, 'account': account, 'phoneNumber': phoneNumber,
                               'lastLoginTime': lastLoginTime, 'lastLoginIp': lastLoginIp,
                               'isFrozen': isFrozen, 'isIpBlocked': isIpBlocked})
        return {'status': 0, 'msg': '', 'tableData': table_data}

    def changeStatus(self, form_data):
        """
        改变冻结状态
        """
        """
        gameId = form_data['gameId']
        account = form_data['account']
        state = form_data['state']
        type_ = form_data['type']

        data = db.session.query(
            AccountStatus
        ).filter(
            AccountStatus.game_id == int(gameId)
        ).filter(
            AccountStatus.account == int(account)
        ).first()
        if data:
            item = data.to_dict()
            if type_ == 'isFrozen':
                AccountStatus.query.filter(
                    AccountStatus.id == item['id']
                ).update({
                    'isFrozen': state,
                })
            else:
                AccountStatus.query.filter(
                    AccountStatus.id == item['id']
                ).update({
                    'isIpBlocked': state,
                })
            db.session.commit()
        """
        return {'state': 0, 'msg': ''}




