# _*_ coding:utf-8 _*_
"""
Created by Sunqi on 2017/11/20
文件处理
"""

import os
import uuid

from werkzeug.utils import secure_filename

from web_app import app


class HandleFile():
    """
    文件处理
    """
    def __init__(self, file_save_path=None):
        if file_save_path is None:
            self.file_save_path = os.path.join(app.root_path, 'upload')
        else:
            self.file_save_path = file_save_path
        if not os.path.exists(self.file_save_path):
            os.makedirs(self.file_save_path)

    def generate_file_full_name(self, file_obj, file_name=None):
        """
        生成文件的全路径名
        :param file_obj:
        :return:
        """
        file_extension = os.path.splitext(secure_filename(file_obj.filename))[1]
        if file_name is None:
            file_name = '{0}{1}'.format(uuid.uuid4().hex, file_extension)
        else:
            file_name = '{0}{1}'.format(file_name, file_extension)
        file_full_name = os.path.join(self.file_save_path, file_name)
        return file_full_name

    def save_file(self, file_obj, file_name=None):
        """
        保存文件
        :param file_obj:
        :return:
        """
        file_full_name = self.generate_file_full_name(file_obj, file_name)
        file_obj.save(file_full_name)
        return file_full_name

    def get_api_file_path(self, file_full_name):
        """
        得到文件api地址
        :param file_full_name:
        :return:
        """
        upload_count = file_full_name.count("upload")
        if upload_count != 1:
            return None
        upload_site = file_full_name.find("upload")
        if upload_site == -1:
            return None
        sub_path = file_full_name[upload_site:]
        api_file_name = os.path.join("/api/", sub_path)
        return api_file_name

    def delete_file(self, re_file_full_name):
        """
        删除本地图片
        :param file_full_name:
        :return:
        """
        if not os.path.isfile(re_file_full_name):
            dirname, re_file_name = os.path.split(re_file_full_name)
            for root, dirs, files in os.walk(dirname):
                for file_ in files:
                    file_name, ext = os.path.splitext(file_)
                    # if re_file_name == file_name:
                    if file_name.startswith(re_file_name):
                        # file_full_name = "{0}{1}".format(re_file_full_name, ext)
                        os.remove(os.path.join(dirname, file_))
        else:
            if os.path.exists(re_file_full_name):
                os.remove(re_file_full_name)










