#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import random

########### file / path ##########
def get_cur_dir():
    path = sys.path[0]
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)

def get_report_path():
    return get_cur_dir() + "\\_para\\"

def get_report_name():
    return "report.txt"

def get_report_file():
    return get_report_path() + get_report_name()



########### url para ##########
def get_token():
    # 通过以下网址的可以抓取有效 token 值
    # "http://data.eastmoney.com/zjlx/zs000001.html"
    # "http://data.eastmoney.com/zjlx/detail.html"
    token_list = ["70f12f2f4f091e459a279469fe49eca5",
                  "4f1862fc3b5e77c150a2b985b12db0fd",
                  "1942f5da9b46b069953c873404aad4b5",
                  "894050c76af8597a853f5b408b759f5d",]
    token = random.choice(token_list)
    return token

def get_rt():
    # min = 51675001
    # max = 51932721
    # rt = random.randint(min, max)
    # return str(rt)
    return "51932721"

def get__():
    # min = 1557200000001
    # max = 1557981070462
    # underline = random.randint(min, max)
    # return str(underline)
    return "1557981070462"
