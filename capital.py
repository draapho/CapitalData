import sys
import os
import gui_main
import gui_sub
import subprocess
import datetime
import csv
import numpy as np
import pandas as pd
from myutil import *
from gui_misc import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class GuiMain(QMainWindow, gui_main.Ui_MainWindow):
    def __init__(self, block=None):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.sys_init()

    def sys_init(self):
        # 变量
        # self.file = ".\\_data\\_info\\0000011.csv"
        self.file = ".\\_data\\_info\\"
        self.index = {
                    "0000011": "上证指数",
                    "3990012": "深圳指数",
                    "3990052": "中小板",
                    "3990062": "创业板"
                }

        # 菜单栏
        self.actionParameter.triggered.connect(self.setParameter)
        self.actionOpen.triggered.connect(self.openFile)
        self.actionCollect.triggered.connect(self.collectDate)
        self.actionAutoFix.triggered.connect(self.autoFix)
        self.actionSharesCsv.triggered.connect(self.sharesCsv)
        self.actionBlocksCsv.triggered.connect(self.blocksCsv)
        self.actionBlocksFolders.triggered.connect(self.blocksFolder)

        try:
            with open( ".\\_para\\parameter.ini", 'r', encoding="utf-8") as csv_file:
                reader = csv.reader(skip_comments(csv_file))
                self.para = dict(reader)
        except Exception as e:
            self.para = {}
            print (e)
        print(self.para)

        # # 搜索文件列表
        # self.path = ".\\_data\\_info\\*.csv"
        # try:
        #     self.tickers_code = glob.glob(self.path)
        #     if len(self.tickers_code) == 0:
        #         self.tickers_code = glob.glob(self.path)
        #     # print (self.tickers_code)
        # except Exception as e:
        #     self.tickers_code = []
        #     self.file = ""
        #     print (e)
        # items_list = [os.path.splitext(os.path.basename(t))[0] for t in self.tickers_code]
        # print (items_list)

        # 加载代码和名称, 用于自动匹配输入
        items_list = list(self.index.values())
        # 读取csv文件获取股票名称
        try:
            with open( ".\\_para\\tickers.csv", 'r', encoding="utf-8") as csv_file:
                reader = csv.reader(csv_file)
                items_list.extend(list(dict(reader).keys()))
                items_list.extend(list(dict(reader).values()))
        except Exception as e:
            print (e)
        # 读取csv文件获取板块名称
        try:
            with open( ".\\_para\\blocks.csv", 'r', encoding="utf-8") as csv_file:
                reader = csv.reader(csv_file)
                items_list.extend(list(dict(reader).keys()))
                items_list.extend(list(dict(reader).values()))
        except Exception as e:
            print (e)

        # print (items_list)
        completer = QCompleter(items_list)
        completer.activated.connect(self.completerActivated)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)

        self.lineEditSticker.setCompleter(completer)
        self.lineEditSticker.setText(os.path.splitext(os.path.basename(self.file))[0])
        self.lineEditSticker.editingFinished.connect(self.editFinished)

        # table 初始数据
        self.blocks = pd.DataFrame(self.index.items(), columns=['code', 'name'])
        blocks_csv = pd.read_csv(".\\_para\\blocks.csv", header=None, names=['code', 'name'], dtype=np.dtype([('code', 'S'), ('name', 'S')]), encoding="utf-8")
        self.blocks = self.blocks.append(blocks_csv)
        # print (self.blocks)
        self.tickers = pd.read_csv(".\\_para\\tickers.csv", header=None, names=['code', 'name'], dtype=np.dtype([('code', 'S'), ('name', 'S')]), encoding="utf-8")
        # print (self.tickers)

        # 点击操作
        self.buttonSwitch.clicked.connect(self.buttonClicked)
        self.tableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableView.clicked.connect(self.tableClicked)
        self.tableView.doubleClicked.connect(self.tableDoubleClicked)

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
        elif (name in list(self.blocks['name'])):
            name = self.blocks[self.blocks['name'].isin([name])]
            name = name.iloc[0][0]
        if ((name in list(self.blocks['code'])) or (name in list(self.tickers['code']))):
            self.file = "{}\\{}.csv".format(os.path.dirname(self.file), name)
            self.drawChart()

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
        try:
            kNumber = self.para.get('K_NUMBER', 'all')
            if kNumber == '1y':
                n_end = 256
            elif kNumber == '3m':
                n_end = 64
            elif kNumber == '1m':
                n_end = 20
            else:
                n_end = 0
            quotes = loadData(self.file, n_end, n_end, names=columns, dtype=dtype, na_values= '-')
            # quotes = pd.read_csv(self.file, header=None, engine='c', names=columns, dtype=dtype, na_values= '-')
            quotes['vol3'] = quotes['vol2'] / 100000  # 单位转换为百亿元, 对应于资金流百分比
            # print (quotes)
        except Exception as e:
            print("open {} file failed!".format(self.file))
            print(e)
            self.graphicsView.clear()
            return
        # print(quotes)

        # 作图初始化
        self.graphicsView.clear()
        self.p1 = self.graphicsView.addPlot(row=0, col=0,
                                       title = os.path.splitext(os.path.basename(self.file))[0],
                                       axisItems={'bottom': DateAxisItem(list(quotes['date']), orientation='bottom')})
        p2 = self.graphicsView.addPlot(row=1, col=0,
                                       axisItems={'left': VolumnAxisItem(orientation='left')})
        p2.hideAxis('bottom')
        self.p1.setMouseEnabled(x=True,y=False)  # 鼠标滚轮仅X轴缩放
        p2.setMouseEnabled(x=True,y=False)
        p2.setXLink(self.p1)                     # 同步缩放
        # self.p1.scene().sigMouseClicked.connect(self.mouseClicked)

        # 导入数据
        item = KItem(quotes[['open', 'high', 'low', 'close']])
        self.p1Len = len(quotes)
        self.p1.addItem(item)
        self.p1.enableAutoRange()
        self.p1.setLimits(minXRange = 10, maxXRange = self.p1Len * 1.2, maxYRange = (quotes[['high']].max()['high'] - quotes[['low']].min()['low']) * 1.2)
        day5=quotes['close'].rolling(5).mean()      # 增加 5日线
        self.p1.plot(day5, pen="#ffffff")                # 白色
        day20=quotes['close'].rolling(20).mean()    # 增加 20日线
        self.p1.plot(day20, pen="#00ffff")               # 青色

        item = VItem(quotes[['vol3', 'main', 'xlarge', 'middle', 'open', 'close']])
        # p2.plot((quotes['small']))
        p2.addItem(item)
        p2.enableAutoRange()
        day5=quotes['main'].rolling(5).mean()    # 增加 5日线
        p2.plot(day5, pen="#ffffff")
        day20=quotes['main'].rolling(20).mean()    # 增加 20日线
        p2.plot(day20, pen="#00ffff")

        # # 参考1, 使用pyqtgraph: https://zmister.com/archives/187.html
        # # 参考2, 使用plt: https://www.jianshu.com/p/c10e57ccc7ba     from mpl_finance import candlestick_ohlc

    # ======= operation =======
    def setParameter(self):
        os.startfile('.\\_para\\parameter.ini')
        # 加载初始化参数
        try:
            with open( ".\\_para\\parameter.ini", 'r', encoding="utf-8") as csv_file:
                reader = csv.reader(skip_comments(csv_file))
                para = dict(reader)
        except Exception as e:
            print (e)

    def openFile(self):
        os.startfile('.\\_para\\')

    def collectDate(self):
        # os.system(get_cur_dir()+"\\collect_silence.bat")
        # subprocess.call('start /wait collect_silence.bat', shell=True)
        subprocess.call('python collect_silence.py', shell=False)

    def autoFix(self):
        subprocess.call('python collect_autofix.py', shell=False)

    def sharesCsv(self):
        subprocess.call('python collect_data.py "shares_dl_csv"', shell=False)

    def blocksCsv(self):
        subprocess.call('python collect_data.py "blocks_dl_csv"', shell=False)

    def blocksFolder(self):
        subprocess.call('python collect_data.py "blocks_folder"', shell=False)

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
            text = self.tickers.values[mi.row()][1]
        self.lineEditSticker.setText(text)
        self.codeChoosed()

    def tableDoubleClicked(self, mi):
        if (self.isTableBlocks):
            # block = self.blocks.values[mi.row()][0]
            block = self.blocks.values[mi.row()]
            if block[0] not in self.index:
                dialog = GuiSub(block, self.para, parent=self)
                dialog.show()
        else:
            pass
            # /////////////////////////显示基本面

    # def mouseClicked(self,evt):
    #     pos = evt.pos()
    #     print(pos)
    #     if self.p1.sceneBoundingRect().contains(pos):
    #         mousePoint = self.p1.vb.mapSceneToView(pos)
    #         index = int(mousePoint.x()+1/3)
    #         if index >= 0 and index <self.p1Len:
    #             print (index)


class GuiSub(QDialog,gui_sub.Ui_Dialog):
    def __init__(self, block, para={}, parent=None):
        super(self.__class__, self).__init__(parent)
        self.setupUi(self)
        self.block_code = block[0]
        self.block_name = block[1]
        self.spara = para
        self.sys_init_block()

    def sys_init_block(self):
        self.sfile = ".\\_data\\_info\\"

        # 读取列表
        self.stickers = pd.read_csv(".\\_para\\blocks\\{}.csv".format(self.block_code), header=None, names=['code', 'name'], dtype=np.dtype([('code', 'S'), ('name', 'S')]), encoding="utf-8")
        print (self.tickers)
        # 排序 /////////////////////////////

        # 点击操作
        # self.tableView.setSelectionMode(QAbstractItemView.SingleSelection)
        # self.tableView.clicked.connect(self.tableClicked)

        # 初始化GUI
        # self.set_table()
        # self.drawChart()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui_action = GuiMain()
    gui_action.show()
    sys.exit(app.exec_())
