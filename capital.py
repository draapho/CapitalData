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
        init_index="0000011"
        self.file = ".\\_data\\_info\\{}.csv".format(init_index)
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
        self.kNumber = self.para.get('K_NUMBER', 'all')

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
                dicts = dict(reader)
                items_list.extend(list(dicts.keys()))
                items_list.extend(list(dicts.values()))
        except Exception as e:
            print (e)
        # 读取csv文件获取板块名称

        try:
            with open( ".\\_para\\blocks.csv", 'r', encoding="utf-8") as csv_file:
                reader = csv.reader(csv_file)
                dicts = dict(reader)
                items_list.extend(list(dicts.keys()))
                items_list.extend(list(dicts.values()))
        except Exception as e:
            print (e)

        completer = QCompleter(items_list)
        completer.activated.connect(self.completerActivated)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)

        self.lineEditSticker.setCompleter(completer)
        self.lineEditSticker.setText(os.path.splitext(os.path.basename(self.file))[0])
        self.lineEditSticker.editingFinished.connect(self.editFinished)

        # table 初始数据
        self.blocks = pd.DataFrame(list(self.index.items()), columns=['code', 'name'])
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
        drawChart(self.graphicsView,self.file,name=self.index[init_index],kNumber=self.kNumber)

    # ======= 操作复用函数 =======
    def set_table(self):
        if (self.isTableBlocks):
            model = PandasModel(self.blocks)
        else:
            model = PandasModel(self.tickers)
        self.tableView.setModel(model)

    def codeChoosed(self):
        text = self.lineEditSticker.text()
        if (text in list(self.tickers['name'])):
            name = text
            code = self.tickers[self.tickers['name'].isin([text])]
            code = code.iloc[0][0]
        elif (text in list(self.blocks['name'])):
            name = text
            code = self.blocks[self.blocks['name'].isin([text])]
            code = code.iloc[0][0]
        if (text in list(self.tickers['code'])):
            code = text
            name = self.tickers[self.tickers['name'].isin([text])]
            name = name.iloc[0][0]
        elif (text in list(self.blocks['code'])):
            code = text
            name = self.blocks[self.blocks['name'].isin([text])]
            name = name.iloc[0][0]
        if (code in list(self.blocks['code'])):
            self.file = "{}\\{}.csv".format(os.path.dirname(self.file), code)
            drawChart(self.graphicsView,self.file,name=name,kNumber=self.kNumber)
        elif (code in list(self.tickers['code'])):
            self.file = "{}\\{}.csv".format(os.path.dirname(self.file), code)
            drawChart(self.graphicsView,self.file,name=name,kNumber=self.kNumber)

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
                dialog = GuiSub(block, self.kNumber, parent=self)
                dialog.show()
        else:
            pass
            # /////////////////////////显示基本面

class GuiSub(QDialog,gui_sub.Ui_Dialog):
    def __init__(self, block, para={}, parent=None):
        super(self.__class__, self).__init__(parent)
        self.setupUi(self)
        self.block_code = block[0]
        self.block_name = block[1]
        self.spara = para
        self.sys_init_block()

    def sys_init_block(self):
        self.sfile = ".\\_data\\_info\\{}.csv".format(self.block_code)

        # 读取列表
        self.stickers = pd.read_csv(".\\_para\\blocks\\{}.csv".format(self.block_code), header=None, names=['code', 'name'], dtype=np.dtype([('code', 'S'), ('name', 'S')]), encoding="utf-8")
        # 排序 /////////////////////////////

        # 点击操作
        self.tableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableView.clicked.connect(self.stableClicked)

        # 初始化GUI
        self.setWindowTitle("{} {}".format(self.block_code,self.block_name))
        model = PandasModel(self.stickers)
        self.tableView.setModel(model)
        drawChart(self.graphicsView,self.sfile,name=self.block_name,kNumber=self.spara)

    def stableClicked(self, mi):
        # row = mi.row()
        # column = mi.column()
        # print (row, column)
        code = self.stickers.values[mi.row()][0]
        name = self.stickers.values[mi.row()][1]
        self.sfile = "{}\\{}.csv".format(os.path.dirname(self.sfile), code)
        drawChart(self.graphicsView, self.sfile, name=name, kNumber=self.spara)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui_action = GuiMain()
    gui_action.show()
    sys.exit(app.exec_())
