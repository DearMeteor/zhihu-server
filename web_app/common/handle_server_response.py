# _*_ coding:utf-8 _*_
"""
Created by Sunqi on 2017/11/17
"""


class HandleServerResponse():
    """
    处理服务端返回的数据
    """

    def __init__(self):
        self.msg = ''
        self.state = 0

    def handle_multi_app_server_response(self, data=None, server_res=None, field_name=None, field_name_other=None):
        """
        处理多次请求返回的数据
        :return:
        """
        msg = ''
        state = 0
        for res in server_res:
            if res.get('code'):
                state += res['code']
                msg += "应用编号{0}：请求失败-{1}\n".format(res["appId"], res['info'])
            else:
                serverId = res["serverId"]
                appId = res['appId']
                for s in serverId:
                    resServer = res[s]
                    if resServer['code'] == 0 and data is not None:
                        if field_name_other is None:
                            data.append((appId, s, resServer['info'].get(field_name, '')))
                        else:
                            data.append((appId, s, resServer['info'].get(field_name, ''), resServer['info'][field_name_other]))
                    elif resServer['code'] == 0 and data is None:
                        pass
                    else:
                        state += resServer['code']
                        msg += "应用编号{0}-区服编号{1}: 请求失败-{2}\n".format(res["appId"], s, resServer["info"])
        if data is None:
            return msg, state
        else:
            return msg, state, data

    def handle_single_app_server_response(self, data=None, server_res=None, field_name=None, field_name_other=None):
        """
        处理单次请求返回的数据
        :param data:
        :param server_res:
        :return:
        """
        msg = ''
        state = 0
        if server_res.get("code"):
            state = server_res.get("code")
            if server_res.get("info"):
                msg = server_res.get("info")
        else:
            serverId = server_res["serverId"]
            appId = server_res['appId']
            for s in serverId:
                resServer = server_res[s]
                if resServer['code'] == 0 and data is not None:
                    if field_name_other is None:
                        data.append((appId, s, resServer['info'].get(field_name, '')))
                    else:
                        data.append((appId, s, resServer['info'].get(field_name, ''), resServer['info'][field_name_other]))
                elif resServer['code'] == 0 and data is None:
                    pass
                else:
                    state += resServer['code']
                    msg += "应用编号{0}-区服编号{1}: 请求失败-{2}\n".format(appId, s, resServer["info"])
                    data.append((appId, s))
        if data is None:
            return msg, state
        else:
            return msg, state, data

    def handle_single_app_server_query_response(self, data=None, server_res=None, field_name=None,
                                                field_name_other=None):
        """
        处理单次请求查询表返回的数据
        :param data:
        :param server_res:
        :return:
        """
        msg = ''
        state = 0
        serverId = server_res["serverId"]
        appId = server_res['appId']
        if server_res.get('code') == 0 and data is not None:
            if field_name_other is None:
                data.append((appId, serverId, server_res['info'][field_name]))
            else:
                data.append((appId, serverId, server_res['info'][field_name], server_res['info'][field_name_other]))
        elif server_res['code'] == 0 and data is None:
            pass
        else:
            state += server_res.get('code')
            msg += "应用编号{0}-区服编号{1}: 请求失败-{2}\n".format(appId, serverId, server_res["info"])
        if data is None:
            return msg, state
        else:
            return msg, state, data
