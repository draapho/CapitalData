#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import webbrowser
import numpy as np
import pyqtgraph as pg
from ast import literal_eval
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from myutil import *

def openBrowser(code, flag=0xFF):
    if (flag & 0x01):
        url = 'http://data.eastmoney.com/stockcalendar/{}.html'.format(code[:-1]) # 个股日历
        webbrowser.open(url)
    if (flag & 0x02):
        url ='http://data.eastmoney.com/bbsj/yjbb/{}.html'.format(code[:-1]) # 财务报表
        webbrowser.open(url)
    # shsz = "SH" if (code[-1]==1) else "SZ"
    # url = 'http://f10.eastmoney.com/f10_v2/OperationsRequired.aspx?code={}{}#'.format(shsz, code[:-1]) # F10资料, 很多个股没有这个页面
    # webbrowser.open(url)

def drawChart(graphicsView, data, para):
    # 数据的最终格式:
    # ['2019-01-11", "15:26:49', '1', '000001', '上证指数', '2553.83', '2539.55', '2554.79', '2533.36', '14944410112', '122375663616', '-75811.38', '7516236800', '-7049105152', '46713.16', '0.39%', '25009520128', '-26234765568', '-122524.54', '-1.03%', '43805553408', '-44895364096', '-108981.07', '-0.91%', '43093999360', '-41246074880', '184792.45', '1.55%']
    columns = ['date', 'time', 'market', 'code', 'name', 'close', 'open', 'high', 'low', 'volume', 'vol2', 'main',
               'xin', 'xout', 'xlarge', 'xper', 'lin', 'lout', 'large', 'lper', 'min', 'mout', 'middle', 'mper', 'sin',
               'sout', 'small', 'sper']
    dtype = np.dtype([('date', 'S'), ('time', 'S'), ('market', 'S'), ('code', 'S'), ('name', 'S'),
                      ('close', '<f4'), ('open', '<f4'), ('high', '<f4'), ('low', '<f4'), ('volume', '<f4'),
                      ('vol2', '<f4'), ('main', '<f4'),
                      ('xin', '<f4'), ('xout', '<f4'), ('xlarge', '<f4'), ('xper', 'S'),
                      ('lin', '<f4'), ('lout', '<f4'), ('large', '<f4'), ('lper', 'S'),
                      ('min', '<f4'), ('mout', '<f4'), ('middle', '<f4'), ('mper', 'S'),
                      ('sin', '<f4'), ('sout', '<f4'), ('small', '<f4'), ('sper', 'S'),
                      ])
    # 读取数据
    try:
        n_end = int(para.get('K_NUMBER', 0))
        if (n_end>256) or (n_end<0):
            n_end=0
    except:
        n_end=0
    try:
        ci = l2i('code') # code index
        pei = l2i('PE')
        pbi = l2i('PB')
        file = "{}{}.csv".format(get_data_path(), data[ci])
        quotes = loadData(file, n_end, n_end, names=columns, dtype=dtype, na_values='-')
        # quotes = pd.read_csv(file, header=None, engine='c', names=columns, dtype=dtype, na_values= '-')
        quotes['vol3'] = quotes['vol2'] / 100000  # 单位转换为百亿元, 对应于资金流百分比
        quotes['c_pre'] = quotes['close'].shift()
        # print (quotes)
    except Exception as e:
        print(e)
        print("open {} file failed!".format(file))
        graphicsView.clear()
        return None
    # print(quotes)

    # 作图初始化
    graphicsView.clear()
    p1 = graphicsView.addPlot(row=0, col=0,
                                   axisItems={'bottom': DateAxisItem(list(quotes['date']), orientation='bottom')})
    p2 = graphicsView.addPlot(row=1, col=0,
                                   axisItems={'left': VolumnAxisItem(orientation='left'),
                                              'bottom': DateAxisItem(list(quotes['date']), orientation='bottom')})

    y1Axis = p1.getAxis('left')
    y2Axis = p2.getAxis('left')
    # y1Axis.setLabel(text='Price', units='units')
    # y2Axis.setLabel(text='Volumn', units='units')
    y1Axis.setWidth(w=40)
    y2Axis.setWidth(w=40)
    try:
        bk = str(data[l2i('板块')]).split('/')[1].strip()
    except:
        bk = ""
    title = "{} <i>{}</i> <i>{}</i>".format(data[ci][:-1], data[l2i('name')], bk)
    if (data[ci].startswith("BK") or data[ci].startswith("399") or data[ci] == "0000011"):
        title += "<br></br>PE{:.1f}".format(data[pei])
        title += " PB{:.1f}".format(data[pbi])
    else:
        if (data[pei]<30.0):     # 市盈率
            color = "#969696"
        elif (data[pei]<60.0):
            color = "#FF00FF"
        else:
            color = "#FF0000"
        title += "<br></br><font color={}>PE{:.1f}</font>".format(color,data[pei])
        if (data[pbi]<3.0):     # 市净率
            color = "#969696"
        elif (data[pbi]<6.0):
            color = "#FF00FF"
        else:
            color = "#FF0000"
        title += " <font color={}>PB{:.1f}</font>".format(color,data[pbi])
        # try:
        value = data[l2i('市值')].split('/')[1].strip()
        if ('万亿' in value or '亿亿' in value):
            color = "#969696"
        elif ('亿' in value):
            try:
                if float(value[:-1])<100.0:         # <100亿市值, 标注出来
                    color = "#FF00FF"
                else:
                    color = "#969696"
            except:
                color = "#FF00FF"
        else:
            color = "#FF00FF"
        title += " <font color={}>{}</font>".format(color,value)
        # except
    p1.setTitle(title)
    p2.hideAxis('bottom')

    p1.setMouseEnabled(x=True, y=False)  # 鼠标滚轮仅X轴缩放
    p2.setMouseEnabled(x=True, y=False)
    # 设置缩放
    p1Len = quotes.shape[0]
    p1.setRange(yRange=[quotes[['low']].min()['low'], quotes[['high']].max()['high']])
    p1.setLimits(minXRange=1, maxXRange=p1Len*1.25, xMin=-p1Len/4, xMax=p1Len*1.25)
    p2.setLimits(minXRange=1, maxXRange=p1Len*1.25, xMin=-p1Len/4, xMax=p1Len*1.25)
    # p1.enableAutoRange()
    # p2.enableAutoRange()
    p1.setXLink(p2)  # 同步缩放
    p2.setXLink(p1)  # 同步缩放

    # 导入数据
    ref_date = literal_eval(para.get('REF_DATE', "[]")) # 在K线图上标注出关键日期
    if not isinstance(ref_date, list):
        ref_idx = []
    else:
        ref_idx = []
        for d in ref_date:
            ref_idx += quotes[(quotes.date==d)].index.tolist()

    if (p1Len >= 16 and len(ref_idx)==0):
        ref_idx = [p1Len-16]

    if len(ref_idx):
        try:
            ref_len = int(para.get('REF_LENGTH', 0))
        except Exception as e:
            print ("drawChart ref_len error:{}".format(e))
            ref_len = 0
        if (ref_len > 0):
            ref_idx += [ref_idx[0]+ref_len]
        else:
            ref_idx += [-1] # 无结束点
    else:
        ref_idx = [-1]  # 不显示
    # print (ref_idx)

    item_list = ['date', 'open', 'high', 'low', 'close', 'c_pre', 'vol3', 'main', 'xlarge', 'middle', 'small']
    item = KItem(quotes[item_list], ref_idx)
    p1.addItem(item)
    day = quotes['close'].rolling(16).mean()  # 日均线
    p1.plot(day, pen="#ffffff")

    item = VItem(quotes[item_list], ref_idx)
    p2.addItem(item)
    dayS = quotes['main'].rolling(16).mean()  # 短均线
    p2.plot(dayS, pen="#ffffff")
    # dayL = quotes['main'].rolling(12).mean()  # 长均线
    # p2.plot(dayL, pen="#00ffff")

    # # 参考1, 使用pyqtgraph: https://zmister.com/archives/187.html
    # # 参考2, 使用plt: https://www.jianshu.com/p/c10e57ccc7ba     from mpl_finance import candlestick_ohlc
    return data[ci]

