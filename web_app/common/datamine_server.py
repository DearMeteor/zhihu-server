# -*- coding: utf-8 -*-
from web_app.models.model import db
from config import JsonConfig


class DataMineServer(object):
    def __init__(self, game_id=None):
        self.game_id = game_id
        self.server_table = JsonConfig['SERVER_TABLE_NAME']
        self.table_name = self.server_table.get(str(self.game_id))
        self.MERGE_GAME = JsonConfig['MERGE_GAME']
        self.server_id_key = 'merge_server' if self.game_id in self.MERGE_GAME else 'server_id'
        #     if self.game_id in self.MERGE_GAME else 'server_id'
        self.server_name_key = 'merge_name' if self.game_id in self.MERGE_GAME else 'server_name'

    def get_datamine_server_select_by_game(self):
        """
        获取数据中心区服数据
        :return:
        """
        sql = 'select DISTINCT(%s) as merge_server, game_id, app_id, %s as merge_name ' \
              'from %s' % (self.server_id_key, self.server_name_key, self.table_name)
        sql_data = db.execute_bind(sql, bind='datamine').fetchall()
        return [{'label': x.merge_name, 'value': '%d_%d' % (x.app_id, x.merge_server)} for x in sql_data]

    def get_merge_server_id_name_dict(self):
        """
        获得合并后区服的id和区服名字字典
        :return:
        """
        sql = 'select DISTINCT(%s) as merge_server, game_id, app_id, %s as merge_name ' \
              'from %s' % (self.server_id_key, self.server_name_key, self.table_name)
        sql_data = db.execute_bind(sql, bind='datamine').fetchall()
        return {'%d_%d' % (x.app_id, x.merge_server): x.merge_name for x in sql_data}

    def get_merge_server_name_id_dict(self):
        """
        获得合并后区服的名字和区服的id字典
        :return:
        """
        sql = 'select DISTINCT(%s) as merge_server, game_id, app_id, area_type, %s as merge_name ' \
              'from %s' % (self.server_id_key, self.server_name_key, self.table_name)
        sql_data = db.execute_bind(sql, bind='datamine').fetchall()
        return {x.merge_name.replace(" ", ""): "%d_%d" % (x.merge_server, x.area_type) for x in sql_data}

    def get_all_app_id(self):
        """
        获得所有的app_id
        :return:
        """
        sql = 'select DISTINCT(app_id) as app_id from %s' % self.table_name
        sql_data = db.execute_bind(sql, bind='datamine').fetchall()
        return [x.app_id for x in sql_data]

    def get_server_id_by_app_id(self, app_id=None):
        """
        通过app_id得到区服id
        :return:
        """
        from collections import defaultdict
        if app_id is not None:
            sql = 'select %s as merge_server from %s where app_id = %s' % (self.server_id_key, self.table_name, app_id)
            sql_data = db.execute_bind(sql, bind='datamine').fetchall()
            return {app_id: [item.merge_server for item in sql_data]}
        else:
            sql = 'select app_id, DISTINCT(%s) as merge_server from %s order by app_id asc' % (
                self.server_id_key, self.table_name)
            sql_data = db.execute_bind(sql, bind='datamine').fetchall()
            app_server_dict = defaultdict(list)
            for item in sql_data:
                app_server_dict[item.app_id].append(item.merge_server)
            return app_server_dict

    def get_server_id_and_server_name_by_app_id(self, app_id):
        """
        通过app_id得到区服id和区服名字
        :return:
        """
        sql = 'select server_id, server_name from %s where app_id = %s' % (self.table_name, app_id)
        sql_data = db.execute_bind(sql, bind='datamine').fetchall()
        return [[item.server_id, item.server_name] for item in sql_data]

    def get_server_id_app_id_dict(self):
        """
        获得area_type和app_id字典
        :return:
        """
        sql = 'select DISTINCT app_id, area_type from %s order by app_id asc' % self.table_name
        sql_data = db.execute_bind(sql, bind='datamine').fetchall()
        server_id_app_id_dict = {}
        for item in sql_data:
            app_id = item.app_id
            area_type = item.area_type
            server_id_app_id_dict[area_type] = app_id
        return server_id_app_id_dict

    def get_all_datamine_server(self):
        """
        获取全部区服数据
        :return:
        """
        sql = '''
            select DISTINCT(merge_server) as server_id, dq_server.game_id, game_name, app_id, merge_name as server_name from dq_server
            LEFT JOIN game_info on game_info.game_id = dq_server.game_id
            union ALL
            select DISTINCT(server_id) as server_id, dq2_server.game_id, game_name, app_id, server_name from dq2_server
            LEFT JOIN game_info on game_info.game_id = dq2_server.game_id
            ORDER BY game_id, app_id, server_id
        '''
        data = db.execute_bind(sql, bind="datamine").fetchall()
        return data

    def get_server_ids_by_merge_server(self, server_ids):
        """
        根据合服id获取原区服id(有用)
        :param server_ids:
        :return:
        """
        sql_filter = self.get_server_sql_filter(server_ids)
        sql = '''
            select app_id, server_id, area_type from %s where %s 
        ''' % (self.table_name, sql_filter)
        data = db.execute_bind(sql, bind="datamine").fetchall()
        return ['%s_%s_%s' % (x.app_id, x.server_id, x.area_type) for x in data]

    def get_some_merge_server_ids_by_server_id(self, app_id, server_id):
        """
        通过server_id获取相同合服下的其他server_id(有用)
        :param app_id: 应用id
        :param server_id: 区服id
        :return:
        """
        sql = '''
            select server_id from %s where app_id = %s and merge_server = (
                select merge_server from %s where 
                app_id = %s and server_id = %s
            )
        ''' % (self.table_name, app_id, self.table_name, app_id, server_id)
        if self.game_id in self.MERGE_GAME:
            data = db.execute_bind(sql, bind="datamine").fetchall()
            return [x.server_id for x in data]
        else:
            return [server_id]

    def get_server_merge_server_dict(self):
        """
        获取原区服和合服区服字典(有用)
        :return:
        """
        game_table = JsonConfig['SERVER_TABLE_NAME']
        sql = ''
        for index, item in enumerate(game_table.items()):
            key = int(item[0])
            table_name = item[1]
            if int(key) in self.MERGE_GAME:
                sql = sql + ' select app_id, server_id, area_type, merge_server, merge_name from %s ' % table_name
            else:
                sql = sql + ' select app_id, server_id, area_type, server_id as merge_server, server_name as merge_name from %s ' \
                            % table_name
            if index < len(game_table) - 1:
                sql = sql + ' union all '

        data = db.execute_bind(sql, bind="datamine").fetchall()
        return {'%d_%d' % (x.app_id, x.server_id): [x.merge_server, x.merge_name, x.area_type] for x in data}

    def get_area_type_by_server(self, server_ids):
        """
        通过区服获取area_type
        :param server_ids:
        :return:
        """
        sql_filter = self.get_server_sql_filter(server_ids)
        sql = '''
            select area_type from %s where %s 
        ''' % (self.table_name, sql_filter)
        data = db.execute_bind(sql, bind="datamine").fetchall()
        return [x.area_type for x in data]

    def get_server_sql_filter(self, server_ids, app_str='app_id', is_server_table=True):
        """
        获取app_id和server_id的查询sql条件
        :param server_ids:
        :return:
        """
        sql_filter = ''
        app_server = {}
        server_id_key = self.server_id_key if is_server_table else 'server_id'
        for item in server_ids:
            app_id = item.split('_')[0]
            server_id = item.split('_')[1]
            app_server.setdefault(app_id, []).append(server_id)
        for index, (k, v) in enumerate(app_server.items()):
            server_id_str = ','.join(v)
            if index == 0:
                sql_filter = ' (%s = %s and %s in (%s)) ' % (app_str, k, server_id_key, server_id_str)
            else:
                sql_filter = sql_filter + ' or (%s = %s and %s in (%s)) ' % (app_str, k, server_id_key, server_id_str)
        return sql_filter
