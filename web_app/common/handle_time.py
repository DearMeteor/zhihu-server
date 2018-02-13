# _*_ coding:utf-8 _*_
"""
Created by Sunqi on 2017/9/27
"""

from datetime import date

def date_str_to_date(date_str):
    """
    将日期字符串变成日期格式
    :param date_str:
    :return:
    """
    ymd = [int(x) for x in date_str.split('-')]
    return date(*ymd)