from PyQt5.QtCore import *
from PyQt5.QtGui import *
from myutil import *
import webbrowser
import numpy as np
import pyqtgraph as pg

def openBrowser(code):
    url = 'http://data.eastmoney.com/stockcalendar/{}.html'.format(code[:-1]) # 个股日历
    webbrowser.open(url)
    # url = 'http://data.eastmoney.com/bbsj/{}.html'.format(code[:-1]) # 业绩报表
    # webbrowser.open(url)
    shsz = "SH" if (code[-1]==1) else "SZ"
    url = 'http://f10.eastmoney.com/f10_v2/OperationsRequired.aspx?code={}{}#'.format(shsz, code[:-1]) # F10资料
    webbrowser.open(url)

def drawChart(graphicsView, data, kNumber='all'):
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
        if kNumber == '1y':
            n_end = 256
        elif kNumber == '6m':
            n_end = 128
        elif kNumber == '3m':
            n_end = 64
        elif kNumber == '1m':
            n_end = 24
        else:
            n_end = 0

        file = "{}{}.csv".format(get_data_path(), data[0])
        quotes = loadData(file, n_end, n_end, names=columns, dtype=dtype, na_values='-')
        # quotes = pd.read_csv(file, header=None, engine='c', names=columns, dtype=dtype, na_values= '-')
        quotes['vol3'] = quotes['vol2'] / 100000  # 单位转换为百亿元, 对应于资金流百分比
        # print (quotes)
    except Exception as e:
        print("open {} file failed!".format(file))
        print(e)
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
    title = "{} <i>{}</i>".format(data[0][:-1], data[1])
    if (data[0].startswith("BK") or data[0].startswith("399") or data[0] == "0000011"):
        pass
        # ////////////////////////////////////////////// 也显示一下
    else:
        if (data[6]<" 30.0"):     # 市盈率
            color = "#969696"
        elif (data[6]<" 60.0"):
            color = "#FF00FF"
        else:
            color = "#FF0000"
        title += "<br></br><font color={}>PE{}</font>".format(color,data[6].strip())
        if (data[7]<" 3.0"):     # 市净率
            color = "#969696"
        elif (data[7]<" 6.0"):
            color = "#FF00FF"
        else:
            color = "#FF0000"
        title += " <font color={}>PB{}</font>".format(color,data[7].strip())
    p1.setTitle(title)
    p2.hideAxis('bottom')

    p1.setMouseEnabled(x=True, y=False)  # 鼠标滚轮仅X轴缩放
    p2.setMouseEnabled(x=True, y=False)
    # 设置缩放
    p1Len = len(quotes)
    p1.setRange(yRange=[quotes[['low']].min()['low'], quotes[['high']].max()['high']])
    p1.setLimits(minXRange=1, maxXRange=p1Len*1.25, xMin=-p1Len/4, xMax=p1Len*1.25)
    p2.setLimits(minXRange=1, maxXRange=p1Len*1.25, xMin=-p1Len/4, xMax=p1Len*1.25)
    # p1.enableAutoRange()
    # p2.enableAutoRange()
    p1.setXLink(p2)  # 同步缩放
    p2.setXLink(p1)  # 同步缩放

    # 导入数据
    item = KItem(quotes[['open', 'high', 'low', 'close']])
    p1.addItem(item)
    day = quotes['close'].rolling(16).mean()  # 日均线
    p1.plot(day, pen="#ffffff")

    item = VItem(quotes[['vol3', 'main', 'xlarge', 'middle', 'open', 'close']])
    p2.addItem(item)
    dayS = quotes['main'].rolling(5).mean()  # 短均线
    p2.plot(dayS, pen="#ffffff")
    dayL = quotes['main'].rolling(12).mean()  # 长均线
    p2.plot(dayL, pen="#00ffff")

    # # 参考1, 使用pyqtgraph: https://zmister.com/archives/187.html
    # # 参考2, 使用plt: https://www.jianshu.com/p/c10e57ccc7ba     from mpl_finance import candlestick_ohlc
    return data[0]


