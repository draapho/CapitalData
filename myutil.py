#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re
import csv
import random
import locale
import pandas as pd

########### file / path ##########
def get_cur_dir():
    path = sys.path[0]
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)

def get_data_path():
    return ".\\_data\\_info\\"

def get_para_path():
    # return get_cur_dir() + "\\_para\\"
    return ".\\_para\\"

def get_report_name():
    return "report.txt"

def get_report_file():
    return get_para_path() + get_report_name()

def get_parameter_name():
    return "parameter.ini"

def get_parameter_file():
    return get_para_path() + get_parameter_name()

comment_pattern = re.compile(r'\s*#.*$')


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
print (data)
"""
def loadData(file_path, skip_n_end, rows_n, **kwargs):
    # lines = sum(1 for _ in csv.reader(open(file_path,'r', encoding='UTF-8')))
    lines = 0
    fp = open(file_path, "r", encoding='utf-8')
    while True:
        buffer = fp.read(8*1024*1024)
        if not buffer:
            break
        lines += buffer.count('\n')
    fp.close()
    # print(lines)

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
def get_cb():
    return "jQuery0_0"

def get_rt():
    return "0"

def get__():
    return "0"


########## number ##########
"""
Convert a number for human consumption

Divisor can be 1, 1000, 1024

If the locale has been set before this
function is called, then numbers appropriate to the
locale will be retured. This is commonly done like:
    locale.setlocale(locale.LC_ALL,'')

A divisor of 1 => the thousands seperator
appropriate to ones locale is inserted.

With other divisors the output is aligned
in a 7 or 8 character column respectively,
which one can strip() if the display is not
using a fixed width font.
"""
def readableNum(num, divisor=1000, power=""):
    num=float(num)
    if divisor == 1000:
        powers=[" ","K","M","G","T","P"]
    elif divisor == 1024:
        powers=["  ","Ki","Mi","Gi","Ti","Pi"]
    elif divisor == 10000:
        powers=[" ","万","亿","万亿","亿亿"]
    else:
        return locale.format("%.f",num,1)
    if not power: power=powers[0]
    while num >= 1000: #4 digits
        num /= divisor
        power=powers[powers.index(power)+1]
    if power.strip():
        num = locale.format("%.2f",num,1)
    else:
        num = locale.format("%.2f  ",num,1)
    return "%s%s" % (num,power)


if __name__ == '__main__':
    print (readableNum(1264, divisor=10000))
