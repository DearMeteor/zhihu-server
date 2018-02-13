# -*- coding: utf-8 -*-
"""
Created by Linjianhui on 2017/1/10
网络请求发送
"""
import base64
import json
import uuid
from pprint import pprint

import binascii
import requests
from pprint import pprint

from web_app.common import generate_id
from web_app.utils.log.logger import logger

try:
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')
except NameError:
    pass

try:
    from urllib import urlencode, quote
except ImportError:
    from urllib.parse import urlencode, quote

from gevent import spawn, joinall

from config import ISBASE64, URLS


def print_error(*res):
    """
    打印文字到错误流
    :param res:
    :return:
    """
    for row in res:
        sys.stderr.writelines(str(row))


def game_server_http_single(params, res_list=None, callback=None, url=None):
    """
    单个游戏服务端http请求
    :param param:
    :param res_list:
    :return:
    """
    url = URLS["SERVER_URL"] if url is None else url
    logger.info('game_server_http_request', trace_id=generate_id(), extra={'url': url, 'params': params})
    headers = {"Content-Type": "application/json"}
    try:
        data = json.dumps(params)
        r = requests.post(url, data=data, headers=headers, timeout=30)
        res = r.text
        if ISBASE64 == 1:
            res = base64.decodestring(res)
        try:
            res = json.loads(res)
        except ValueError:
            print_error('ValueError: ', res)
            print_error('ValueError: ', params)
            if res == 'Address is denied':
                info = 'IP白名单阻拦'
            elif res.find('500 Internal Server Error') != -1:
                info = '请求api发生500错误'
            else:
                info = '其它未知字符串: %s' % res
            res = {
                'code': 500,
                'info': info
            }
    except requests.exceptions.ConnectionError:
        res = {"info": "ConnectionError", "code": 10001, "ActionId": 0}
    except requests.exceptions.Timeout:
        res = {"info": "Timeout", "code": 10001, "ActionId": 0}
    except ValueError:
        res = {"info": "No JSON", "code": 10001, "ActionId": 0}
    except binascii.Error:
        res = {"info": "base64解码异常", "code": 10001, "ActionId": 0}
    res['appId'] = params['appId']
    res['serverId'] = params['serverId']
    logger.info('game_server_http_response', trace_id=generate_id(), extra={'response': res})
    if callback:
        res = callback(res)
    if res_list is None:
        return res
    else:
        res_list.append(res)


def game_server_http(params, callback=None):
    """
    发送到游戏服务器请求
    :param params:
    :return:
    """
    res_list = []
    gls = []
    data = params['data']
    appServerData = params["appServerData"]
    for appId, serverId in appServerData.items():
        param_ = {}
        param_.update(data)
        param_.update({"appId": appId, "serverId": serverId})
        gl = spawn(game_server_http_single, param_, res_list, callback)
        gls.append(gl)
    joinall(gls)
    return res_list


def mass_mail_server_http(params):
    """
    群发邮件游戏服务器请求
    :param params:
    :return:
    """
    res_list = []
    gls = []
    for param in params:
        gl = spawn(game_server_http_single, param, res_list)
        gls.append(gl)
    joinall(gls)
    return res_list


def transactions_http(params, res_list=None):
    """
    支付中心请求
    :param params:
    :return:
    """
    url = params.get('url')
    data = params.get('data')
    logger.info('transactions_http_request', trace_id=generate_id(), extra={'url': url, 'params': data})
    data_urlencode = urlencode(data)
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    try:
        r = requests.post(url, data=data_urlencode, headers=headers, timeout=30)
        res = r.text
        if ISBASE64 == 1:
            res = base64.decodestring(res)
        try:
            res = json.loads(res)
        except ValueError:
            print_error('ValueError: ', res)
            print_error('ValueError: ', params)
            if res == 'Address is denied':
                info = 'IP白名单阻拦'
            elif res.find('500 Internal Server Error') != -1:
                info = '请求api发生500错误'
            else:
                info = '其它未知字符串: %s' % res
            res = {
                'StatusCode': 500,
                'Msg': info
            }
        res['Info'] = '提交成功' if res['StatusCode'] == 0 else ('提交失败' if res['Msg'] == '' else res['Msg'])
        res['Stat'] = res['StatusCode']
    except requests.exceptions.ConnectionError:
        res = {"Info": "ConnectionError", "Stat": 10001, "ActionId": 0}
    except requests.exceptions.Timeout:
        res = {"Info": "Timeout", "Stat": 10001, "ActionId": 0}
    except binascii.Error:
        res = {"Info": "base64解码异常", "Stat": 10001, "ActionId": 0}
    try:
        res['server_id'] = ['_'.join([str(data['AppId']), str(server)]) for server in
                            data['ServerId'].split(',').strip()]
    except AttributeError:
        res['server_id'] = "_".join([str(data['AppId']), str(data['ServerId'])])
    logger.info('transactions_http_response', trace_id=generate_id(), extra={'response': res})
    if res_list is None:
        return res
    else:
        res_list.append(res)


