#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/8/12 下午7:34
@Author  : Gie
@File    : inner_ip.py
@Desc    :
"""
import platform
import socket

import requests


def get_linux_inner_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('www.baidu.com', 0))
        ip = s.getsockname()[0]
    except:
        return

    return ip


def get_inner_ip():
    sys_platform = platform.system()

    if sys_platform == "Windows":
        inner_ip = socket.gethostbyname(socket.gethostname())
        print(f'get inner ip for windows: {inner_ip}')
        return [inner_ip, 'Windows']

    if sys_platform == "Linux":
        response = requests.get(f'http://ifconfig.me')
        inner_ip = response.text.strip()
        print(f"get inner ip for linux: {inner_ip}")
        return [inner_ip, 'Linux']
    elif sys_platform == "Darwin":
        inner_ip = socket.gethostname()
        print(f"get inner ip for MacOs: {inner_ip}")
        return [inner_ip, 'Darwin']
    else:
        print("Other System @ some ip")
        return
