#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import datetime
import time
import pytz
import json
import codecs
import os
import fileinput
import numpy as np
import pandas as pd
from myutil import *
from tendo import singleton
from ast import literal_eval

class collect_data(object):
    def __init__(self):
        self.time_str = None
        self.rd = {}
        self.tz = pytz.timezone('Asia/Shanghai')
        self.check_s = ['f3020', 'f3045', 'f3009', 'f3023', 'f3049', 'f3129', 'f3037', 'f3135', 'f1020', 'f20', 'f1045', 'f45', 'f9', 'f23', 'f37']
        self.check_b = ['f2009', 'f2023', 'f2037', 'f134', 'f2020', 'f2045', ]

    """
    def get_day_detail(self, id):
        # 资金流明细, 走势图. 网址: "http://data.eastmoney.com/zjlx/zs000001.html"
        # 分时资金流: http://ff.eastmoney.com/EM_CapitalFlowInterface/api/js?id=0000011&type=ff&check=MLBMS&cb=var%20aff_data=&js={(x)}&rtntype=3&acces_token=1942f5da9b46b069953c873404aad4b5&_=1558414459473
        # js代码文件: http://data.eastmoney.com/js_001/fn_zjlx.js?201806021830
        # 相关内容:   http://ff.eastmoney.com/EM_CapitalFlowInterface/api/js?id=" + code + "&type=ff&check=MLBMS&cb=var%20aff_data=&js={(x)}&rtntype=3&acces_token=1942f5da9b46b069953c873404aad4b5
        url = "http://ff.eastmoney.com/EM_CapitalFlowInterface/api/js?id={}".format(id) \
            + "&type=ff&check=MLBMS&cb=var%20aff_data=&js={(x)}&rtntype=3&acces_token=1942f5da9b46b069953c873404aad4b5" \
            + "&_={}".format(get__())
        r = self.requests_get(url, "资金明细")
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
            self.rd["detail_capital_{}".format(id)] = "url: {}\r\n\terr: {}\r\n\tinfo:{}".format(
                url, e, detail_capital)
            print("detail_capital_{}, err:{}\r\n\tinfo:{}".format(
                id, e, detail_capital))
            return None

        # 股价明细, 走势图.网址: "http://quote.eastmoney.com/zs000001.html"
        # 分时股价:   http://pdfm.eastmoney.com/EM_UBG_PDTI_Fast/api/js?rtntype=5&token=4f1862fc3b5e77c150a2b985b12db0fd&cb=jQuery183012573462323834872_1558414725983&id=0000011&type=r&iscr=false&_=1558414728436
        # js代码文件: http://hqres.eastmoney.com/EM15AGIndex/js/emchart.min.js
        # 相关内容:        //pdfm.eastmoney.com/EM_UBG_PDTI_Fast/api/js?rtntype=5&token=4f1862fc3b5e77c150a2b985b12db0fd ,可知缺少参数 cb type iscr
        url = "http://pdfm.eastmoney.com/EM_UBG_PDTI_Fast/api/js?rtntype=5&token=4f1862fc3b5e77c150a2b985b12db0fd" \
            + "&cb={}&id={}&type=r&iscr=false&_={}".format(get_cb(), id, get__())
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
            self.rd["detail_price_{}".format(id)] = "url: {}\r\n\terr: {}\r\n\tinfo:{}".format(
                url, e, detail_price)
            print("detail_price_{}, err:{}\r\n\tinfo:{}".format(id, e, detail_price))
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
        day_details["value"] = detail_price[1:]  # 舍弃9:30的开盘值, 和资金流数据对齐.
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

    def save_detail(self, detail, fileName, path=None):
        if detail is None:
            print("fail to save_detail. fileName: {}".format(fileName))
        if self.time_str is None:
            raise Exception("failed! save_detail: NO time information.")
        else:
            ymd = self.time_str.split("-")
            ymd[2] = ymd[2].split()[0]
            date = self.time_str.split()[0]
            # print (ymd)
        if (path is None):
            path = get_cur_dir() + \
                "\\_data\\{}\\{}\\".format(ymd[0], ymd[1] + ymd[2])
        fileName += ".csv"
        # print(path + fileName)

        # 如果不是收盘, 就需要对齐数据. 否则无法DataFrame转换
        length = len(detail["main"]) - len(detail["value"])
        if (length > 0):
            temp_list = [''] * length
            detail["value"].extend(temp_list)

        df = pd.DataFrame(detail)
        # print (df)
        if (os.path.exists(path) is False):
            os.makedirs(path)
        df.to_csv(path + fileName)
        print("saved {} details. Date: {}".format(fileName, date))

    def get_detail_example:
        d = self.get_day_detail(code)
        # print(d)
        self.save_detail(d, code)
    """

    def requests_get(self, url, comment=""):
        for i in range(3):
            try:
                print("{} {}".format(comment, url))
                r = requests.get(url, timeout=20)
                # print (r.text)
                break
            except Exception as e:
                t = time.strftime("%H%M%S", time.localtime())
                self.rd["url_err_{}".format(t)] = url
                # 10s后重试连接
                print("10s后重试. 错误:{}".format(e))
                time.sleep(10)
                r = None
        if r is None:
            raise Exception("requests_get FAILED: {}".format(url))
        return r

    def get_code_info(self, cmd):
        # 单日资金流. 网址: "http://data.eastmoney.com/zjlx/601006.html"
        # 单日资金流: http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&cmd=0000011&sty=CTBFTA&st=z&sr=&p=&ps=&cb=&js=var%20tab_data=({data:[(x)]})&token=70f12f2f4f091e459a279469fe49eca5
        # js代码文件: http://data.eastmoney.com/js_001/zjlx/fn_zjlxStock.js?t=_201801301611
        #            http://data.eastmoney.com/js_001/fn_zjlx_index.js?201806021830
        #            这一块比较混乱, 猜测是把 Stock Block Index 都分开处理了. 还好最终的地址是通用的.
        # 相关内容:   http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&cmd=' + _stockCode + _stockMarke + '&sty=CTBFTA&st=z&sr=&p=&ps=&cb=&js=var tab_data=({data:[(x)]})&token=70f12f2f4f091e459a279469fe49eca5
        #             http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&cmd=' + _code +                    '&sty=CTBFTA&st=z&sr=&p=&ps=&cb=&js=var tab_data=({data:[(x)]})&token=70f12f2f4f091e459a279469fe49eca5
        url = "http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT" \
            + "&sty=CTBFTA&st=z&sr=&p=&ps=&cb=&js=var%20tab_data=({data:[(x)]})&token=70f12f2f4f091e459a279469fe49eca5" \
            + "&cmd={}".format(cmd)
        r = self.requests_get(url, "资金数据")
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
            raise Exception("get_code_info capital ERROR\r\n\turl:{}\r\n\tinfo_capital:{}\r\n\terr:{}".format(url, info_capital, e))
            return None

        # 单日股价. 网址: "http://data.eastmoney.com/zjlx/601006.html"
        # 单日股价:   http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&sty=DCARQRQB&st=z&sr=&p=&ps=&cb=&js=var%20zjlx_hq%20=%20(x)&token=1942f5da9b46b069953c873404aad4b5&cmd=0000011&rt=51947244
        # js代码文件: http://data.eastmoney.com/js_001/zjlx/fn_zjlxStock.js?t=_201801301611
        #            http://data.eastmoney.com/js_001/fn_zjlx_index.js?201806021830
        #            这一块比较混乱, 猜测是把 Stock Block Index 都分开处理了. 还好最终的地址是通用的.
        # 相关内容:   http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&sty=DCARQRQB&st=z&sr=&p=&ps=&cb=&js=var zjlx_hq = (x)&token=1942f5da9b46b069953c873404aad4b5&cmd="
        url = "http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&sty=DCARQRQB&st=z&sr=&p=&ps=&cb=&js=var%20zjlx_hq%20=%20(x)&token=1942f5da9b46b069953c873404aad4b5" \
            + "&cmd={}&rt={}".format(cmd, get__())
        r = self.requests_get(url, "股价数据")
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
            raise Exception("get_code_info price ERROR\r\n\turl:{}\r\n\tinfo_price:{}\r\n\terr:{}".format(url, info_price, e))
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

    def get_code_fund(self, code):
        # 基本面信息. 网址: "http://quote.eastmoney.com/sh601006.html"
        # 基本面信息: http://push2.eastmoney.com/api/qt/slist/get?spt=1&np=3&fltt=2&invt=2&fields=f9,f12,f13,f14,f20,f23,f37,f45,f49,f134,f135,f129,f1000,f2000,f3000&ut=bd1d9ddb04089700cf9c27f6f7426281&cb=jQuery183046200764579979126_1558420775801&secid=1.601006&_=1558420777320
        #            http://push2.eastmoney.com/api/qt/slist/get?spt=1&np=3&fltt=2&invt=2&fields=f9,f12,f13,f14,f20,f23,f37,f45,f49,f134,f135,f129,f1000,f2000,f3000&ut=bd1d9ddb04089700cf9c27f6f7426281&cb=jQuery183002584313374160585_1558488528956&secid=0.000002&_=1558488529739
        # Chrome调试: Network->Filter 分别搜索 "quote-min.js" 和 "get?spt", 可以提取如下链接.
        # js代码文件: http://hqres.eastmoney.com/emag14/js/0509/quote-min.js?v=20190425
        # 相关内容:   http://push2.eastmoney.com/api/qt/slist/get?spt=1&np=3&fltt=2&invt=2&fields=f9,f12,f13,f14,f20,f23,f37,f45,f49,f134,f135,f129,f1000,f2000,f3000&ut=bd1d9ddb04089700cf9c27f6f7426281
        """
        jQuery18307755203476525021_1558398132890({
            "rc": 0,
            "rt": 18,
            "svr": 181403912,
            "lt": 2,
            "full": 1,
            "data": {
                "total": 2,
                "diff": [{
                    "f9": 7.59,             // 市盈率
                    "f12": "601006",        // 代码
                    "f13": 1,               // 所在版块, 0表示深圳, 1表示上海
                    "f14": "大秦铁路",      // 名称
                    "f20": 121610354396,    // 总市值
                    "f23": 1.1,             // 市净率
                    "f37": 3.69,            // ROE %
                    "f45": 4005657757.0,    // 净利润
                    "f49": 26.2073,         // 毛利率
                    "f129": 20.29,          // 净利率
                    "f134": "-",
                    "f135": 118771503514.0, // 净资产
                    "f1020": 2,             // 总市值排名
                    "f1113": 8,
                    "f1045": 1,             // 净利润排名
                    "f1009": 2,             // 市盈率排名
                    "f1023": 48,            // 市净率排名
                    "f1049": 12,            // 毛利率排名
                    "f1129": 6,             // 净利率排名
                    "f1037": 10,            // ROE排名
                    "f1135": 1,             // 净资产排名
                    ...
                    "f3020": 1,                 // 总市值分数: 1-高
                    "f3113": 1,
                    "f3045": 1,                 // 净利润分数: 3-较低
                    "f3009": 1,                 // 市盈率分数: 3-较低
                    "f3023": 4,                 // 市净率分数: 4-低 (高不好!)
                    "f3049": 1,                 // 毛利率分数: 1-高
                    "f3129": 1,                 // 净利率分数: 3-较低
                    "f3037": 1,                 // ROE分数: 3-较低
                    "f3135": 1,                 // 净资产分数: 2-较高
                    ...
                }, {
                    "f9": 16.61,
                    "f12": "BK0422",
                    "f13": 90,
                    "f14": "交运物流",
                    "f20": 728481824000,            // 流通市值
                    "f134": 57,                     // 板块个股数量
                    ...
                    "f2020": 12654500302.84,        // 总市值
                    "f2113": 4.52,
                    "f2045": 179833436.99,          // 净利润
                    "f2009": 46.99,                 // 市盈率
                    "f2023": 2.45,                  // 市净率
                    "f2049": 18.75,                 // 毛利率
                    "f2129": 4.18,                  // 净利率
                    "f2037": 1.77,                  // ROE
                    "f2135": 7805660590.25,         // 净资产
                    "f2115": 38.84,
                    ...
                }]
            }
        });
        """
        url = "http://push2.eastmoney.com/api/qt/slist/get?spt=1&np=3&fltt=2&invt=2&fields=f9,f12,f13,f14,f20,f23,f37,f45,f49,f134,f135,f129,f1000,f2000,f3000&ut=bd1d9ddb04089700cf9c27f6f7426281" \
            + "&cb={}&secid={}.{}&_={}".format(get_cb(), '1' if code[-1]=='1' else '0', code[:-1], get__())
        r = self.requests_get(url, "基本信息")
        # print (r.text)
        try:
            text = r.text[r.text.find("(")+1:-2]
            # print (text)
            data = json.loads(text)['data']['diff']
            # print (data)
            s=data[0]
            b=data[1]
            list_share = []
            list_block = []

            # 检查数据合法性
            for i in self.check_s:
                try:
                    float(s[i])
                except ValueError:
                    s[i] = 0
            for i in self.check_b:
                try:
                    float(b[i])
                except ValueError:
                    b[i] = 0
            if s['f9']<0 or s['f9']>999.9:
                s['f9'] = 999.9
            if s['f23']<0 or s['f23']>99.9:
                s['f23'] = 99.9
            if s['f37']<0:
                s['f37'] = 0

            # 提取个股基本面数据
            s['code'] = str(s['f12']) + ('1' if s['f13'] == '1' else '2')
            # 基本面综合评分, 满分100
            s['score'] = "{:2d}".format(99-3 * (s['f3020'] + s['f3045'] + s['f3009'] + (5-s['f3023']) + s['f3049'] + s['f3129'] + s['f3037'] + s['f3135']-8))
            # 基本面排名和详情
            s['value'] = "{:3d} / {}".format(s['f1020'],readableNum(s['f20'],divisor=10000)) # 排名/总市值
            s['profit'] = "{:3d} / {}".format(s['f1045'],readableNum(s['f45'],divisor=10000)) # 排名/净利润
            s['PE'] = "{:5.1f} / {:.1f}".format(s['f9'],b['f2009']) # 市盈率/版块市盈率/
            s['PB'] = "{:4.1f} / {:.1f}".format(s['f23'],b['f2023']) # 市净率/版块市净率
            s['ROE'] = "{:4.1f} / {:.1f}".format(s['f37'],b['f2037']) # ROE/版块ROE%
            s['blk'] = "{:3d} / {} ".format(b['f134'],b['f14']) # 个股数量/所属板块
            # print (s)
            #       含义: 代码, 名称 , 保留给资金流分析,         评分,   总市值,    净利润, 市盈率,市净率, ROE, 所属版块
            # list_key = ['code','f14', 'res1', 'res2', 'res3', 'score', 'value', 'profit', 'PE', 'PB', 'ROE', 'blk']
            list_key = ['code', 'score', 'value', 'profit', 'PE', 'PB', 'ROE', 'blk']
            for k in list_key:
                list_share.append(s.get(k,'-'))
            # print (list_share)

            # 提取版块基本面数据
            b['code'] = b['f12'] + '1'
            # 基本面排名和详情
            # b['market'] = readableNum(b['f20'],divisor=10000,sort=True)    # 流通市值
            b['value'] = readableNum(b['f2020'],divisor=10000,sort=True)    # 平均市值
            b['profit'] = readableNum(b['f2045'],divisor=10000,sort=True)  # 平均净利润
            b['PE'] = "{:6.1f}".format(b['f2009']) # 市盈率
            b['PB'] = "{:5.1f}".format(b['f2023']) # 市净率
            b['ROE'] = "{:4.1f}".format(b['f2037']) # ROE%
            b['num'] = "{:3d}".format(b['f134']) # 版块个数数量
            #       含义: 代码, 名称 , 保留给资金流分析,       排序, 平均市值,平均净利润, 市盈率,市净率, ROE, 个股数量
            # list_key = ['code','f14', 'res1', 'res2', 'res3', 'res4', 'value', 'profit', 'PE', 'PB', 'ROE', 'num']
            list_key = ['code', 'value', 'profit', 'PE', 'PB', 'ROE', 'num']
            for k in list_key:
                list_block.append(b.get(k,'-'))
            # print (list_block)
            return (list_share, list_block)
        except Exception as e:
            raise Exception("get_code_fund err\r\n\turl:{}\r\n\tdata:{}\r\n\terr:{}".format(url, data, e))
            return None

    def get_blocks_from_web(self):
        print("===> get_blocks_from_web START <===")

        # 获取板块代码. 网址: "http://data.eastmoney.com/bkzj/hy.html"
        # 板块列表:   http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&cmd=C._BKHY&sty=DCFFPBFM&st=(BalFlowMain)&sr=-1&p=1&ps=999&js=&token=894050c76af8597a853f5b408b759f5d&cb=callback05954677021554038&callback=callback05954677021554038&_=1558418601523
        # js代码文件: http://data.eastmoney.com/js_001/chart.js
        # 相关内容:   http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&cmd=C._BKHY&sty=DCFFPBFM&st=(BalFlowMain)&sr=1&p=1&ps=&ps=&js=&token=894050c76af8597a853f5b408b759f5d
        #            参数 cb 和 callback 的值会回显在结果上, 可以自定义或为空
        url = "http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&cmd=C._BKHY" \
            + "&sty=DCFFPBFM&st=(BalFlowMain)&sr=-1&p=1&ps=999&js=&token=894050c76af8597a853f5b408b759f5d" \
            + "&cb={}&callback={}&_={}".format(get_cb(), get_cb(), get__())
        r = self.requests_get(url, "板块代码")
        # print (r.text)

        sectors = re.compile(r'\"(\d+,\w+,.*?),.*?\"', re.S).findall(r.text)
        # print(sectors)

        # 获取板块代码. 网址: "http://data.eastmoney.com/bkzj/gn.html"
        # 板块列表:   http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&cmd=C._BKGN&sty=DCFFPBFM&st=(BalFlowMain)&sr=-1&p=1&ps=10000&js=&token=894050c76af8597a853f5b408b759f5d&cb=callback04384373587445334&callback=callback04384373587445334&_=1558419287487
        # js代码文件: http://data.eastmoney.com/js_001/chart.js
        # 相关内容:   找不到...
        url = "http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&cmd=C._BKGN" \
            + "&sty=DCFFPBFM&st=(BalFlowMain)&sr=-1&p=1&ps=10000&js=&token=894050c76af8597a853f5b408b759f5d&cb=&callback=" \
            + "&_={}".format(get__())
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
        # 板块列表:   http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?cb=jQuery112403575218980903154_1558419737279&type=CT&token=4f1862fc3b5e77c150a2b985b12db0fd&sty=FCOIATC&js=(%7Bdata%3A%5B(x)%5D%2CrecordsFiltered%3A(tot)%7D)&cmd=C.BK06111&st=(ChangePercent)&sr=-1&p=1&ps=20&_=1558419737296
        # js代码文件: http://hqres.eastmoney.com/EMQuote_Center3.0/js/boardlist.min.js?v=190429171011214
        # 相关内容:        //nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&token=4f1862fc3b5e77c150a2b985b12db0fd&js=({data:[(x)],recordsTotal:(tot),recordsFiltered:(tot)})"
        url = "http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?cb={}".format(get_cb()) \
            + "&type=CT&token=4f1862fc3b5e77c150a2b985b12db0fd&sty=FCOIATC&js=(%7Bdata%3A%5B(x)%5D%2CrecordsFiltered%3A(tot)%7D)" \
            + "&st=(ChangePercent)&sr=-1&ps=20&_={}".format(get__())
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

    def get_shares_in_blocks(self):
        print("===> get_shares_in_blocks START <===")
        blocks = self.get_blocks_from_file()
        # 获取板块内个股. 网址: "http://quote.eastmoney.com/center/boardlist.html#boards-BK06111"
        # 板块列表:   http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?cb=jQuery112403575218980903154_1558419737279&type=CT&token=4f1862fc3b5e77c150a2b985b12db0fd&sty=FCOIATC&js=(%7Bdata%3A%5B(x)%5D%2CrecordsFiltered%3A(tot)%7D)&cmd=C.BK06111&st=(ChangePercent)&sr=-1&p=1&ps=20&_=1558419737296
        # js代码文件: http://hqres.eastmoney.com/EMQuote_Center3.0/js/boardlist.min.js?v=190429171011214
        # 相关内容:        //nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&token=4f1862fc3b5e77c150a2b985b12db0fd&js=({data:[(x)],recordsTotal:(tot),recordsFiltered:(tot)})"
        url = "http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?cb={}".format(get_cb()) \
            + "&type=CT&token=4f1862fc3b5e77c150a2b985b12db0fd&sty=FCOIATC&js=(%7Bdata%3A%5B(x)%5D%2CrecordsFiltered%3A(tot)%7D)" \
            + "&st=(ChangePercent)&sr=-1&ps=20&_={}".format(get__())
        url_cmd_page = "&cmd=C.{}&p={}"

        total = len(blocks)
        for i, cmd in enumerate(blocks,1):
            print("===> {}/{}\tget_shares_in_blocks({})".format(i, total, cmd))
            if not cmd.startswith("BK"):
                continue
            name = {}
            r_old = None
            page = 0
            while (True):
                page += 1
                r = self.requests_get(
                    url + url_cmd_page.format(cmd, page), "个股代码")
                if (r_old == r.text):
                    print("{} have {} pages, {} shares.".format(cmd, page - 1, len(name)))
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

    def save_info(self, info, fileName, path=None):
        try:
            if (path is None):
                path = get_data_path()
            fileName += ".csv"
            # print(path)
            # print(info)
            df = pd.DataFrame(info).T
            # print (df)
            if (os.path.exists(path) is False):
                os.makedirs(path)

            read_last_line(path + fileName, info[0])
            df.to_csv(path + fileName, mode='a', header=False,
                      index=False, encoding='utf-8')
            print("saved {} info: {}".format(fileName, info))

            # check result
            flag_ok = False
            lastLine = str(read_last_line(path + fileName, None), encoding="utf-8").split(",")
            if (len(lastLine) == 28):
                # list_info 最终格式:                                   最新价      开盘价      最高       最低        成交量(手)      成交额(万)       主力净值(万)   超大流入(元)   超大流出(元)   超大净值(万)   占比      大单流入(元)    大单流出(元)      大单净值(万)   占比       中单流入(元)    中单流出(元)     中单净值(万)    占比       小单流入(元)    小单流出(元)     小单净值(万)  占比
                # ['2019-01-11", "15:26:49', '1', '000001', '上证指数', '2553.83', '2539.55', '2554.79', '2533.36', '14944410112', '122375663616', '-75811.38', '7516236800', '-7049105152', '46713.16', '0.39%', '25009520128', '-26234765568', '-122524.54', '-1.03%', '43805553408', '-44895364096', '-108981.07', '-0.91%', '43093999360', '-41246074880', '184792.45', '1.55%']
                if '-' not in lastLine[12:]:
                    flag_ok = True
            if (flag_ok is False):
                raise Exception("save_info ERROR: \r\n\tlastLine:{}\r\n\tfile:{}\r\n\terr:{}".format(lastLine, fileName, "flag_ok is False"))
        except Exception as e:
            raise Exception("save_info ERROR: \r\n\tinfo:{}\r\n\tfile:{}\r\n\terr:{}".format(info, fileName, e))

    def save_fund(self, fund, file, res):
        try:
            print("save_fund to file: {}".format(file))
            key = fund.keys()
            with codecs.open(file, "r", encoding="utf8") as fi, \
                codecs.open(get_tmp_file(), "w", encoding="utf8") as fo:
                for line in fi:
                    lists = line.split(",")
                    if lists[0] in key:
                        fo.write(','.join(lists[:res] + fund[lists[0]][1:]) + '\r')
                    else:
                        fo.write(line)
            os.remove(file)
            os.rename(get_tmp_file(), file)
            print("save_fund finished: {}".format(file))
        except Exception as e:
            raise Exception("save_fund ERROR: \r\n\tfund:{}\r\n\tfile:{}\r\n\terr:{}".format(fund, file, e))

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
            for t in sorted(shares.items(),key=lambda item:item[0]):
                if (t[0] in valid_shares):
                    i = i + 1
                    writer.writerow(t)
        print("saved {} shares to file: {}".format(i, path))

    def save_shares_to_file(self, path=None):
        if (path is None):
            if (os.path.exists(get_para_path()) is False):
                os.makedirs(get_para_path())
            path = get_para_path() + "tickers_dl.csv"

        shares = self.get_shares_from_web()
        with open(path, 'w', encoding="utf-8", newline='') as csv_file:
            writer = csv.writer(csv_file)
            for t in sorted(shares.items(),key=lambda item:item[0]):
                writer.writerow(list(t) + ['-' for n in range(10)])
        print("===> save_shares_to_file SUCCESS: {} <===".format(path))

    def save_blocks_to_file(self, path=None):
        index = {
            "0000011":"上证指数",
            "3990012":"深圳指数",
            "3990052":"中小板",
            "3990062":"创业板",
        }
        if (path is None):
            if (os.path.exists(get_para_path()) is False):
                os.makedirs(get_para_path())
            path = get_para_path() + "blocks_dl.csv"
        blocks = self.get_blocks_from_web()
        with open(path, 'w', encoding="utf-8", newline='') as csv_file:
            writer = csv.writer(csv_file)
            for t in sorted(index.items(),key=lambda item:item[0]):
                writer.writerow(list(t) + ['-' for n in range(10)])
            for t in sorted(blocks.items(),key=lambda item:item[0]):
                writer.writerow(list(t) + ['-' for n in range(10)])
        print("===> save_blocks_to_file SUCCESS: {} <===".format(path))

    def get_blocks_from_file(self, file=None):
        blocks_code = []
        if (file is None):
            file = get_para_path() + "blocks.csv"
        try:
            with open(file, 'r', encoding="utf-8") as csv_file:
                reader = csv.reader(csv_file)
                blocks_code = [row[0] for row in reader if '-' not in row[0]]
        except Exception as e:
            self.rd['get_blocks_from_file'] = e
            print(e)
        return blocks_code

    def get_shares_from_file(self, file=None):
        tickers_code = []
        if (file is None):
            file = get_para_path() + "tickers.csv"
        try:
            with open(file, 'r', encoding="utf-8") as csv_file:
                reader = csv.reader(csv_file)
                tickers_code = [row[0] for row in reader]
        except Exception as e:
            self.rd['get_shares_from_file'] = e
            print(e)
        return tickers_code

    def get_all_infos(self, codes=None):
        # codes = ['BK04561', 'BK04771', '6012161', '3000012'] # 列表格式
        print("===> get_all_infos START <===")
        if codes is None:
            codes = []
            codes.extend(self.get_blocks_from_file())
            codes.extend(self.get_shares_from_file())
            if (len(codes) == 0):
                self.rd['get_all_infos'] = "NO codes found"
                print("===> get_all_infos END: NO codes found! <===")
                return

        for j in range(3): # retry 3 times
            retry = []
            total = len(codes)
            for i, code in enumerate(codes,1):
                try:
                    print("===> {}/{}\tget_all_infos({})_{}".format(i, total, code, j))
                    l = self.get_code_info(code)
                    # print(l)
                    self.save_info(l, code)
                except Exception as e:
                    retry.append(code)
                    self.rd["get_all_infos({})_{}".format(code, j)] = e
                    print("get_all_infos({})_{}:\t{}".format(code, j, e))
            codes = retry

        self.rd["get_all_infos_missed"] = codes
        print("get_all_infos_missed: {}".format(codes))

        # /////////////////////// 计算股价, 资金流, 波动系数
        self.rd["===> get_all_infos"] = self.time_str
        print("===> get_all_infos END <===")

    def get_all_funds(self, tickers=None):
        # tickers = ['6012161', '3000012', ] # 列表格式, 前6为为代码, 最后一位1表示上海, 2表示深圳
        print("===> get_all_funds START <===")
        if tickers is None:
            tickers = self.get_shares_from_file()
            if (len(tickers) == 0):
                self.rd['get_all_funds'] = "NO tickers found"
                print("===> get_all_funds END: NO tickers found! <===")
                return

        self.fund_ticker = {}
        self.fund_block = {}
        for j in range(3): # retry 3 times
            retry = []
            total = len(tickers)
            for i, ticker in enumerate(tickers,1):
                try:
                    print("===> {}/{}\tget_all_funds({})_{}".format(i, total, ticker, j))
                    l = self.get_code_fund(ticker)
                    # print(l)
                    self.fund_ticker[ticker] = l[0]
                    self.fund_block[l[1][0]] = l[1]
                except Exception as e:
                    retry.append(ticker)
                    self.rd["get_all_funds({})_{}".format(ticker, j)] = e
                    print("get_all_funds({})_{}:\t{}".format(ticker, j, e))
            tickers = retry

        try:
            # print (self.fund_ticker)
            # print (self.fund_block)
            if (len(self.fund_ticker)):
                self.save_fund(self.fund_ticker, get_para_path()+"tickers.csv", 4)
            if (len(self.fund_block)):
                self.save_fund(self.fund_block, get_para_path()+"blocks.csv", 5)
        except Exception as e:
            self.rd["get_all_funds_save"] = e
            print("get_all_funds_save:\t{}".format(e))

        self.rd["get_all_funds_missed"] = tickers
        print("get_all_funds_missed: {}".format(tickers))
        self.rd["===> get_all_funds"] = self.time_str
        print("===> get_all_funds END <===")

    def update_check(self):
        print("===> update_check START <===")
        now = datetime.datetime.now(self.tz)
        week = now.strftime('%a')
        self.rd['run_start'] = now
        print("当前时间:{}".format(now))
        if (week == 'Sat' or week == 'Sun' or now.hour < 7 or now.hour >= 16):
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
                        print("已是最新数据, 无需更新!")
                        print("===> update_check, UPDATED! <===")
                        return "UPDATED"
                except Exception as e:
                    print("Read report file failed. {}".format(e))
            print("===> update_check PASS <===")
            return "PASS"
        print("股票数据变动中, 为数据完整, 请在收盘后更新数据!")
        print("===> update_check DENY <===")
        return "DENY"

    def update_finished(self):
        print("===> update_finished, START! <===")
        # 最后的数据更新时间
        self.rd['data_end'] = self.time_str
        # 程序运行结束时间
        now = datetime.datetime.now(self.tz)
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

    def get_missed_codes(self):
        codes_dict = {"missed_info":self.rd.get("get_all_infos_missed",[]), "missed_fund":self.rd.get("get_all_funds_missed",[])}
        return codes_dict

