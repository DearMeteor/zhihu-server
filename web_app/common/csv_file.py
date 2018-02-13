# _*_ coding:utf-8 _*_
"""
Created by Sunqi on 2017/7/5
"""

import codecs
import csv
import json
import os
from zipfile import ZipFile

import shutil

from io import BytesIO
from datetime import datetime
import time


class ExcelTable:
    def __init__(self):
        from web_app import app
        self.app = app
        self.sio = BytesIO()
        self.csv_writer = csv.writer(self.sio, dialect=csv.excel)
        self.save_path = os.path.join(app.root_path, 'static/table_file/')
        self.max_size = 60000
        self.sys_name = os.name

    def write_excel(self, excel_datas):
        for row in excel_datas:
            self.writerow(row)

    def writerow(self, row):
        self.csv_writer.writerow(row)

    def save_excel(self):
        data = self.sio.getvalue().encode('gbk')
        res = self.app.make_response(data)
        cur_time = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        res.headers['Content-Disposition'] = 'attachment;filename="' + cur_time + '.csv"'
        res.headers['Content-Type'] = 'text/csv'
        return res

    def create_excel_table(self, excel_data):
        self.write_excel(excel_data['table_datas'])
        res = self.save_excel()
        return res

    def create_excel_table_file(self, file_name, excel_data):
        file_path = os.path.join(self.save_path, file_name)
        with open(file_path, 'w') as fd:
            self.write_excel(excel_data['table_datas'])
            data = self.sio.getvalue()
            data = codecs.BOM_UTF8 + data
            fd.write(data)
            fd.close()
            self.sio.truncate(0)

    def async_create_excel_table_file(self, excel_datas):
        """
        异步获取表格数据保存到文件提供下载
        :param excel_datas:
        :return:
        """
        page_excel_datas = []
        for excel_data in excel_datas:
            data_len = len(excel_data['table_datas'])
            count = data_len / self.max_size
            if count > 0:
                for i in range(count):
                    start = i * self.max_size
                    end = (i + 1) * self.max_size
                    end = data_len if end > data_len else end
                    tmp_data = {
                        'sheet_title': '%s_%d' % (excel_data['sheet_title'], i + 1),
                        'table_datas': excel_data['table_datas'][start:end]
                    }
                    page_excel_datas.append(tmp_data)
            else:
                page_excel_datas.append(excel_data)
        dir_name = str(time.time())
        if not os.path.exists(os.path.join(self.save_path, dir_name)):
            os.mkdir(os.path.join(self.save_path, dir_name))
        file_info = {
            'last_time': dir_name
        }
        file_names = []
        for excel_data in page_excel_datas:
            file_name = u'%s/%s.csv' % (dir_name, excel_data['sheet_title'])
            if self.sys_name == 'posix':
                file_name = file_name.encode("utf-8")
            file_names.append(file_name)
            self.create_excel_table_file(file_name, excel_data)
        file_info['file_names'] = file_names
        zip_name = os.path.join(self.save_path, dir_name)
        with ZipFile(zip_name + '.zip', 'w') as zip_fd:
            os.chdir(self.save_path)
            for file_name in file_names:
                zip_fd.write(file_name)
        shutil.rmtree(zip_name)
        with open(os.path.join(self.save_path, 'file_info.json'), 'r+') as fd:
            json_arr = json.load(fd)
            json_arr = self.del_old_dir(json_arr, fd)
            json_arr.append(file_info)
        with open(os.path.join(self.save_path, 'file_info.json'), 'w') as fd:
            json.dump(json_arr, fd)
        return {'state': 0, 'msg': '生成完成:<a href="/static/table_file/' + dir_name + '.zip">下载地址<a/>'}

    def del_old_dir(self, json_arr, fd, day=2):
        """
        删除旧的文件夹
        :param json_arr:
        :param fd:
        :return:
        """
        old_time = float(time.time()) - day * 86400000
        new_arr = []
        for item in json_arr:
            last_time = float(item['last_time'])
            if last_time < old_time:
                dir_path = os.path.join(self.save_path, item['last_time'] + '.zip')
                if os.path.exists(dir_path):
                    os.remove(dir_path)
            else:
                new_arr.append(item)
        return new_arr

    def create_echartdata_csv(self, echart_data):
        """

        :param echart_data:
        :return:
        """
        legend_data = echart_data['legend']['data']
        legend_data.insert(0, "时间")
        series_data = [echart_data['xAxis']['data']]
        for row in echart_data['series']:
            series_data.append(row['data'])
        series_data = zip(*series_data)
        legend_data = [legend_data]
        legend_data.extend(series_data)
        self.write_excel(legend_data)
        res = self.save_excel()
        return res
