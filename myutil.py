#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re
import csv
import random
import pandas as pd

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

comment_pattern = re.compile(r'\s*#.*$')

########### file / path ##########
"""
HOW to use:
with open('data_with_comments.csv') as f:
    reader = csv.DictReader(skip_comments(f))
    for line in reader:
        print(line)
"""
def skip_comments(lines):
    comment_pattern = re.compile(r'\s*#.*$')

    for line in lines:
        line = re.sub(comment_pattern, '', line).strip()
        if line:
            yield line


"""
读取大型数据文件的任意行
http://www.lining0806.com/%E5%A6%82%E4%BD%95%E5%BF%AB%E9%80%9F%E8%AF%BB%E5%8F%96%E6%95%B0%E6%8D%AE%E6%96%87%E4%BB%B6%E8%8B%A5%E5%B9%B2%E8%A1%8C/
https://blog.csdn.net/u012762054/article/details/78384294

HOW to use:
N_to_end = 9
N_lines = 9
data = loadData('test.txt', N_to_end, N_lines) # 从倒数第N_to_end行数开始读取N_lines行
print data
"""
def loadData(file_path, skip_n_end, rows_n, **kwargs):
    lines = sum(1 for _ in csv.reader(open(file_path,'r', encoding='UTF-8')))
    # print lines
    if (skip_n_end == 0):
        skip_n_end = lines
    if (rows_n == 0):
        rows_n = lines
    data = pd.read_csv(file_path,
                      engine='c',
                      header=None,
                      skiprows=lines-skip_n_end,
                      nrows=rows_n,
                      **kwargs,
    )
    return data


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
