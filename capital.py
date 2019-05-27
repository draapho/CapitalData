import gui_main
import gui_sub
import subprocess
import webbrowser
import numpy as np
import pandas as pd
from ast import literal_eval
from gui_misc import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class GuiMain(QMainWindow, gui_main.Ui_MainWindow):
    def __init__(self, block=None):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.sys_init()

    def sys_init(self):
        # 工具按钮
        self.webM1M2 = QAction('M1M2走势', self)
        self.webPrice = QAction('平均股价', self)
        self.webPosition = QAction('平均持仓', self)
        self.webPE = QAction('等权市盈率', self)
        self.webPB = QAction('破净股比例', self)
        self.calculateRRI = QAction('Run calculate_rri', self)
        self.collectFunds = QAction('Run get_all_funds', self)
        self.autoFix = QAction('Fix based report.txt', self)
        self.collectSilence = QAction('Run collect_silence', self)
        self.openFile = QAction('Open _para folder', self)
        self.setParameter = QAction('Open parameter.ini', self)
        self.tickersCsv = QAction('Get tickers_dl.csv', self)
        self.blocksCsv = QAction('Get blocks_dl.csv', self)
        self.blocksFolder = QAction('Get tickers in blocks', self)

        menu = QMenu(self)
        menu.addAction(self.webM1M2)
        menu.addAction(self.webPrice)
        menu.addAction(self.webPosition)
        menu.addAction(self.webPE)
        menu.addAction(self.webPB)
        menu.addSeparator()
        menu.addAction(self.calculateRRI)
        menu.addAction(self.collectFunds)
        menu.addAction(self.collectSilence)
        menu.addAction(self.autoFix)
        menu.addSeparator()
        menu.addAction(self.openFile)
        menu.addAction(self.setParameter)
        menu.addSeparator()
        menu.addAction(self.tickersCsv)
        menu.addAction(self.blocksCsv)
        menu.addAction(self.blocksFolder)
        self.toolButton.setMenu(menu)

        self.webM1M2.triggered.connect(self.tools)
        self.webPrice.triggered.connect(self.tools)
        self.webPosition.triggered.connect(self.tools)
        self.webPE.triggered.connect(self.tools)
        self.webPB.triggered.connect(self.tools)
        self.calculateRRI.triggered.connect(self.tools)
        self.collectFunds.triggered.connect(self.tools)
        self.collectSilence.triggered.connect(self.tools)
        self.autoFix.triggered.connect(self.tools)
        self.openFile.triggered.connect(self.tools)
        self.setParameter.triggered.connect(self.tools)
        self.tickersCsv.triggered.connect(self.tools)
        self.blocksCsv.triggered.connect(self.tools)
        self.blocksFolder.triggered.connect(self.tools)

        self.para = read_parameter_ini()
        print(self.para)

        # # 搜索文件列表, 加入自动匹配
        # self.path = ".\\_data\\_info\\*.csv"
        # try:
        #     self.tickers_code = glob.glob(self.path)
        #     if len(self.tickers_code) == 0:
        #         self.tickers_code = glob.glob(self.path)
        #     # print (self.tickers_code)
        # except Exception as e:
        #     self.tickers_code = []
        #     print (e)
        # items_list = [os.path.splitext(os.path.basename(t))[0] for t in self.tickers_code]
        # print (items_list)

        # 加载代码和名称, 用于自动匹配输入
        items_list = []
        # 读取csv文件获取股票名称
        try:
            with open( ".\\_para\\tickers.csv", 'r', encoding="utf-8") as csv_file:
                reader = csv.reader(csv_file)
                for row in reader:
                    items_list.extend(row[0:2])
        except Exception as e:
            print (e)

        # 读取csv文件获取板块名称
        try:
            with open( ".\\_para\\blocks.csv", 'r', encoding="utf-8") as csv_file:
                reader = csv.reader(csv_file)
                for row in reader:
                    items_list.extend(row[0:2])
        except Exception as e:
            print (e)

        completer = QCompleter(items_list)
        completer.activated.connect(self.completerActivated)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)

        # table 初始数据
        # dtype=np.dtype([('code', 'S'), ('name', 'S'), ('资金异动', 'f'), ('资金强度', 'f'), ('股价波动', 'f'), ('排序', 'S'), ('平均市值', 'S'), ('净利润', 'S'), ('PE', 'f'), ('PB', 'f'), ('ROE', 'f'), ('个股', 'f')]),
        self.blocks = pd.read_csv(".\\_para\\blocks.csv", header=None, names=['code', 'name', '异动', '资金', '股价', '排序', 'PE', 'PB', 'ROE', '利润', '市值', '个股'],
                                 dtype=str, encoding="utf-8")  # na_values='-'
        # print (self.blocks)
        dtype=np.dtype([('code', 'S'), ('name', 'S'), ('异动', 'f'), ('资金', 'f'), ('股价', 'f'), ('评分', 'f'), ('PE', 'f'), ('PB', 'f'), ('ROE', 'f'), ('利润', 'S'), ('市值', 'S'), ('板块', 'S')])
        self.tickers = pd.read_csv(".\\_para\\tickers.csv", header=None, names=['code', 'name', '异动', '资金', '股价', '评分', 'PE', 'PB', 'ROE', '利润', '市值', '板块'], dtype=dtype, encoding="utf-8",na_values='-')
        # print (self.tickers)
        data = list(self.blocks.iloc[0])
        ##//////////////////////////////////////////////////////// pandas 小数精度问题. 解决方法: pandas导入, pandas输出, tableview设置...
        ## //////////////////////////// 板块加载数字化. 需要修改 tickers.csv

        # UI 初始化
        self.lineEditSticker.setCompleter(completer)
        self.lineEditSticker.setText(data[0])
        self.lineEditSticker.editingFinished.connect(self.editFinished)
        self.lineEditSticker.selectionChanged.connect(self.selection)
        self.buttonSwitch.clicked.connect(self.switchClicked)
        self.buttonMore.clicked.connect(self.moreClicked)
        self.tableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableView.pressed.connect(self.tableClicked)
        self.tableView.installEventFilter(self) # eventFilter
        self.tableView.doubleClicked.connect(self.tableDoubleClicked)
        self.tableView.setSortingEnabled(True)
        self.isTableBlocks = True
        self.set_table()
        self.code = drawChart(self.graphicsView,data,self.para)

    # ======= 操作复用函数 =======
    def set_table(self):
        if (self.isTableBlocks):
            self.model = PandasModel(self.blocks, parent=self.tableView, isBlock=True)
        else:
            self.model = PandasModel(self.tickers, parent=self.tableView)
        self.tableView.setModel(self.model)
        # self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents) # 导致性能非常差.
        self.tableView.setColumnWidth(1, 60)
        self.tableView.setColumnWidth(5, 30)
        self.tableView.setColumnWidth(6, 45)
        self.tableView.setColumnWidth(9, 90)
        self.tableView.setColumnWidth(10, 90)
        self.tableView.setColumnWidth(11, 90)
        self.tableView.setColumnWidth(0, 0) # 不要修改, 高效强制刷新的唯一方法
        self.tableView.setColumnWidth(0, 60)

    def codeChoosed(self, lineEdit=False):
        text = self.lineEditSticker.text()
        if (text in list(self.tickers['name'])):
            data = list(self.tickers[self.tickers['name'].isin([text])].iloc[0])
        elif (text in list(self.blocks['name'])):
            data = list(self.blocks[self.blocks['name'].isin([text])].iloc[0])
        elif (text in list(self.tickers['code'])):
            data = list(self.tickers[self.tickers['code'].isin([text])].iloc[0])
        elif (text in list(self.blocks['code'])):
            data = list(self.blocks[self.blocks['code'].isin([text])].iloc[0])
        else:
            self.lineEditSticker.setText("")
            data = [self.code]
        if (self.code !=  data[0]):
            if (data[0] in list(self.blocks['code']) and '-' not in data[0]):
                self.code = drawChart(self.graphicsView, data, self.para)
                if (lineEdit and self.isTableBlocks):
                    crow = list(self.blocks.code).index(data[0])
                    trow = self.model.getIndex().index(crow)
                    self.tableView.selectRow(trow)
            elif (data[0] in list(self.tickers['code'])):
                self.code = drawChart(self.graphicsView, data, self.para)
                if (lineEdit and not self.isTableBlocks):
                    crow = list(self.tickers.code).index(data[0])
                    trow = self.model.getIndex().index(crow)
                    self.tableView.selectRow(trow)

    # ======= operation =======
    def tools(self):
        if self.sender() == self.webM1M2:
            webbrowser.open("https://legulegu.com/stockdata/m1m2")  # M1M2供应量
        elif self.sender() == self.webPrice:
            webbrowser.open("https://legulegu.com/stockdata/market-analysis-average-price")  # A股平均股价
        elif self.sender() == self.webPosition:
            webbrowser.open("https://legulegu.com/stockdata/averageposition")  # 平均仓位
        elif self.sender() == self.webPE:
            webbrowser.open("https://legulegu.com/stockdata/a-ttm-lyr")  # 等权市盈率
        elif self.sender() == self.webPB:
            webbrowser.open("https://legulegu.com/stockdata/below-net-asset-statistics")  # 破净股比例
        elif self.sender() == self.collectFunds:
            subprocess.call('python collect_data.py "get_all_funds"',shell=False)
        elif self.sender() == self.calculateRRI:
            subprocess.call('python collect_data.py "calculate_rri"',shell=False)
        elif self.sender() == self.collectSilence:
            # os.system(get_cur_dir()+"\\collect_silence.bat")
            # subprocess.call('start /wait collect_silence.bat', shell=True)
            subprocess.call('python collect_silence.py', shell=False)
        elif self.sender() == self.autoFix:
            # 从记录文件提取下载失败的代码信息
            file = get_report_file()
            missed = {}
            with open(file, 'r') as f:
                for line in f.readlines():
                    if line.startswith("get_all_infos(missed)_2,"):
                        l = literal_eval("["+line.split("[")[1])
                        # print (type(l),l)
                        missed['infos'] = l
                    if line.startswith("get_all_funds(missed)_2,"):
                        l = literal_eval("["+line.split("[")[1])
                        # print (type(l),l)
                        missed['funds'] = l
            subprocess.call('python collect_data.py {} {}'.format(missed.get('infos', []), missed.get('funds', [])), shell=False)
        elif self.sender() == self.openFile:
            os.startfile('.\\_para\\')
        elif self.sender() == self.setParameter:
            os.startfile(get_parameter_file())
            self.para = read_parameter_ini()
        elif self.sender() == self.tickersCsv:
            subprocess.call('python collect_data.py "shares_dl_csv"', shell=False)
        elif self.sender() == self.blocksCsv:
            subprocess.call('python collect_data.py "blocks_dl_csv"', shell=False)
        elif self.sender() == self.blocksFolder:
            subprocess.call('python collect_data.py "blocks_folder"', shell=False)

    def completerActivated(self):
        self.codeChoosed(lineEdit=True)

    def editFinished(self):
        if (self.lineEditSticker.hasFocus()):   # 解决触发两次的问题
            self.codeChoosed(lineEdit=True)

    def selection(self):
        self.lineEditSticker.setText("")

    def switchClicked(self):
        self.isTableBlocks = not self.isTableBlocks
        self.set_table()

    def eventFilter(self, obj, event):
        if (obj == self.tableView):
            if (event.type() == QEvent.KeyPress):
                row = -10
                if (event.key() == Qt.Key_Up):
                    row = self.tableView.selectionModel().currentIndex().row() - 1
                if (event.key() == Qt.Key_Down):
                    row = self.tableView.selectionModel().currentIndex().row() + 1
                if (row >= -1):
                    column = self.tableView.selectionModel().currentIndex().column()
                    if (column > 1):
                        column = 1
                    if (row < 0):
                        row=0
                    if (self.isTableBlocks):
                        if (row >= len(self.blocks)):
                            row -= 1
                        brow = self.model.getIndex()[row]
                        text = self.blocks.values[brow][column]
                    else:
                        if (row >= len(self.tickers)):
                            row -= 1
                        text = self.tickers.values[self.model.getIndex()[row]][column]
                    self.lineEditSticker.setText(text)
                    self.codeChoosed()
        return False

    def tableClicked(self, mi):
        row = mi.row()
        column = mi.column()
        if (column > 1):
            column = 1
        # print (row, column)
        brow = self.model.getIndex()[row]
        if (self.isTableBlocks):
            text = self.blocks.values[brow][column]
        else:
            text = self.tickers.values[brow][column]
        self.lineEditSticker.setText(text)
        self.codeChoosed()

    def tableDoubleClicked(self, mi):
        brow = self.model.getIndex()[mi.row()]
        col = mi.column()
        if (self.isTableBlocks):
            block = self.blocks.values[brow]
            if block[0].startswith("BK") and (col < 6):
                dialog = GuiSub(block, self.para, parent=self)
                dialog.show()
            elif '-' not in block[0]:
                url = None
                if block[0] == '0000011':
                    if col==6:
                        url = "https://legulegu.com/stockdata/shanghaiPE"     # 上证市盈率
                    elif col==7:
                        url = "https://legulegu.com/stockdata/shanghaiPB"     # 上证市净率
                elif block[0] == "3990012":
                    if col==6:
                        url = "https://legulegu.com/stockdata/shenzhenPE"     # 深证市盈率
                    elif col==7:
                        url = "https://legulegu.com/stockdata/shenzhenPB"     # 深证市净率
                elif block[0] == "3990052":
                    if col==6:
                        url = "https://legulegu.com/stockdata/zxbPE"          # 中小市盈率
                    elif col==7:
                        url = "https://legulegu.com/stockdata/zxbPB"          # 中小市净率
                elif block[0] == "3990062":
                    if col==6:
                        url = "https://legulegu.com/stockdata/cybPE"          # 创业市盈率
                    elif col==7:
                        url = "https://legulegu.com/stockdata/cybPB"          # 创业市净率
                elif block[0] == "BK06111":
                    if col==6:
                        url = "https://legulegu.com/stockdata/sz50-ttm-lyr"   # 上证50市盈率
                    elif col==7:
                        url = "https://legulegu.com/stockdata/sz50-pb"   # 上证50市净率
                elif block[0] == "BK05001":
                    if col==6:
                        url = "https://legulegu.com/stockdata/hs300-ttm-lyr"  # 沪深300市盈率
                    elif col==7:
                        url = "https://legulegu.com/stockdata/hs300-pb"  # 沪深300市净率
                elif block[0] == "BK07001":
                    if col==6:
                        url = "https://legulegu.com/stockdata/zz500-ttm-lyr"  # 中证500市盈率
                    elif col==7:
                        url = "https://legulegu.com/stockdata/zz500-pb"  # 中证500市净率
                elif block[0] == "BK06121":
                    if col==6:
                        url = "https://legulegu.com/stockdata/sz180-ttm-lyr"  # 上证180市盈率
                    elif col==7:
                        url = "https://legulegu.com/stockdata/sz180-pb"  # 上证180市净率
                elif block[0] == "BK07051":
                    if col==6:
                        url = "https://legulegu.com/stockdata/sz380-ttm-lyr"  # 上证380市盈率
                    elif col==7:
                        url = "https://legulegu.com/stockdata/sz380-pb"  # 上证380市净率
                if (url):
                    webbrowser.open(url)
        else: # 打开个股基本面/信息网页
            code = self.tickers.values[brow][0]
            openBrowser(code)

    def moreClicked(self):
        code_list = list(self.blocks.code)
        if self.code is None:
            pass
        elif not self.code.startswith("BK"):
            # url = 'http://data.eastmoney.com/cjsj/hbgyl.html'
            url = 'https://legulegu.com/stockdata/m1m2' # M1M2供应量
            webbrowser.open(url)
        elif self.code in code_list:
            row = code_list.index(self.code)
            dialog = GuiSub(self.blocks.values[row], self.para, parent=self)
            dialog.show()
        else: # 打开个股基本面/信息网页
            openBrowser(self.code)