class PandasModel(QAbstractTableModel):
    """
    Class to populate a table view with a pandas dataframe
    """
    def __init__(self, data, parent=None, coloring=False):
        QAbstractTableModel.__init__(self, parent)
        self._data = data
        self.coloring=coloring
        self.index = list(self._data.index.values)

    def rowCount(self, parent=None):
        return len(self._data.values)
        # return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.columns.size
        # return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.values[index.row()][index.column()])
            elif self.coloring and (role == Qt.ForegroundRole):
                if (index.column() == 5):
                    data = self._data.values[index.row()][5]
                    if (data<"50"):      # 总体评分
                        return QColor("#F53131")
                    elif (data<"70"):
                        return QColor("#D63DD6")
                    # return QColor(Qt.red)
        return QVariant()

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None

    def sort(self,column, order):
        self.layoutAboutToBeChanged.emit()
        self._data = self._data.sort_values(by=list(self._data)[column], ascending=False if order else True)
        self.index = list(self._data.index.values)
        self.layoutChanged.emit()

    def getIndex(self):
        # print(row, self.index)
        # print(self.index[row])
        return self.index


class KItem(pg.GraphicsObject):
    def __init__(self, data):
        pg.GraphicsObject.__init__(self)

        # 生成横轴的刻度名字
        self.data = data  ## data must have fields: open, max, min, close
        self.generatePicture()

    def generatePicture(self):
        self.picture = QPicture()
        p = QPainter(self.picture)
        w = 1 / 3.
        last = None
        for t, (open, max, min, close) in enumerate(self.data.values):
            if open > close:
                p.setBrush(pg.mkBrush('g'))
                p.setPen(pg.mkPen('g'))
                p.drawLine(QPointF(t, min), QPointF(t, max))
                p.drawRect(QRectF(t - w, open, w * 2, close - open))
                last = close
            elif open < close:
                p.setBrush(pg.mkBrush('r'))
                p.setPen(pg.mkPen('r'))
                p.drawLine(QPointF(t, min), QPointF(t, max))
                p.drawRect(QRectF(t - w, open, w * 2, close - open))
                last = close
            elif open == close:
                # print (t, (open, max, min, close))
                p.setBrush(pg.mkBrush('w'))
                p.setPen(pg.mkPen('w'))
                if (min != max):
                    p.drawLine(QPointF(t, min), QPointF(t, max))
                p.drawLine(QPointF(t - w, close), QPointF(t+w, close))
                last = close
            elif last != None: # open or close is None
                # print (t, (open, max, min, close))
                p.setBrush(pg.mkBrush('y'))
                p.setPen(pg.mkPen('y'))
                p.drawLine(QPointF(t - w, last), QPointF(t+w, last))
        p.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QRectF(self.picture.boundingRect())


class VItem(pg.GraphicsObject):
    def __init__(self, data):
        pg.GraphicsObject.__init__(self)

        # 生成横轴的刻度名字
        self.data = data  ## data must have fields: vol2, main, xlarge, middle, open, close
        self.generatePicture()

    def generatePicture(self):
        self.picture = QPicture()
        p = QPainter(self.picture)
        w = 1 / 3.
        # about color: https://doc.qt.io/archives/qtjambi-4.5.2_01/com/trolltech/qt/core/Qt.GlobalColor.html
        for t, (v, main, x, m, o, c) in enumerate(self.data.values):
            p.setPen(pg.mkPen("#ffff00"))
            p.setBrush(pg.mkBrush("#ffff00"))   # yellow, 中等资金
            p.drawRect(QRectF(t, 0, w, m))
            if (abs(x) > abs(main)):
                p.setPen(pg.mkPen("#800000"))
                p.setBrush(pg.mkBrush("#800000"))   # dark red, 超大
                p.drawRect(QRectF(t-w, 0, w, x))
                p.setPen(pg.mkPen("#ff00ff"))
                p.setBrush(pg.mkBrush("#ff00ff"))  # magenta, 主力资金
                p.drawRect(QRectF(t - w, 0, w, main))
            else:
                p.setPen(pg.mkPen("#ff00ff"))
                p.setBrush(pg.mkBrush("#ff00ff"))  # magenta, 主力资金
                p.drawRect(QRectF(t - w, 0, w, main))
                p.setPen(pg.mkPen("#800000"))
                p.setBrush(pg.mkBrush("#800000"))   # dark red, 超大
                p.drawRect(QRectF(t-w, 0, w, x))
            # 主力资金(main) = 超大资金(x) + 大额资金(l)
            # 小额资金 + 中等资金 + 大额资金 + 超大资金 = 0

            p.setBrush(Qt.NoBrush)
            if (c-o < 0) and (main > 0):
                p.setPen(pg.mkPen('r'))
            else:
                p.setPen(pg.mkPen("#a0a0a4"))
            p.drawRect(QRectF(t-w, -v, 2*w, 2*v))   # 百分比化的交易量. 极值为资金流占比达到10%
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
