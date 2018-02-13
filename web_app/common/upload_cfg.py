# _*_ coding:utf-8 _*_
"""
Created by Sunqi on 2017/9/4
"""

from web_app.common.wulin_profile import WulinProfile
from web_app.common.server import Server
try:
    UNICODE_EXISTS = bool(type(unicode))
except NameError:
    unicode = lambda s: str(s)

class ItemInfo():
    def __init__(self):
        self.item_info = dict()

    def get_item_info(self):
        """
        获得所有item的item_name和item_type-item
        :return:
        """
        if not self.item_info:
            item_dict_list = WulinProfile().get_item(0)
            item_dict = {item['label']: item['value'] for item in item_dict_list}
            self.item_info = item_dict
        return self.item_info

    def get_item_by_item_name(self, item_name):
        """
        通过item_name得到item
        :param item_name:
        :return:
        """
        item_type_item = self.get_item_info().get(unicode(item_name)) or self.get_item_info().get(unicode(item_name + ' '))
        item_type_item_list = item_type_item.split('-')
        item = item_type_item_list[1]
        return item

    def get_item_type_by_item_name(self, item_name):
        """
        通过item_name得到item_type
        :param item_name:
        :return:
        """
        item_type_item = self.get_item_info().get(item_name) or self.get_item_info().get(item_name + ' ')
        item_type_item_list = item_type_item.split('-')
        item_type = item_type_item_list[0]
        return item_type

    def get_item_type_name_by_item_name(self, item_name):
        """
        通过itme_name得到item_type_name
        :param item_name:
        :return:
        """
        item_type = self.get_item_type_by_item_name(item_name)
        item_type_name_dict = WulinProfile().get_item_type_name_dict()
        item_type_name = item_type_name_dict[int(item_type)]
        return item_type_name


class ServerInfo():
    def get_server_info(self):
        """
        得到区服名和区服Id字典
        :return:
        """
        server_info_list = Server().get_server_select()
        server_dict = {server['label']: server['value'] for server in server_info_list}
        return server_dict

    def get_server_id_by_server_name(self, server_name):
        """
        通过区服名字获得区服Id
        :param server_name:
        :return:
        """
        server_name_id_dict = self.get_server_info()
        server_id = server_name_id_dict.get(server_name)
        return server_id