# -*- coding: utf-8 -*-
import os

from flask import send_from_directory, request

from web_app import app
from web_app.common.excel_tool import ExcelTool
from web_app.common.file_tool import save_file
from web_app.resources import UPLOAD_ROOT_PATH


@app.route('/api/download/<string:type_name>', methods=['GET'])
def download_excel_template(type_name):
    return ExcelTool().download_template_file(type_name)


@app.route('/api/upload/<string:sub_path>/<string:file_name>', methods=['GET'])
def response_file_to_client(sub_path, file_name):
    file_save_path = os.path.join(app.root_path, 'upload')
    file_path_name = os.path.join(file_save_path, sub_path)
    return send_from_directory(file_path_name, file_name)


@app.route('/api/upload_image/<string:image_folder>', methods=['POST'])
def upload_image(image_folder):
    """
    一个页面单个图片上传
    :param image_folder: 保存图片的文件夹名称。
    :return: 
    """
    image = request.files['file']
    UPLOAD_PATH = os.path.join(UPLOAD_ROOT_PATH, image_folder)
    image_url = '/api/upload/' + image_folder + '/'
    image_name = save_file(image, UPLOAD_PATH)
    return image_url + image_name


@app.route('/api/upload_image_multiple/<string:image_folder>/<string:image_type>', methods=['POST'])
def upload_multiple(image_folder, image_type):
    """
    一个页面多个图片上传
    :param image_folder: 
    :param image_type: 
    :return: 
    """
    image = request.files['file']
    UPLOAD_PATH = os.path.join(UPLOAD_ROOT_PATH, image_folder)
    image_url = '/api/upload/' + image_folder + '/'
    image_name = save_file(image, UPLOAD_PATH, image_type)
    return image_url + image_name


@app.route('/api/remove_upload', methods=['POST'])
def remove_upload():
    params = request.get_json().get('params')
    urls = []
    if params:
        urls = [v.get('url')[len('/api/upload/'):] for k, v in params.items()]
    for file_url in urls:
        file_path = os.path.join(UPLOAD_ROOT_PATH, file_url)
        if os.path.exists(file_path):
            os.remove(file_path)
    return 'ok'
