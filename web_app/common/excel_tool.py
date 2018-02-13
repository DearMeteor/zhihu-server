# -*- coding: utf-8 -*-
import os

from pyexcel_xls import get_data
from flask import request, make_response, send_file
from web_app import app


class ExcelTool:
    def read_excel_sheet1(self):
        """
        读取上传的excel数据
        :return: 第一个sheet，第二行开始的数据，默认第一行为标题不读取
        """
        try:
            file_bin = request.files['file']
            xls_data = get_data(file_bin)
            tmp = []
            for sheet_n in xls_data.keys():
                tmp.append(xls_data[sheet_n])
            excel_data = tmp[0] if len(tmp) > 0 else []
            data = [row for index, row in enumerate(excel_data) if index > 0]
            return data
        except TypeError as e:
            error = {'status': 1, 'message': e}
            return error

    def download_template_file(self, type_name):
        """
        下载excel文件
        :return:
        """
        app_root_path = app.root_path
        tmp_path = os.path.join(app_root_path, 'excel_template')
        file_name = type_name + '.xlsx'
        file_path = os.path.join(tmp_path, file_name)
        if os.path.exists(file_path):
            response = make_response(send_file(file_path))
            response.headers["Content-Disposition"] = "attachment; filename=" + file_name + ";"
            return response
