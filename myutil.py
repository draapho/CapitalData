#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re
import csv
import datetime
import winreg
import pandas as pd

########### list #################
def l2i(value):     # list to index
    l = ['code', 'name', '当日', '异动', '资金', '股价', '序', '|', 'PE', 'PB', 'ROE', '利润', '市值', '个股']
    if value == '分':
        value = '序'
    if value == '板块':
        value = '个股'
    return l.index(value)


def get_data_path():
    return ".\\_data\\_info\\"

def get_defautl_path():
    return ".\\_para\\"

########### file / path ##########
class Gpath(object):
    def __init__(self, gpath=None):
        if gpath and os.path.exists(gpath) and os.path.isdir(gpath) and gpath.startswith('.\\'):  # 相对路径存在
            self.gpath = os.path.basename(gpath) + '\\'
        else:
            self.gpath = ".\\_para\\"

    def para_path(self):
        return self.gpath

    def report_file(self):
        return self.gpath + "report.txt"

    def block_path(self):
        return self.gpath + "blocks\\"

    def parameter_file(self):
        return self.gpath + "parameter.ini"

    def tmp_file(self):
        return self.gpath + "tmp"

    def tickers_csv(self):
        return self.gpath + "tickers.csv"

    def blocks_csv(self):
        return self.gpath + "blocks.csv"

    def read_parameter_ini(self):
        try:
            with open(self.parameter_file(), 'r', encoding="utf-8-sig") as csv_file:
                reader = csv.reader(skip_comments(csv_file))
                para = dict(reader)
        except Exception as e:
            para = {}
            print("Decode \"parameter.ini\" failed! ERR:{}".format(e))
        para['K_NUMBER'] = para.get('K_NUMBER',0)
        para['REF_DATE'] = para.get('REF_DATE',"")
        para['REF_LENGTH'] = para.get('REF_LENGTH',0)
        print (self.gpath, para)
        return para


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

"""
获取文件的最后一行.
如果最后一行的日期和输入的date相同, 则删除.
"""
def read_last_line(file, date, size=1024):
    last_line = b""
    if os.path.exists(file):
        # 读取文件最后一行
        with open(file, 'rb+') as f:
            # 在文本文件中，没有使用b模式选项打开的文件，只允许从文件头开始,只能seek(offset,0)
            if os.path.getsize(file) > size:
                f.seek(-size, os.SEEK_END)  # 从文件末尾开始向前1000个字符
                lines = f.readlines()
            else:
                lines = f.readlines()
            try:
                last_line = lines[-1]
                date_last = last_line.decode().split(',')[0]
            except Exception as e:
                last_line = b""
                print(e)
            else:
                # 日期相同, 则删除最后一行
                if date_last == date:
                    f.seek(-len(last_line), os.SEEK_END)
                    f.truncate()
    return last_line


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

A divisor of 1 => the thousands seperator
appropriate to ones locale is inserted.

With other divisors the output is aligned
in a 7 or 8 character column respectively,
which one can strip() if the display is not
using a fixed width font.
"""
def readableNum(num, divisor=1000, power="", sort=False, precision=1):
    num=float(num)
    if divisor == 1024:
        powers=["  ","Ki","Mi","Gi","Ti","Pi"]
    elif divisor == 10000:
        powers=[" ","万","亿","万亿","亿亿"]
    else:
        powers=[" ","K","M","G","T","P"]
    if not power: power=powers[0]
    while num >= 1000 or num <=-1000: #4 digits
        num /= divisor
        power=powers[powers.index(power)+1]
    if sort:
        format_str = "{}{:"+str(4+precision)+"."+str(precision)+"f}"  # "{}{:5.1f}"
        return format_str.format(power,num)
    else:
        format_str = "{:."+str(precision)+"f}{}" # "{:.1f}{}"
        return format_str.format(num,power)