def collect_data_test(cd):
    # cd.get_all_infos()
    # cd.get_all_infos(cd.get_blocks_from_file())
    # codes = ['BK04561', 'BK04771', '0003332','6000171']
    # cd.get_all_infos(codes)
    # codes = ['0003332','6000171']
    # cd.get_all_funds(codes)
    pass


if __name__ == '__main__':
    me = singleton.SingleInstance()
    cd = collect_data()

    if len(sys.argv) == 2:
        print("\r\n===> 强烈建议收盘后下载数据. 否则可能导致数据缺失! <===\r\n")
        if sys.argv[1] == "get_all_funds":
            cd.get_all_funds()
        elif sys.argv[1] == "shares_dl_csv":
            cd.save_shares_to_file()
        elif sys.argv[1] == "blocks_dl_csv":
            cd.save_blocks_to_file()
        elif sys.argv[1] == "blocks_folder":
            cd.get_shares_in_blocks()
    elif len(sys.argv) == 3:
        try:
            infos = literal_eval(sys.argv[1])
            funds = literal_eval(sys.argv[2])
            print("\r\n===> 尝试修复 <===\r\n")
            print("infos:{}".format(infos))
            print("funds:{}".format(funds))
            if cd.update_check() != "DENY":
                print("get_all_infos:{}\r\nget_all_funds:{}\r\n".format(infos, funds))
                if (len(infos)):
                    cd.get_all_infos(infos)
                if (len(funds)):
                    cd.get_all_funds(funds)
            print("===> 修复完成! <===\r\n")
        except Exception as e:
            print(e)
    else:
        # test purpose
        collect_data_test(cd)
