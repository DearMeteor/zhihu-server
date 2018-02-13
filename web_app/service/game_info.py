# -*- coding: utf-8 -*-
from ..models.model import GameInfo, db


class GameInfoService(object):
    def __init__(self):
        pass

    def get_all_game(self):
        """
        获取所有游戏
        :return: 
        """
        query = GameInfo.query.all()
        return query

    def get_game_select(self):
        """
        获取游戏下拉列表
        :return: 
        """
        data = self.get_all_game()
        return [{'label': x.game_name, 'value': x.game_id} for x in data]
