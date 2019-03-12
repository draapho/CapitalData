import sys
import os
import glob
import gui_capital
import subprocess
import datetime
import csv
import numpy as np
import pandas as pd
import pyqtgraph as pg
from myutil import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class capital(QMainWindow, gui_capital.Ui_MainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.sys_init()

    def sys_init(self):
        # 变量
        year = datetime.date.today().strftime('%Y')
        self.path = ".\\_data\\{}\\_info\\*.csv"

        # 菜单栏
        self.actionOpen.triggered.connect(self.openFile)
        self.actionCollect.triggered.connect(self.collectDate)
        self.actionAutoFix.triggered.connect(self.autoFix)
        self.actionDlSave.triggered.connect(self.dlSave)

        # 搜索文件列表
        try:
            self.tickers = glob.glob(self.path.format(year))
            if len(self.tickers) == 0:
                year = year-1
                self.tickers = glob.glob(self.path.format(year))
            self.file = ".\\_data\\{}\\_info\\上证指数.csv".format(year)
            # print (self.tickers)
        except Exception as e:
            self.tickers = []
            self.file = ""
            print (e)

        # 读取csv文件获取股票名称
        try:
            with open( ".\\_para\\tickers.csv", 'r', encoding="utf-8") as csv_file:
                reader = csv.reader(csv_file)
                self.names = list(dict(reader).values())
        except Exception as e:
            print (e)
            self.names = []
        # print(self.names)

        # 自动补全
        items_list = [os.path.splitext(os.path.basename(t))[0] for t in self.tickers]
        items_list.extend(self.names)
        # print (items_list)
        completer = QCompleter(items_list)
        completer.activated.connect(self.completerActivated)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        self.lineEditSticker.setCompleter(completer)
        self.lineEditSticker.setText(os.path.splitext(os.path.basename(self.file))[0])
        self.lineEditSticker.editingFinished.connect(self.editFinished)

        # table 初始数据
        try:
            with open( ".\\_para\\blocks.csv", 'r', encoding="utf-8") as csv_file:
                reader = csv.reader(csv_file)
                self.blocks = pd.DataFrame(reader, columns=['code', 'name'])
                self.blocks['deviate'] = np.nan
                self.blocks['20days'] = np.nan
        except Exception as e:
            print (e)
            self.blocks = pd.DataFrame(columns=['code', 'name', 'deviate', '20days'])
        # print (self.blocks)

        try:
            with open( ".\\_para\\tickers.csv", 'r', encoding="utf-8") as csv_file:
                reader = csv.reader(csv_file)
                self.tickers = pd.DataFrame(reader, columns=['code', 'name'])
                self.tickers['deviate'] = np.nan
                self.tickers['20days'] = np.nan
        except Exception as e:
            print (e)
            self.tickers_dict = pd.DataFrame(columns=['code', 'name', 'deviate', '20days'])
        # print (self.tickers)

        # 点击操作
        self.buttonSwitch.clicked.connect(self.buttonClicked)
        self.tableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableView.clicked.connect(self.tableClicked)

        # 初始化GUI
        self.isTableBlocks = True
        self.set_table()
        self.drawChart()

    # ======= 操作复用函数 =======
    def set_table(self):
        if (self.isTableBlocks):
            model = PandasModel(self.blocks)
        else:
            model = PandasModel(self.tickers)
        self.tableView.setModel(model)

    def codeChoosed(self):
        name = self.lineEditSticker.text()
        if (name in list(self.tickers['name'])):
            name = self.tickers[self.tickers['name'].isin([name])]
            name = name.iloc[0][0]
        if ((name in list(self.blocks['name'])) or (name in list(self.tickers['code']))):
            name = "{}\\{}.csv".format(os.path.dirname(self.file), name)
            if os.path.exists(name):
                print (name)
                self.file = name
                self.drawChart()
                return
        print ("Not find {}".format(name))
        self.lineEditSticker.setText(os.path.splitext(os.path.basename(self.file))[0])

    def drawChart(self):
        # 数据的最终格式:
        # ['2019-01-11", "15:26:49', '1', '000001', '上证指数', '2553.83', '2539.55', '2554.79', '2533.36', '14944410112', '122375663616', '-75811.38', '7516236800', '-7049105152', '46713.16', '0.39%', '25009520128', '-26234765568', '-122524.54', '-1.03%', '43805553408', '-44895364096', '-108981.07', '-0.91%', '43093999360', '-41246074880', '184792.45', '1.55%']
        columns = ['date', 'time', 'market','code','name','close','open','high','low','volume','vol2', 'main', 'xin', 'xout', 'xlarge', 'xper', 'lin', 'lout', 'large', 'lper', 'min', 'mout', 'middle', 'mper',  'sin', 'sout', 'small', 'sper' ]
        dtype = np.dtype([('date', 'S'), ('time', 'S'), ('market', 'S'), ('code', 'S'), ('name', 'S'),
                          ('close', '<f4'), ('open', '<f4'), ('high', '<f4'), ('low', '<f4'), ('volume', '<f4'), ('vol2', '<f4'), ('main', '<f4'),
                          ('xin', '<f4'),('xout', '<f4'),('xlarge', '<f4'),('xper', 'S'),
                          ('lin', '<f4'),('lout', '<f4'),('large', '<f4'),('lper', 'S'),
                          ('min', '<f4'),('mout', '<f4'),('middle', '<f4'),('mper', 'S'),
                          ('sin', '<f4'),('sout', '<f4'),('small', '<f4'),('sper', 'S'),
                          ])
        # 读取数据
        quotes = pd.read_csv(self.file, header=None, names=columns, dtype=dtype)
        quotes['vol3'] = quotes['vol2'] / 100000  # 单位转换为百亿元, 对应于资金流百分比
        # print(quotes)

        # 作图初始化
        self.graphicsView.clear()
        p1 = self.graphicsView.addPlot(row=0, col=0,
                                       title = os.path.splitext(os.path.basename(self.file))[0],
                                       axisItems={'bottom': DateAxisItem(list(quotes['date']), orientation='bottom')})
        p2 = self.graphicsView.addPlot(row=1, col=0,
                                       axisItems={'left': VolumnAxisItem(orientation='left')})
        p2.hideAxis('bottom')
        p1.setMouseEnabled(x=True,y=False)  # 鼠标滚轮仅X轴缩放
        p2.setMouseEnabled(x=True,y=False)
        p2.setXLink(p1)                     # 同步缩放

        # 导入数据
        item = KItem(quotes[['open', 'high', 'low', 'close']])
        p1.addItem(item)
        day5=quotes['close'].rolling(5).mean()    # 增加 5日线
        p1.plot(day5, pen="#ffffff")                # 白色
        day20=quotes['close'].rolling(20).mean()    # 增加 20日线
        p1.plot(day20, pen="#00ffff")               # 青色

        item = VItem(quotes[['vol3', 'main', 'xlarge', 'middle', 'open', 'close']])
        # p2.plot((quotes['small']))
        p2.addItem(item)
        day5=quotes['main'].rolling(5).mean()    # 增加 5日线
        p2.plot(day5, pen="#ffffff")
        day20=quotes['main'].rolling(20).mean()    # 增加 20日线
        p2.plot(day20, pen="#00ffff")

        # # 参考1, 使用pyqtgraph: https://zmister.com/archives/187.html
        # # 参考2, 使用plt: https://www.jianshu.com/p/c10e57ccc7ba     from mpl_finance import candlestick_ohlc

    # ======= operation =======
    def openFile(self):
        os.startfile('.\\')

    def collectDate(self):
        # os.system(get_cur_dir()+"\\collect_silence.bat")
        subprocess.call('start /wait collect_silence.bat', shell=True)

    def autoFix(self):
        subprocess.call('start /wait collect_autofix.bat', shell=True)

    def dlSave(self):
        subprocess.call('start /wait python collect_data.py', shell=True)

    def completerActivated(self):
        self.codeChoosed()

    def editFinished(self):
        if (self.lineEditSticker.hasFocus()):   # 解决触发两次的问题
            self.codeChoosed()

    def buttonClicked(self):
        self.isTableBlocks = not self.isTableBlocks
        self.set_table()

    def tableClicked(self, mi):
        # row = mi.row()
        # column = mi.column()
        # print (row, column)
        if (self.isTableBlocks):
            text = self.blocks.values[mi.row()][1]
        else:
            text = self.tickers.values[mi.row()][0]
        self.lineEditSticker.setText(text)
        self.codeChoosed()

class PandasModel(QAbstractTableModel):
    """
    Class to populate a table view with a pandas dataframe
    """
    def __init__(self, data, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self._data = data

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
        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None


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
        for t, (open, max, min, close) in enumerate(self.data.values):
            if open > close:
                p.setBrush(pg.mkBrush('g'))
                p.setPen(pg.mkPen('g'))
            else:
                p.setBrush(pg.mkBrush('r'))
                p.setPen(pg.mkPen('r'))
            p.drawLine(QPointF(t, min), QPointF(t, max))
            p.drawRect(QRectF(t - w, open, w * 2, close - open))
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
        return [format(value, '.0e') for value in values]

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui_action = capital()
    gui_action.show()
    sys.exit(app.exec_())