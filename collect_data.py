#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import datetime
import time
import pytz
from myutil import *
from tendo import singleton
from ast import literal_eval


class collect_data(object):
    def __init__(self):
        self.time_str = None
        self.url = None
        self.rd = {}

    def requests_get(self, url, comment=""):
        for i in range(3):
            try:
                print("{} {}".format(comment, url))
                r = requests.get(url, timeout=30)
                # print (r.text)
                break
            except Exception as e:
                t = time.strftime("%H%M%S", time.localtime())
                self.rd["url_err_{}".format(t)] = url
                # 替换原来的token值
                pattern = r'token=(.*?)&'
                url = re.sub(pattern, "token={}&".format(get_token()), url)
                # 10s后重试连接
                print("10s后重试. 错误:{}".format(e))
                time.sleep(10)
                r = None
        if r is None:
            raise Exception("===>FAILED! requests_get: {}".format(url))
        return r

    def get_day_detail(self, id):
        # 单日资金流明细, 走势图.  网址: "http://data.eastmoney.com/zjlx/zs000001.html"
        self.url = "http://ff.eastmoney.com/EM_CapitalFlowInterface/api/js?" \
            "type=ff&check=MLBMS&cb=var%20aff_data=&js={(x)}&rtntype=3&" \
            + "id={}&acces_token={}&_={}".format(id, get_token(), get__())
        r = self.requests_get(self.url, "资金明细")
        # print (r.text)

        try:
            pattern = r'\"ya\":\[(.*?)\]'
            detail_capital = re.compile(pattern, re.S).findall(r.text)
            # print (detail_capital[0])
            pattern = r'\"(.*?,.*?,.*?,.*?)\",?'
            detail_capital = re.compile(
                pattern, re.S).findall(detail_capital[0])
            # print (detail_capital)
            # 只保存了 "ya" 下的数值. "xa"被滤除, 其格式固定, 为9:31-11:30, 13:01-15:00, 间隔为1分钟的时间, 共240个时间间隔.
            # "xa":"             09:31,                                  09:32,                                   09:33,                                  ...,11:30,13:01,...,15:00,"
            # "ya" 含义(亿元):   '主力   超大    大单    中单   小单'  , '主力    超大   大单    中单   小单'     '主力    超大    大单   中单   小单',   ...
            # "ya" 储存为 list: ['0.1205,0.8402,-0.7196,-0.5943,0.4737', '-0.3273,0.9383,-1.2656,-0.7716,1.0989', '-0.4815,1.0363,-1.5178,-0.982,1.4634', ... ]
            detail_capital[0].split(',')[4]
        except Exception as e:
            self.rd["detail_capital_{}".format(id)] = "url: {}\r\nerr: {}\r\ninfo:{}".format(
                self.url, e, detail_capital)
            print("detail_capital_{}, err:{}\r\ninfo:{}".format(
                id, e, detail_capital))
            return None

        # 单日股价明细, 走势图. 网址: "http://quote.eastmoney.com/zs000001.html"
        url = "http://pdfm.eastmoney.com/EM_UBG_PDTI_Fast/api/js?" \
              "rtntype=5&cb=jQuery18307447134581131771_1547432773503&type=r&iscr=false&" \
              + "id={}&token={}&_={}".format(id, get_token(), get__())
        r = self.requests_get(url, "股价明细")
        # print (r.text)

        try:
            pattern = r'\"data\":\[(.*?)\]\}'
            detail_price = re.compile(pattern, re.S).findall(r.text)
            # print (detail_price[0])
            pattern = r'\".*?,(.*?),.*?,.*?,.*?\",?'
            detail_price = re.compile(pattern, re.S).findall(detail_price[0])
            # print (detail_price)
            # 只保存了每分钟的股价, 其格式固定, 为9:30-11:30, 13:01-15:00, 间隔为1分钟的时间, 共241个时间间隔.
            # 储存为 list: ['2553.33', '2553.29', '2555.65', ...]
            detail_price[1]
        except Exception as e:
            self.rd["detail_price_{}".format(id)] = "url: {}\r\nerr: {}\r\ninfo:{}".format(
                self.url, e, detail_price)
            print("detail_price_{}, err:{}\r\ninfo:{}".format(id, e, detail_price))
            return None

        # 将所有信息打包成字典并返回
        day_details = {}
        # 对capital_info降维, 变为 [0.1205,0.8402,-0.7196,-0.5943,0.4737, -0.3273,0.9383,-1.2656,-0.7716,1.0989, ...]
        capital_temp = [x for l in detail_capital for x in l.split(',')]
        day_details["main"] = capital_temp[0::5]
        day_details["super"] = capital_temp[1::5]
        day_details["large"] = capital_temp[2::5]
        day_details["middle"] = capital_temp[3::5]
        day_details["small"] = capital_temp[4::5]
        day_details["value"] = detail_price[1:]       # 舍弃9:30的开盘值, 和资金流数据对齐.
        # print (detail_capital)
        # print (capital_temp)
        # print (day_details["main"])
        # print (day_details["super"])
        # print (day_details["large"])
        # print (day_details["middle"])
        # print (day_details["small"])
        # print (day_details["value"])

        # 字典格式, 包含当日股价详情和资金流详情. 键值: "value", "main", "super", "large", "middle", "small"
        # print (day_details)
        return day_details

    def get_code_info(self, cmd):
        # 单日资金流数据信息. 网址: "http://data.eastmoney.com/zjlx/zs000001.html"
        self.url = "http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?" \
            "type=CT&sty=CTBFTA&st=z&sr=&p=&ps=&cb=&js=var%20tab_data=({data:[(x)]})&" \
            + "cmd={}&token={}".format(cmd, get_token())
        r = self.requests_get(self.url, "资金数据")
        # print (r.text)

        try:
            pattern = r'\"(.*?)\"'
            info_capital = re.compile(pattern, re.S).findall(r.text)
            # print (info_capital)

            # 转换为规则化list
            list1 = info_capital[0].split(",")
            self.time_str = list1[-1]
            # print (self.time_str)
            # print (list1)
            # list1 打印格式:             3最新价     4涨跌幅   5主力净值(万) 6??       7超大流入(元)   8超大流出(元)   9超大净值(万) 10占比   11大单流入(元)  12大单流出(元)    13大单净值(万) 14占比     15中单流入(元)  16中单流出(元)    17中单净值(万) 18占比     19小单流入(元)  20小单流出(元)    21小单净值(万) 22占比  23主力占比  24时间日期
            # ['1', '000001', '上证指数', '2553.83', '0.74%', '-75811.38', '285986', '7516236800', '-7049105152', '46713.16', '0.39%', '25009520128', '-26234765568', '-122524.54', '-1.03%', '43805553408', '-44895364096', '-108981.07', '-0.91%', '43093999360', '-41246074880', '184792.45', '1.55%', '-0.63%', '2019-01-11 15:26:49']
            list1[23]
        except Exception as e:
            self.rd["info_capital_{}".format(cmd)] = "url: {}\r\nerr: {}\r\ninfo:{}".format(
                self.url, e, info_capital)
            print("info_capital_{}, err:{}\r\ninfo:{}".format(cmd, e, info_capital))
            return None

        # 单日涨跌信息. 网址: "http://data.eastmoney.com/zjlx/zs000001.html"
        self.url = "http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?" \
            "type=CT&sty=DCARQRQB&st=z&sr=&p=&ps=&cb=&js=var%20zjlx_hq%20=%20(x)&" \
            + "cmd={}&token={}&rt={}".format(cmd, get_token(), get_rt())
        r = self.requests_get(self.url, "股价数据")
        # print (r.text)

        try:
            pattern = r'\"(.*?)\"'
            info_price = re.compile(pattern, re.S).findall(r.text)
            # print (info_price)

            # 转换为规则化list
            list2 = info_price[0].split(",")
            # print (list2)
            # list2 打印格式:             3最新价     4涨跌额   5幅度%  6成交量(手)      7成交额(万)      8振幅   9昨收       10今开     11最高      12最低      -3??    -2??   -1
            # ['1', '000001', '上证指数', '2553.83', '18.73', '0.74', '14944410112', '122375663616', '0.85', '2535.10', '2539.55', '2554.79', '2533.36', '0.44', '0.87', '-']
            list2[13]
        except Exception as e:
            self.rd["info_price_{}".format(cmd)] = "url: {}\r\nerr: {}\r\ninfo:{}".format(
                self.url, e, info_price)
            print("info_price_{}, err:{}\r\ninfo:{}".format(cmd, e, info_price))
            return None

        list_info = []
        list_info.extend(list1[-1].split())
        list_info.extend(list2[0:4])
        list_info.extend(list2[10:13])
        list_info.extend(list2[6:8])
        list_info.append(list1[5])
        list_info.extend(list1[7:23])
        # print (list_info)
        # list_info 最终格式:                                   最新价      开盘价      最高       最低        成交量(手)      成交额(万)       主力净值(万)   超大流入(元)   超大流出(元)   超大净值(万)   占比      大单流入(元)    大单流出(元)      大单净值(万)   占比       中单流入(元)    中单流出(元)     中单净值(万)    占比       小单流入(元)    小单流出(元)     小单净值(万)  占比
        # ['2019-01-11", "15:26:49', '1', '000001', '上证指数', '2553.83', '2539.55', '2554.79', '2533.36', '14944410112', '122375663616', '-75811.38', '7516236800', '-7049105152', '46713.16', '0.39%', '25009520128', '-26234765568', '-122524.54', '-1.03%', '43805553408', '-44895364096', '-108981.07', '-0.91%', '43093999360', '-41246074880', '184792.45', '1.55%']
        # self.get_captial_details(cmd)
        return list_info

    def check_file(self, file, date):
        last_line = b""
        if os.path.exists(file):
            # 读取文件最后一行
            with open(file, 'rb+') as f:
                # 在文本文件中，没有使用b模式选项打开的文件，只允许从文件头开始,只能seek(offset,0)
                if os.path.getsize(file) > 1000:
                    f.seek(-1000, os.SEEK_END)      # 从文件末尾开始向前1000个字符
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
                    #日期相同, 则删除最后一行
                    if date_last == date:
                        f.seek(-len(last_line), os.SEEK_END)
                        f.truncate()
        return last_line

    def save_info(self, info, fileName, path=None):
        if info is None:
            raise Exception("===>FAILED! NO information")
        if (path is None):
            path = get_data_path()
        fileName += ".csv"
        # print(path)
        # print(info)
        df = pd.DataFrame(info).T
        # print (df)
        if (os.path.exists(path) is False):
            os.makedirs(path)

        self.check_file(path + fileName, info[0])
        df.to_csv(path + fileName, mode='a', header=False,
                  index=False, encoding='utf-8')
        print("saved {} info: {}".format(fileName, info))

        # check result
        flag_ok = 0
        listLine = str(self.check_file(path + fileName, None), encoding = "utf-8").split(",")
        if (len(listLine) == 28):
            # list_info 最终格式:                                   最新价      开盘价      最高       最低        成交量(手)      成交额(万)       主力净值(万)   超大流入(元)   超大流出(元)   超大净值(万)   占比      大单流入(元)    大单流出(元)      大单净值(万)   占比       中单流入(元)    中单流出(元)     中单净值(万)    占比       小单流入(元)    小单流出(元)     小单净值(万)  占比
            # ['2019-01-11", "15:26:49', '1', '000001', '上证指数', '2553.83', '2539.55', '2554.79', '2533.36', '14944410112', '122375663616', '-75811.38', '7516236800', '-7049105152', '46713.16', '0.39%', '25009520128', '-26234765568', '-122524.54', '-1.03%', '43805553408', '-44895364096', '-108981.07', '-0.91%', '43093999360', '-41246074880', '184792.45', '1.55%']
            if '-' not in listLine[12:]:
                flag_ok = 1
        if (flag_ok == 0):
            raise Exception("===>FAILED! ERR information: {}".format(info))

    # def save_detail(self, detail, fileName, path=None):
    #     if detail is None:
    #         print("fail to save_detail. fileName: {}".format(fileName))
    #     if self.time_str is None:
    #         raise Exception("failed! save_detail: NO time information.")
    #     else:
    #         ymd = self.time_str.split("-")
    #         ymd[2] = ymd[2].split()[0]
    #         date = self.time_str.split()[0]
    #         # print (ymd)
    #     if (path is None):
    #         path = get_cur_dir() + \
    #             "\\_data\\{}\\{}\\".format(ymd[0], ymd[1] + ymd[2])
    #     fileName += ".csv"
    #     # print(path + fileName)
    #
    #     # 如果不是收盘, 就需要对齐数据. 否则无法DataFrame转换
    #     length = len(detail["main"]) - len(detail["value"])
    #     if (length > 0):
    #         temp_list = [''] * length
    #         detail["value"].extend(temp_list)
    #
    #     df = pd.DataFrame(detail)
    #     # print (df)
    #     if (os.path.exists(path) is False):
    #         os.makedirs(path)
    #     df.to_csv(path + fileName)
    #     print("saved {} details. Date: {}".format(fileName, date))

    def get_shares_from_web(self):
        print("===> get_shares_from_web START <===")
        blocks = {
            "BK06111": "上证50_",
            "BK06121": "上证180_",
            "BK07051": "上证380",
            "BK07431": "深证100R",
            "BK05681": "深成500",
            "BK05001": "HS300_",
            "BK07011": "中证500",
            "BK08211": "MSCI中国",
            "BK08571": "MSCI大盘",
            "BK08581": "MSCI中盘",
        }
        # 获取板块内个股. 网址: "http://quote.eastmoney.com/center/boardlist.html#boards-BK06111"
        url = "http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?" \
              "cb=jQuery112407525040804622392_1557980547906&type=CT&sty=FCOIATC&js=(%7Bdata%3A%5B(x)%5D%2CrecordsFiltered%3A(tot)%7D)&" \
              "st=(ChangePercent)&sr=-1&ps=20&" \
              + "token={}&_={}".format(get_token(), get__())
        url_cmd_page = "&cmd=C.{}&p={}"
        name = {}

        for cmd, block in blocks.items():
            r_old = None
            page = 0
            while (True):
                page += 1
                r = self.requests_get(
                    url + url_cmd_page.format(cmd, page), "个股代码")
                if (r_old == r.text):
                    print("{} have pages:{}".format(block, page - 1))
                    break
                else:
                    r_old = r.text
                    # print (r.text)
                    shares = re.compile(
                        r'\"(\d+,\w+,.*?),.*?\"', re.S).findall(r.text)
                    print(shares)
                    for i in shares:
                        temp = i.split(',')
                        # 去除B股, ST股
                        if ('B' in temp[2] or 'ST' in temp[2]):
                            continue
                        else:
                            name[temp[1] + temp[0]] = temp[2]
        print(len(name), name)
        print("===> get_shares_from_web END <===")
        return name

    def get_blocks_from_web(self):
        print("===> get_blocks_from_web START <===")

        # 获取板块代码. 网址: "http://data.eastmoney.com/bkzj/hy.html"
        url = "http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?" \
              "type=CT&cmd=C._BKHY&sty=DCFFPBFM&st=(BalFlowMain)&sr=-1&p=1&ps=999&js=&" \
              "cb=callback09278314611305656&callback=callback09278314611305656&" \
              + "token={}&_={}".format(get_token(), get__())
        r = self.requests_get(url, "板块代码")
        # print (r.text)

        sectors = re.compile(r'\"(\d+,\w+,.*?),.*?\"', re.S).findall(r.text)
        # print(sectors)

        # 获取概念代码. 网址: "http://data.eastmoney.com/bkzj/gn.html"
        url = "http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?" \
              "type=CT&cmd=C._BKGN&sty=DCFFPBFM&st=(BalFlowMain)&sr=-1&p=1&ps=10000&js=&" \
              "cb=callback05370824536073362&callback=callback05370824536073362&" \
              + "token={}&_={}".format(get_token(), get__())
        r = self.requests_get(url, "概念代码")
        # print (r.text)

        concepts = re.compile(r'\"(\d+,\w+,.*?),.*?\"', re.S).findall(r.text)
        # print(concepts)

        name = {}
        for i in sectors:
            temp = i.split(',')
            name[temp[1] + temp[0]] = temp[2]
        for i in concepts:
            temp = i.split(',')
            name[temp[1] + temp[0]] = temp[2]
        print(name)
        print("===> get_blocks_from_web END <===")
        return name

    def save_shares_to_file(self, path=None):
        if (path is None):
            if (os.path.exists(get_para_path()) is False):
                os.makedirs(get_para_path())
            path = get_para_path() + "tickers_dl.csv"

        shares = self.get_shares_from_web()
        with open(path, 'w', encoding="utf-8", newline='') as csv_file:
            writer = csv.writer(csv_file)
            for key, value in shares.items():
                writer.writerow([key, value])
        print("saved shares to file: {}".format(path))

    def save_blocks_to_file(self, path=None):
        if (path is None):
            if (os.path.exists(get_para_path()) is False):
                os.makedirs(get_para_path())
            path = get_para_path() + "blocks_dl.csv"
        blocks = self.get_blocks_from_web()
        with open(path, 'w', encoding="utf-8", newline='') as csv_file:
            writer = csv.writer(csv_file)
            for key, value in blocks.items():
                writer.writerow([key, value])
        print("saved blocks to file: {}".format(path))

    def get_blocks_from_file(self, file=None):
        blocks_dict = {}
        if (file is None):
            file = get_para_path() + "blocks.csv"
        try:
            with open(file, 'r', encoding="utf-8") as csv_file:
                reader = csv.reader(csv_file)
                blocks_dict = dict(reader)
        except Exception as e:
            self.rd['blocks_csv_err'] = e
            print(e)
        return blocks_dict

    def get_shares_from_file(self, file=None):
        tickers_dict = {}
        if (file is None):
            file = get_para_path() + "tickers.csv"
        try:
            with open(file, 'r', encoding="utf-8") as csv_file:
                reader = csv.reader(csv_file)
                tickers_dict = dict(reader)
        except Exception as e:
            self.rd['tickers_csv_err'] = e
            print(e)
        return tickers_dict

        # 输入文件为通达信 EBK文件, 需要格式转换
        # codes_list = []
        # if (file is None):
        #     # 通达信导出格式为EBK, 股票代码0开头表示深圳, 1开头表示上海
        #     file = get_cur_dir() + "\\_para\\tickers.EBK"
        # try:
        #     with open(file, 'r') as f:
        #         for line in f.readlines():
        #             line = line.strip('\r\n ')
        #             if (len(line) == 7):
        #                 if line.startswith('0'):
        #                     # 东方财富用2结尾表示深圳. 将首个0去掉, 末尾加上2
        #                     line = line[1:] + '2'
        #                     codes_list.append(line)
        #                 elif line.startswith('1'):
        #                     # 东方财富用1结尾表示上海. 将1移到末尾
        #                     line = line[1:] + '1'
        #                     codes_list.append(line)
        #     print (codes_list)
        # except Exception as e:
        #     self.rd['tickers_ebk_err'] = e
        #     print (e)
        # return codes_list

    def save_shares_in_blocks(self, block, shares, path=None):
        if (path is None):
            path = get_para_path() + "blocks\\"
            if (os.path.exists(path) is False):
                os.makedirs(path)
            path = path + "{}.csv".format(block)

        valid_shares = self.get_shares_from_file()
        i = 0
        with open(path, 'w', encoding="utf-8", newline='') as csv_file:
            writer = csv.writer(csv_file)
            for key, value in shares.items():
                if (key in valid_shares):
                    i = i + 1
                    writer.writerow([key, value])
        print("saved {} shares to file: {}".format(i, path))

    def get_shares_in_blocks(self):
        print("===> get_shares_in_blocks START <===")
        blocks = self.get_blocks_from_file()
        # 获取板块内个股. 网址: "http://quote.eastmoney.com/center/boardlist.html#boards-BK06111"
        url = "http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?" \
              "cb=jQuery112407525040804622392_1557980547906&type=CT&sty=FCOIATC&js=(%7Bdata%3A%5B(x)%5D%2CrecordsFiltered%3A(tot)%7D)&" \
              "st=(ChangePercent)&sr=-1&ps=20&" \
              + "token={}&_={}".format(get_token(), get__())
        url_cmd_page = "&cmd=C.{}&p={}"

        total = len(blocks)
        idx = 0

        for cmd, block in blocks.items():
            idx += 1
            print("===> {}/{}\tin get_shares_in_blocks".format(idx, total))
            name = {}
            r_old = None
            page = 0
            while (True):
                page += 1
                r = self.requests_get(
                    url + url_cmd_page.format(cmd, page), "个股代码")
                if (r_old == r.text):
                    print("{} {} have pages:{}, shares:{}".format(cmd, block, page - 1, len(name)))
                    # print(name)
                    self.save_shares_in_blocks(cmd, name)
                    break
                else:
                    r_old = r.text
                    # print (r.text)
                    shares = re.compile(
                        r'\"(\d+,\w+,.*?),.*?\"', re.S).findall(r.text)
                    print(shares)
                    for i in shares:
                        temp = i.split(',')
                        # 去除B股, ST股
                        if ('B' in temp[2] or 'ST' in temp[2]):
                            continue
                        else:
                            name[temp[1] + temp[0]] = temp[2]
        print("===> get_shares_in_blocks END <===")

    def get_all_indexs(self):
        # 指数信息
        name = {
            "0000011": "上证指数",
            "3990012": "深圳指数",
            "3990052": "中小板",
            "3990062": "创业板"
        }

        print("===> get_all_indexs START <===")
        for code in name:
            try:
                l = self.get_code_info(code)
                # print(l)
                self.save_info(l, code)
                # d = self.get_day_detail(code)
                # # print(d)
                # self.save_detail(d, code)
            except Exception as e:
                self.rd[code] = e
                print("code:{}, err:{}".format(code, e))
        self.rd['_____get_all_indexs'] = self.time_str
        print("===> get_all_indexs END <===")

    def get_all_blocks(self, blocks=None):
        # blocks = ['BK04561', 'BK04771'] # 列表格式
        if blocks is None:
            blocks = self.get_blocks_from_file()
            if (len(blocks) == 0):
                self.rd['no_blocks'] = "NO blocks found"
                print("===> get_all_blocks NO blocks found! <===")
                return

        # 板块信息
        print("===> get_all_blocks START <===")
        total = len(blocks)
        idx = 0

        for code in blocks:
            try:
                idx += 1
                print("===> {}/{}\tin get_all_blocks".format(idx, total))
                l = self.get_code_info(code)
                # print(l)
                self.save_info(l, code)
                # d = self.get_day_detail(code)
                # # print(d)
                # self.save_detail(d, code)
            except Exception as e:
                self.rd[code] = e
                print("code:{}, err:{}".format(code, e))
        self.rd['_____get_all_blocks'] = self.time_str
        print("===> get_all_blocks END <===")

    def get_all_shares(self, tickers=None):
        # tickers = ['6012161', '3000012', ] # 列表格式, 前6为为代码, 最后一位1表示上海, 2表示深圳
        if tickers is None:
            tickers = self.get_shares_from_file()
            if (len(tickers) == 0):
                self.rd['no_tickers'] = "NO tickers found"
                print("===> get_all_shares NO tickers found! <===")
                return

        print("===> get_all_shares START <===")
        total = len(tickers)
        idx = 0

        for code in tickers:
            try:
                idx += 1
                print("===> {}/{}\tin get_all_shares".format(idx, total))
                l = self.get_code_info(code)
                # print(l)
                self.save_info(l, code)
                # d = self.get_day_detail(code)
                # # print(d)
                # self.save_detail(d, code)
            except Exception as e:
                self.rd[code] = e
                print("code:{}, err:{}".format(code, e))
        self.rd['_____get_all_shares'] = self.time_str
        print("===> get_all_shares END <===")

    def update_check(self):
        print("===> update_check, START! <===")
        result = False
        now = datetime.datetime.fromtimestamp(int(time.time()), pytz.timezone('Asia/Shanghai')).strftime(
            '%a %Y-%m-%d %H:%M:%S')
        self.rd['run_start'] = now
        print("当前北京时间:{}".format(now))
        week = now.split()[0]
        hour = now.split()[2].split(':')[0]
        if (week == 'Sat' or week == 'Sun' or hour < '07' or hour >= '16'):
            t = self.get_code_info("0000011")
            print("股票更新日期:    {} {}".format(t[0], t[1]))
            self.rd['data_start'] = self.time_str
            hour = t[1].split(':')[0]
            min = t[1].split(':')[1]
            if (hour == '15' and min > '05'):
                try:
                    d = {}
                    with open(get_report_file(), 'r') as f:
                        lines = f.readlines()
                        for line in lines:
                            if "data_end" in line:
                                kv = line.replace('\t', '').strip().split(',')
                                d[kv[0]] = kv[1]
                    # print (d)
                    if d['data_end'][:13] == self.time_str[:13]:
                        print("===> 已是最新数据, 无需更新! <===")
                        print("===> update_check, DENY! <===")
                        return result
                except Exception as e:
                    print("Read report file failed. {}".format(e))

                result = True
                print("===> update_check, PASS! <===")
        if (result is False):
            print("股票数据变动中, 为数据完整, 请在收盘后更新数据!")
            print("===> update_check, DENY! <===")
        return result

    def update_finished(self):
        print("===> update_finished, START! <===")
        # 最后的数据更新时间
        self.rd['data_end'] = self.time_str
        now = datetime.datetime.fromtimestamp(int(time.time()), pytz.timezone('Asia/Shanghai')).strftime(
            '%a %Y-%m-%d %H:%M:%S')
        # 程序运行结束时间
        self.rd['run_end'] = now
        try:
            if (os.path.exists(get_para_path()) is False):
                os.makedirs(get_para_path())

            with open(get_report_file(), 'w') as f:
                for key, val in self.rd.items():
                    f.write("{},\t{}\r".format(key, val))
        except Exception as e:
            print("写入报告文件失败: {}".format(e))
        finally:
            print("已完成! 更新数据成功.")
            print("===> update_finished, END! <===")