def popInfo(data, idx, win):
    # print (pos, idx)
    info = QMenu(win)
    # item_list = ['date', 'open', 'high', 'low', 'close', 'c_pre', 'vol3', 'main']
    date = data.loc[idx]['date']
    date = date[5:7] + date[8:10]
    open = data.loc[idx]['open']
    high = data.loc[idx]['high']
    low = data.loc[idx]['low']
    close = data.loc[idx]['close']
    c_pre = data.loc[idx]['c_pre']
    scale = 100 * (close - c_pre) / c_pre
    vol = data.loc[idx]['vol3']
    main = data.loc[idx]['main']
    vol_num = readableNum(vol * 10, divisor=10000, power="万", precision=2)
    main_num = readableNum(main, divisor=10000, power="万", precision=2)
    perm = main / vol  # 千分比
    info.addAction("{} | {:.2f}% {:.2f}‰ | {:.2f} / {:.2f} / {:.2f} / {:.2f} | {} / {}".format(date, scale, perm, open, close, high, low, vol_num, main_num))
    info.move(win.pos() + QPoint(15, 45))
    info.show()

class PandasModel(QAbstractTableModel):
    """
    Class to populate a table view with a pandas dataframe
    """
    def __init__(self, data, parent=None, isBlock=False):
        QAbstractTableModel.__init__(self, parent)
        self._data = data
        self._show = data
        self.isBlock = isBlock
        rri_sh = data.loc[0]['当日']
        rri_sz = data.loc[1]['当日']
        self.rri_max = max(rri_sh, rri_sz)
        self.rri_min = min(rri_sh, rri_sz)
        self._idx = list(self._show.index.values)
        # 有web链接的行
        self.blist = ["0000011", "3990012", "3990052", "3990062", "BK06111", "BK05001", "BK07011", "BK06121", "BK07051"]
        # 一线权重股, 金融地产石油, 消费白马
        #               上证50,   HS300_     上证180_   深证100R     银行       保险      券商信托    中字头     房地产     超级品牌     石油行业   食品饮料    酿酒行业    家电行业
        self.list1 = ["BK06111", "BK05001", "BK06121", "BK07431", "BK04751", "BK04741", "BK04731", "BK05051", "BK04511", "BK08111", "BK04641", "BK04381", "BK04771", "BK04561"]
        # 二线蓝筹股, 基建, 制造, 周期
        #             煤炭采选    有色金属    民航机场    铁路基建   港口水运   高速公路    仪器仪表    机械行业   工程建设    汽车行业    输配电气   交运设备    专用设备   水泥建材    钢铁行业    金属制品   化工行业     化纤行业    材料行业
        self.list2 = ["BK04371", "BK04781", "BK04201", "BK05921", "BK04501", "BK04211", "BK04581", "BK05451", "BK04251", "BK04811", "BK04571", "BK04291", "BK09101", "BK04241", "BK04791", "BK07391", "BK05381", "BK04711", "BK05371"]
        # 三线题材股, 科技, 医药, 生物, 中小板块
        #              中小板      创业板     中证500    上证380     深成500    国产软件    网络安全   云计算      大数据      军工     软件服务     电子信息    通讯行业    电信运营    安防设备  电子元件    医疗行业    医药制造
        self.list3 = ["3990052", "3990062", "BK07011", "BK07051", "BK05681", "BK06961", "BK06551", "BK05791", "BK06341", "BK04901", "BK07371", "BK04471", "BK04481", "BK07361", "BK07351", "BK04591", "BK07271", "BK04651"]

    def rowCount(self, parent=None):
        # return len(self._show.values)
        return self._show.shape[0]

    def columnCount(self, parent=None):
        # return self._show.columns.size
        return self._show.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            row = index.row()
            col = index.column()
            if role == Qt.DisplayRole:
                return self._show.values[row][col]  # 不能用 self._show.iloc[row][col]
            elif role == Qt.ForegroundRole:
                if self.isBlock:
                    val = self._show.values[row][l2i('code')]
                    if col==l2i('code') or col==l2i('name'):
                        if val in self.list1:
                            return QColor("#B03A2E") # 红色
                        elif val in self.list2:
                            return QColor("#D68910") # 橙色/黄色
                        elif val in self.list3:
                            return QColor("#1F618D") # 蓝色
                    if col==l2i('当日'):
                        rri = self._show.values[row][col]
                        if np.isnan(rri) or np.isnan(self.rri_max) or np.isnan(self.rri_min):
                            pass
                        else:
                            if rri > self.rri_max:
                                return QColor('#B03A2E')    # 红色
                            elif rri < self.rri_min:
                                return QColor('#1E8449')    # 绿色
                    if col==l2i('PE') or col==l2i('PB'):
                        if val in self.blist:
                            return QColor("#1F618D")    # 有网页链接
                else:
                    if col == l2i('分'):
                        val = self._show.values[row][col]
                        if (val<50):      # 总体评分
                            return QColor("#F53131")
                        elif (val<70):
                            return QColor("#D63DD6")

            elif role == Qt.BackgroundRole:
                val = self._show.iloc[row][l2i('|')]
                if val == "!":
                    return QColor("#D8EBFC")
        return QVariant()

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._show.columns[col]
        return None

    def sort(self,column, order):
        self.layoutAboutToBeChanged.emit()
        self._show = self._show.sort_values(by=list(self._show)[column], ascending=False if order else True)
        self._idx = list(self._show.index.values)
        self.layoutChanged.emit()
        # self.dataChanged.emit(QModelIndex(), QModelIndex())

    def getShow(self):
        return self._show

    def getIndex(self):
        return self._idx

    def setData(self, index, value=None, role=Qt.EditRole):
        if role == Qt.EditRole:
            self.layoutAboutToBeChanged.emit()
            row = index.row()
            brow = self._idx[row]
            if value is None:   # toggle
                if (self._data.loc[brow]['|'] == '!'):
                    self._data.loc[[brow], ['|']] = '.'
                    self._show.iloc[[row], [l2i('|')]] = '.'
                else:
                    self._data.loc[[brow], ['|']] = '!'
                    self._show.iloc[[row], [l2i('|')]] = '!'
            else:
                self._data.loc[[brow], ['|']] = value
                self._show.iloc[[row], [l2i('|')]] = value
            self.layoutChanged.emit()
            # self.dataChanged.emit(index, index)
            # return True  # No influnce here
        return False


