import numpy as np
import pandas as pd
from lxml import etree
from io import StringIO
from myutil import *
from tendo import singleton
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineView

class Render(QWebEngineView):               # 子类Render继承父类QWebEngineView
    def __init__(self, url):
        self.html = ''
        self.app = QApplication(sys.argv)
        QWebEngineView.__init__(self)       # 子类构造函数继承父类，这种写法python2和3通用，还可以是super().__init__()
        self.loadFinished.connect(self._loadFinished)
        self.load(QUrl(url))
        self.app.exec_()

    def _loadFinished(self):
        self.page().toHtml(self.callable)

    def callable(self, data):
        self.html = data
        self.app.quit()


class get_fundamentals(object):
    def get_fund(self, code):
        fund_share = {}
        if code[-1] == '1':
            code = "sh" + code[:-1]
        elif code[-1] == '2':
            code = "sz" + code[:-1]
        else:
            return fund_share
        url = "http://quote.eastmoney.com/{}.html".format(code)
        print (url)

        """
        获取个股基本面信息: "http://quote.eastmoney.com/sh601006.html"
        <div class="cwzb">
            <table cellpadding="0" cellspacing="0">
                <thead>
                    <tr>
                        <th>&nbsp;</th>
                        <th>总市值</th>
                        <th>净资产</th>
                        <th>净利润</th>
                        <th>市盈率</th>
                        <th>市净率</th>
                        <th>毛利率</th>
                        <th>净利率</th>
                        <th>ROE<b title="加权净资产收益率" class="hxsjccsyl"></b></th>
                    </tr>
                </thead>
                <tbody id="cwzbDataBox">
                    <tr> <td> // 大秦铁路
                    <tr> <td> // 交运物流
                    <tr> <td> // 行业排名
                    <tr> <td> // 四分位属性
                </tbody>
            </table>
        </div>
        """
        r = Render(url)
        # print (r.html)
        tree = etree.parse(StringIO(r.html), etree.HTMLParser())    # 标准化为xml格式
        # print(etree.tostring(tree.getroot(), pretty_print=True, method="html", encoding='unicode'))
        root = tree.xpath('//div[@class="cwzb"]')[0]
        column = root.xpath('./table/thead/tr/th/text()')
        # print (column)  # 获取 ['\xa0', '总市值', '净资产', '净利润', '市盈率', '市净率', '毛利率', '净利率', 'ROE']
        key = root.xpath('./table/tbody[@id="cwzbDataBox"]/tr[1]/td/a/text()')[0]   # 查询的个股
        values = root.xpath('./table/tbody[@id="cwzbDataBox"]/tr[1]/td/text()')
        fund_share[key] = values
        key = root.xpath('./table/tbody[@id="cwzbDataBox"]/tr[2]/td/a/text()')[0]   # 所在版块
        values = root.xpath('./table/tbody[@id="cwzbDataBox"]/tr[2]/td/text()')
        fund_share[key] = values
        key = root.xpath('./table/tbody[@id="cwzbDataBox"]/tr[3]/td/b/text()')[0]   # 行业排名
        values = root.xpath('./table/tbody[@id="cwzbDataBox"]/tr[3]/td/text()')
        fund_share[key] = values
        key = root.xpath('./table/tbody[@id="cwzbDataBox"]/tr[4]/td/b/text()')[0]   # 四分位属性
        values = root.xpath('./table/tbody[@id="cwzbDataBox"]/tr[4]/td/p/text()')
        fund_share[key] = values
        print (fund_share)
        return fund_share

    def get_shares_from_file(self, file=None):
        tickers_code = []
        if (file is None):
            file = get_para_path() + "tickers.csv"
        try:
            with open(file, 'r', encoding="utf-8") as csv_file:
                reader = csv.reader(csv_file)
                tickers_code = [row[0] for row in reader]
        except Exception as e:
            print(e)
        return tickers_code

    def get_all_funds(self, tickers=None, retry=3):
        # tickers = ['6012161', '3000012', ] # 列表格式, 前6为为代码, 最后一位1表示上海, 2表示深圳
        if tickers is None:
            self.fund_block = {}
            tickers = self.get_shares_from_file()
            print("===> get_all_funds START <===")
        else:
            print("===> get_all_shares RETRY <===")

        total = len(tickers)
        idx = 0
        retry_code = []

        for code in tickers:
            try:
                idx += 1
                print("===> {}/{}\tin get_all_funds".format(idx, total))
                l = self.get_fund(code)
                # self.save_info(l, code)
                # /////////// Dataframe
            except Exception as e:
                retry.append(code)
                print("code:{}, err:{}".format(code, e))

        if (len(retry_code) and retry):
            self.get_all_funds(tickers=retry_code, retry=retry-1)
        else:
            # ///////// save file , save block
            if retry <= 0:
                print("===> get_all_funds END. FAILED to get {} <===".format(tickers))
            else:
                print("===> get_all_shares END <===")



if __name__ == "__main__":
    me = singleton.SingleInstance()
    gf = get_fundamentals()
    gf.get_all_funds()