def collect_data_test(cd):
    if (cd.update_check()):
        # cd.get_all_indexs()
        # cd.get_all_blocks()
        # cd.get_all_shares()
        cd.update_finished()
    # blocks = ['BK04561', 'BK04771']
    # cd.get_all_blocks(blocks)
    # tickers = ['0003332','6000171']
    # cd.get_all_shares(tickers)


if __name__ == '__main__':
    me = singleton.SingleInstance()
    cd = collect_data()

    if len(sys.argv) == 2:
        print ("\r\n===> 强烈建议收盘后下载数据. 否则可能导致数据缺失! <===\r\n")
        if sys.argv[1] == "shares_dl_csv":
            cd.save_shares_to_file()
        elif sys.argv[1] == "blocks_dl_csv":
            cd.save_blocks_to_file()
        elif sys.argv[1] == "blocks_folder":
            cd.get_shares_in_blocks()
    elif len(sys.argv) == 3:
        try:
            print("\r\n===> 强烈建议收盘后下载数据. 否则可能导致数据缺失! <===\r\n")
            blocks = literal_eval(sys.argv[1])
            tickers = literal_eval(sys.argv[2])
            print("blocks:{}\r\ntickers:{}\r\n".format(blocks, tickers))
            if (len(blocks)):
                cd.get_all_blocks(blocks)
            if (len(tickers)):
                cd.get_all_shares(tickers)
            print("===> 手动修复完成! <===\r\n")
        except Exception as e:
            print (e)
    else:
        # test purpose
        collect_data_test(cd)
