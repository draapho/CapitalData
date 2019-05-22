# -*- coding: utf-8 -*-

import collect_data
from myutil import *
from tendo import singleton


def check_report():
    print ("===> start check_report <===")
    file = get_report_file()
    process = None
    with open(file, 'r') as f:
        for line in f.readlines():
            if line.startswith("data_start"):
                process = "blocks"
                list_blocks = []
            elif line.startswith("_____get_all_blocks"):
                process = "shares"
                list_shares= []
            elif line.startswith("_____get_all_shares"):
                process = "end"
            elif line.startswith("_____autofix_data"):
                list_blocks = []
                list_shares = []
            if process == "blocks":
                if "===>FAILED!" in line:
                    list_blocks.append(line.split(",")[0])
            elif process == "shares":
                if "===>FAILED!" in line:
                    list_shares.append(line.split(",")[0])
    print ("missed blocks:{}, missed shares:{}".format(list_blocks, list_shares))
    return list_blocks, list_shares


def fix_missed_data(blocks, shares):
    if len(blocks) or len(shares):
        cd = collect_data.collect_data()
        if (cd.update_check() is False):
            print ("===> start fix_missed_data <===")
            if len(blocks):
                cd.get_all_blocks(blocks)
            if len(shares):
                cd.get_all_shares(shares)

            # 更新report文件
            with open(get_report_file(), 'a') as f:
                f.write("_____autofix_data\rblocks:{}\rshares:{}\r".format(blocks, shares))
            print ("===> end fix_missed_data <===")
            return
    print("===> NOT need fix_missed_data <===")

if __name__ == '__main__':
    me = singleton.SingleInstance()
    blocks, shares = check_report()
    fix_missed_data(blocks, shares)