class GuiSub(QDialog,gui_sub.Ui_Dialog):
    def __init__(self, block, para={}, parent=None):
        super(self.__class__, self).__init__(parent)
        self.setupUi(self)
        self.block_code = block[0]
        self.block_name = block[1]
        self.block_pe = block[6]
        self.block_pb = block[7]
        self.para = para
        self.sys_init_block()

    def sys_init_block(self):
        # 读取列表
        with open("{}{}.csv".format(get_block_path(),self.block_code), 'r', encoding="utf-8") as csv_file:
            reader = csv.reader(csv_file)
            codes = [row[0] for row in reader]
        tickers = pd.read_csv(".\\_para\\tickers.csv", header=None, names=['code', 'name', '异动', '资金', '股价', '评分', '市值', '利润', 'PE', 'PB', 'ROE', '板块'],
                                   dtype=str, encoding="utf-8").set_index(['code'])
        ######## /////////////////////////// 加载数字化
        self.stickers = (tickers.loc[codes]).reset_index()
        data = list(self.stickers.iloc[0])
        # print(self.stickers)

        # 点击操作
        self.tableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableView.pressed.connect(self.sTableClicked)
        self.tableView.doubleClicked.connect(self.sTableDoubleClicked)
        self.tableView.installEventFilter(self) # eventFilter
        self.tableView.setSortingEnabled(True)

        # 初始化GUI
        self.setWindowTitle("{} {} PE{} PB{}".format(self.block_code,self.block_name,self.block_pe,self.block_pb))
        self.model = PandasModel(self.stickers, parent=self.tableView)
        self.tableView.setModel(self.model)
        # self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tableView.setColumnWidth(1, 60)
        self.tableView.setColumnWidth(5, 30)
        self.tableView.setColumnWidth(6, 45)
        self.tableView.setColumnWidth(9, 90)
        self.tableView.setColumnWidth(10, 90)
        self.tableView.setColumnWidth(11, 90)
        self.tableView.setColumnWidth(0, 0) # 不要修改, 高效强制刷新的唯一方法
        self.tableView.setColumnWidth(0, 60)
        self.scode = drawChart(self.graphicsView, data, self.para)

    def eventFilter(self, obj, event):
        if (obj == self.tableView):
            if (event.type() == QEvent.KeyPress):
                row = -10
                if (event.key() == Qt.Key_Up):
                    row = self.tableView.selectionModel().currentIndex().row() - 1
                if (event.key() == Qt.Key_Down):
                    row = self.tableView.selectionModel().currentIndex().row() + 1
                if (row >= -1):
                    column = self.tableView.selectionModel().currentIndex().column()
                    if (row < 0):
                        row=0
                    elif (row >= len(self.stickers)):
                        row -= 1
                    srow = self.model.getIndex()[row]
                    data = list(self.stickers.iloc[srow])
                    if (self.scode != data[0]):
                        self.scode = drawChart(self.graphicsView, data, self.para)
        return False

    def sTableClicked(self, mi):
        # row = mi.row()
        # column = mi.column()
        # print (row, column)
        srow = self.model.getIndex()[mi.row()]
        data = list(self.stickers.iloc[srow])
        if (self.scode != data[0]):
            self.scode = drawChart(self.graphicsView, data, self.para)

    def sTableDoubleClicked(self, mi):
        # 打开个股基本面/信息网页
        srow = self.model.getIndex()[mi.row()]
        code = self.stickers.values[srow][0]
        openBrowser(code)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui_action = GuiMain()
    gui_action.show()
    sys.exit(app.exec_())