class KItem(pg.GraphicsObject):
    def __init__(self, data, ref):
        pg.GraphicsObject.__init__(self)

        # 生成横轴的刻度名字
        self.data = data
        self.ref = ref
        self.generatePicture()

    def generatePicture(self):
        self.picture = QPicture()
        p = QPainter(self.picture)
        w = 1 / 3.
        last = None

        for t, (data, open, max, min, close, c_pre, vol3, main, xlarge, middle, small) in enumerate(self.data.values):
            if open > close:
                p.setBrush(pg.mkBrush('g'))
                p.setPen(pg.mkPen('g'))
                # if c_pre < close:
                #     p.setBrush(pg.mkBrush('r'))
                #     p.setPen(pg.mkPen('r'))
                p.drawLine(QPointF(t, min), QPointF(t, max))
                p.drawRect(QRectF(t - w, open, w * 2, close - open))
                last = close
            elif open < close:
                p.setBrush(pg.mkBrush('r'))
                p.setPen(pg.mkPen('r'))
                # if c_pre > close:
                #     p.setBrush(pg.mkBrush('g'))
                #     p.setPen(pg.mkPen('g'))
                p.drawLine(QPointF(t, min), QPointF(t, max))
                p.drawRect(QRectF(t - w, open, w * 2, close - open))
                last = close
            elif open == close:
                p.setBrush(pg.mkBrush('w'))
                p.setPen(pg.mkPen('w'))
                if c_pre > close:
                    p.setBrush(pg.mkBrush('g'))
                    p.setPen(pg.mkPen('g'))
                elif c_pre < close:
                    p.setBrush(pg.mkBrush('r'))
                    p.setPen(pg.mkPen('r'))
                if (min != max):
                    p.drawLine(QPointF(t, min), QPointF(t, max))
                p.drawLine(QPointF(t - w, close), QPointF(t+w, close))
                last = close
            elif last != None: # open or close is None
                # print (t, (open, max, min, close))
                p.setBrush(pg.mkBrush('w'))
                p.setPen(pg.mkPen('w'))
                p.drawLine(QPointF(t - w, last), QPointF(t+w, last))
            if t == self.ref[-1] or t == self.ref[0]:
                p.setBrush(pg.mkBrush('y'))
                p.setPen(pg.mkPen('y'))
                if open == close:
                    p.drawLine(QPointF(t - w, close), QPointF(t + w, close))
                else:
                    p.drawRect(QRectF(t-w+w/6, (open+close)/2-(close-open)/2.4, w*2-w/3, (close - open)/1.2))
                    # p.drawRect(QRectF(t-w, (open+close)/2-(close-open)/4, w*2, (close - open)/2))
                    # p.drawLine(QPointF(t - w, (open+close)/2), QPointF(t+w, (open+close)/2))
                if (min != max):
                    p.drawLine(QPointF(t, min), QPointF(t, max))
            elif t in self.ref:
                p.setBrush(Qt.NoBrush)
                p.setPen(pg.mkPen('y'))
                p.drawLine(QPointF(t - w, (open+close)/2), QPointF(t+w, (open+close)/2))
                if (min != max):
                    p.drawLine(QPointF(t, min), QPointF(t, max))

        p.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QRectF(self.picture.boundingRect())


