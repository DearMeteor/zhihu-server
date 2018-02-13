# -*- coding: utf-8 -*-
import os
import time

from flask import session, json
from werkzeug.utils import secure_filename

from web_app.resources import UPLOAD_ROOT_PATH


def save_file(file_obj, upload_path, *params):
    """
    :param file_obj: 文件
    :param upload_path: 保存路径
    :return: 
    """
    file_type = params[0] if params else ''
    if file_type:
        tmp_file = session.get(file_type)
    else:
        tmp_file = session.get('tmp_file')
    if tmp_file:
        try:
            pass
            # os.remove(tmp_file)
        except:
            pass
    image_name = '%d-%s' % (int(time.time()), secure_filename(file_obj.filename))
    save_path = os.path.join(upload_path, image_name)
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)
    file_obj.save(save_path)
    if file_type:
        session[file_type] = save_path
        list_file = session.get('list_file') if session.get('list_file') else {}
        list_file[file_type] = save_path
        session['list_file'] = list_file
    else:
        session['tmp_file'] = save_path
    return image_name


def remove_file(file_url):
    """
    删除一个文件
    :param file_url: 
    :return: 
    """
    img_url = file_url[len('/api/upload/'):]
    file_path = os.path.join(UPLOAD_ROOT_PATH, img_url)
    if os.path.exists(file_path):
        os.remove(file_path)
