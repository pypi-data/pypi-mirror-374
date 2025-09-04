#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/8/12 下午7:34
@Author  : Gie
@File    : bfLog.py
@Desc    :
"""

from datetime import datetime
from os.path import basename

from scrapy_tools import logger
from scrapy_tools._get_frame import get_frame

"""
基于loguru的日志模块
"""


def formatted_msg(msg, level, class_name="", func_name="", line_num="", track_id="", local_ip='',
                       pod_name='', module='', method_timecost='', input_params='', output=''):
    """
    :param output:
    :param method_timecost:
    :param input_params:
    :param module:      模块
    :param pod_name:    docker端口
    :param local_ip:    服务器ip
    :param msg:         日志内容
    :param level:       日志级别
    :param class_name:  调用模块
    :param line_num:    调用行号
    :param func_name:  调用方法名称
    :param track_id:    trackId
    :return:            格式化后的日志内容
    """
    formatted_level = "{0:>8}".format(f"{level}")
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    formatted_msg = (f"{ts} | {local_ip}:{pod_name} | {formatted_level} | {module}"
                     f" | {class_name}.{func_name}:{line_num} | {track_id} | {method_timecost}"
                     f" | {input_params} | {output} | {msg}")
    return formatted_msg


class Loguru:
    def __init__(self, deep=1, log_file="", local_ip='', pod_name='', module='', rotation='200 MB', minimum_level='INFO'):
        """
        :param deep:           获取调用者文件名、方法名、行号深度
        :log_file  :           输出日志文件目录
        :rotation  :           单文件大小
        :minimum_level  :      最低输入文件日志级别, 不影响控制台输出
        """
        self._frame = None
        self._msg = ""
        self._level = ""
        self._track_id = ""
        self._deep = deep
        self._p_track_id = ""
        self._pod_name = pod_name
        self._module = module
        self._method_timecost = ''
        self._input_params = ''
        self._output = ''
        self._local_ip = local_ip
        if log_file:
            logger.add(log_file,
                       format="{message}",
                       rotation=rotation,
                       level=minimum_level)

    def debug(self, msg):
        self._msg = msg
        self._level = "DEBUG"
        self._frame = get_frame(self._deep)
        return self

    def info(self, msg):
        self._msg = msg
        self._level = "INFO"
        self._frame = get_frame(self._deep)
        return self

    def warning(self, msg):
        self._msg = msg
        self._level = "WARNING"
        self._frame = get_frame(self._deep)
        return self

    def error(self, msg):
        self._msg = msg
        self._level = "ERROR"
        self._frame = get_frame(self._deep)
        return self

    def critical(self, msg):
        self._msg = msg
        self._level = "CRITICAL"
        self._frame = get_frame(self._deep)
        return self

    def p_track_id(self, p_track_id):
        self._p_track_id = p_track_id
        return self

    def pod_name(self, pod_name):
        self._pod_name = pod_name
        return self

    def module(self, module):
        self._module = module
        return self

    def method_timecost(self, method_timecost):
        self._method_timecost = method_timecost
        return self

    def input_params(self, input_params):
        self._input_params = input_params
        return self

    def output(self, output):
        self._output = output
        return self

    def track_id(self, track_id=''):
        self._track_id = (self._p_track_id + "-" + track_id) if self._p_track_id else track_id
        self._p_track_id = ""  # 置空p_track_id
        formatted_msg = formatted_msg(
            self._msg,
            self._level,
            basename(self._frame.f_code.co_filename),  # 脚本名称
            self._frame.f_code.co_name,  # 方法名
            str(self._frame.f_lineno),  # 行号
            self._track_id
        )
        logger.log(self._level, formatted_msg)
        return self

    def tracker(self, track_id=''):
        self._track_id = (self._p_track_id + "-" + track_id) if self._p_track_id else track_id
        self._p_track_id = ""  # 置空p_track_id
        formatted_msg = formatted_msg(
            self._msg,
            self._level,
            basename(self._frame.f_code.co_filename),  # 脚本名称
            self._frame.f_code.co_name,  # 方法名
            str(self._frame.f_lineno),  # 行号
            self._track_id,
            self._local_ip,
            self._pod_name,
            self._module,
            self._method_timecost,
            self._input_params,
            self._output

        )
        self.clear_field()
        logger.log(self._level, formatted_msg)
        return self

    def clear_field(self):
        self._output = ''
        self._input_params = ''
        self._method_timecost = ''
        self._pod_name = ''

    def commit(self):
        pass

if __name__ == '__main__':
    logger1 = Loguru()
    logger1.info('aaa').module('1').output('2').tracker('3')