class VItem(pg.GraphicsObject):
    def __init__(self, data, ref):
        pg.GraphicsObject.__init__(self)

        # 生成横轴的刻度名字
        self.data = data
        self.ref = ref
        self.generatePicture()

    def generatePicture(self):
        self.picture = QPicture()
        p = QPainter(self.picture)
        w = 1 / 3.
        # about color: https://doc.qt.io/archives/qtjambi-4.5.2_01/com/trolltech/qt/core/Qt.GlobalColor.html

        for t, (data, o, h, l, c, cp, vol, main, x, m, s) in enumerate(self.data.values):
            # p.setPen(pg.mkPen("#F9B83F"))
            # p.setBrush(pg.mkBrush("#F9B83F"))   # yellow, 中等资金
            # p.drawRect(QRectF(t, 0, w, m))
            p.setPen(pg.mkPen("#9AC4ED"))
            p.setBrush(pg.mkBrush("#9AC4ED"))   # blue, 小资金
            p.drawRect(QRectF(t, 0, w, s))
            if (abs(x) > abs(main)):
                p.setPen(pg.mkPen("#610000"))
                p.setBrush(pg.mkBrush("#610000"))   # dark red, 超大
                p.drawRect(QRectF(t-w, 0, w, x))
                p.setPen(pg.mkPen("#F735DE"))
                p.setBrush(pg.mkBrush("#F735DE"))  # magenta, 主力资金
                p.drawRect(QRectF(t - w, 0, w, main))
            else:
                p.setPen(pg.mkPen("#F735DE"))
                p.setBrush(pg.mkBrush("#F735DE"))  # magenta, 主力资金
                p.drawRect(QRectF(t - w, 0, w, main))
                p.setPen(pg.mkPen("#610000"))
                p.setBrush(pg.mkBrush("#610000"))   # dark red, 超大
                p.drawRect(QRectF(t-w, 0, w, x))
            # 主力资金(main) = 超大资金(x) + 大额资金(l)
            # 小额资金 + 中等资金 + 大额资金 + 超大资金 = 0

            p.setBrush(Qt.NoBrush)

            v = main / vol  # 1000 * 大资金流入 / 总交易额
            f = (c-o) / o  # 当日波动幅度
            pp = (c-cp) / cp  # 涨幅
            p.setPen(pg.mkPen("#a0a0a4"))
            if (main > 0):
                if (v > 0.3 and f < 0.01)  or (-f * v * 100 > 0.1) \
                    or (v > 0.3 and pp < 0.01) or (-pp * v * 100 > 0.2):
                    # 小幅波动, 大幅流入 # 大资金流入比 * 股价下跌幅度 * 100
                    p.setPen(pg.mkPen('#F60000'))                 # 异动, 红色标出
                elif (v > 0.5):
                    p.setPen(pg.mkPen('#F9B83F'))
                # elif (t > self.ref[0] and t < self.ref[-1]):    # 指定周期内, 只要是流入, 就标注出.
                #     p.setPen(pg.mkPen('#FF6600'))
            p.drawRect(QRectF(t-w, -vol, 2*w, 2*vol))   # 百分比化的交易量. 极值为资金流占比达到10%
        p.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QRectF(self.picture.boundingRect())


class DateAxisItem(pg.AxisItem):
    def __init__(self, date, *args, **kwargs):
        super(DateAxisItem, self).__init__(*args, **kwargs)
        self.date = date

    def tickStrings(self, values, scale, spacing):
        at = []
        for value in values:
            v = int(value)
            if (v >= 0) and (v < len(self.date)):
                temp = self.date[v].split('-')
                at.append(temp[1]+temp[2])
            else:
                at.append("")
        return at

class VolumnAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super(VolumnAxisItem, self).__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        # return [format(value, '.0e') for value in values]
        return [readableNum(value,divisor=10000,power="万",precision=0) for value in values]