def redeem_code_http(params, res_list=None):
    """
    兑换码请求
    :param params:
    :return:
    """
    url = params.get('url')
    data = params.get('data')
    logger.info('redeem_code_http_request', trace_id=generate_id(), extra={'url': url, 'params': data})
    headers = {"Content-Type": "application/json"}
    try:
        data = json.dumps(data)
        r = requests.post(url, data=data, headers=headers, timeout=30)
        res = r.text
        if ISBASE64 == 1:
            res = base64.decodestring(res)
        try:
            res = json.loads(res)
        except ValueError:
            print_error('ValueError: ', res)
            print_error('ValueError: ', params)
            if res == 'Address is denied':
                info = 'IP白名单阻拦'
            elif res.find('500 Internal Server Error') != -1:
                info = '请求api发生500错误'
            else:
                info = '其它未知字符串: %s' % res
            res = {
                'status': 500,
                'Info': info
            }
        # res = json.loads(res)
        res['stat'] = res.get('stat', 1)
        if 'Info' not in res:
            res['Info'] = '提交成功' if res.get('stat') == 1 else '提交失败'
    except requests.exceptions.ConnectionError:
        res = {"Info": "ConnectionError", "Stat": 10001, "ActionId": 0}
    except requests.exceptions.Timeout:
        res = {"Info": "Timeout", "Stat": 10001, "ActionId": 0}
    except binascii.Error:
        res = {"Info": "base64解码异常", "Stat": 10001, "ActionId": 0}
    logger.info('redeem_code_http_response', trace_id=generate_id(), extra={'response': res})
    if res_list is None:
        return res
    else:
        res_list.append(res)


def user_center_http(param):
    """
    用户中心http请求
    :param param:
    :return:
    """
    url = param.get('url')
    logger.info('user_center_http', trace_id=generate_id(), extra={'url': url, 'params': param.get('data')})
    data = 'd=' + quote(urlencode(param['data']))
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    try:
        r = requests.post(url, data=data, headers=headers, timeout=30)
        res = r.text
        # res = json.loads(res)
        try:
            res = json.loads(res)
        except ValueError:
            print_error('ValueError: ', res)
            print_error('ValueError: ', param)
            if res == 'Address is denied':
                info = 'IP白名单阻拦'
            elif res.find('500 Internal Server Error') != -1:
                info = '请求api发生500错误'
            else:
                info = '其它未知字符串: %s' % res
            res = {
                'Stat': 500,
                'Info': info
            }
        res['Info'] = '提交成功' if res['Stat'] == 0 else ('提交失败' if res['Info'] == '' else res['Info'])
    except requests.exceptions.ConnectionError:
        res = {"Info": "ConnectionError", "Stat": 10001, "ActionId": 0}
    except requests.exceptions.Timeout:
        res = {"Info": "Timeout", "Stat": 10001, "ActionId": 0}
    except binascii.Error:
        res = {"Info": "base64解码异常", "Stat": 10001, "ActionId": 0}
    logger.info('user_center_http_response', trace_id=generate_id(), extra={'response': res})
    return res


if __name__ == '__main__':
    param = {
        'actionId': 20603,
        'appId': 1014,
        'serverId': [u'1'],
        'choice': 0,
        'isFull': 0,
        'page': 0,
        'pageSize': 100
    }
    resl = game_server_http_single(param)
    # print(resl['Info'])
    pprint(resl)
