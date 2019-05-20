import gui_main
import gui_sub
import subprocess
from gui_misc import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class GuiMain(QMainWindow, gui_main.Ui_MainWindow):
    def __init__(self, block=None):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.sys_init()

    def sys_init(self):
        # 变量
        self.code="0000011"
        self.file = ".\\_data\\_info\\{}.csv".format(self.code)
        self.index = {
                    "0000011": "上证指数",
                    "3990012": "深圳指数",
                    "3990052": "中小板",
                    "3990062": "创业板"
                }

        # 工具按钮
        self.collectDate = QAction('Run collect_data', self)
        self.autoFix = QAction('Run collect_autofix', self)
        self.openFile = QAction('Open _para folder', self)
        self.setParameter = QAction('Open parameter.ini', self)
        self.tickersCsv = QAction('Get tickers_dl.csv', self)
        self.blocksCsv = QAction('Get blocks_dl.csv', self)
        self.blocksFolder = QAction('Get tickers in blocks', self)

        menu = QMenu(self)
        menu.addAction(self.collectDate)
        menu.addAction(self.autoFix)
        menu.addSeparator()
        menu.addAction(self.openFile)
        menu.addAction(self.setParameter)
        menu.addSeparator()
        menu.addAction(self.tickersCsv)
        menu.addAction(self.blocksCsv)
        menu.addAction(self.blocksFolder)
        self.toolButton.setMenu(menu)

        self.collectDate.triggered.connect(self.tools)
        self.autoFix.triggered.connect(self.tools)
        self.openFile.triggered.connect(self.tools)
        self.setParameter.triggered.connect(self.tools)
        self.tickersCsv.triggered.connect(self.tools)
        self.blocksCsv.triggered.connect(self.tools)
        self.blocksFolder.triggered.connect(self.tools)

        para = self.read_parameter_ini()
        print(para)
        self.kNumber = para.get('K_NUMBER', 'all')

        # # 搜索文件列表, 加入自动匹配
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
        self.buttonSwitch.clicked.connect(self.switchClicked)
        self.buttonMore.clicked.connect(self.moreClicked)
        self.tableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableView.pressed.connect(self.tableClicked)
        self.tableView.installEventFilter(self) # eventFilter
        self.tableView.doubleClicked.connect(self.tableDoubleClicked)

        # 初始化GUI
        self.isTableBlocks = True
        self.set_table()
        drawChart(self.graphicsView,self.file,name=self.index[self.code],kNumber=self.kNumber)

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
            self.code = code.iloc[0][0]
        elif (text in list(self.blocks['name'])):
            name = text
            code = self.blocks[self.blocks['name'].isin([text])]
            self.code = code.iloc[0][0]
        if (text in list(self.tickers['code'])):
            self.code = text
            name = self.tickers[self.tickers['code'].isin([text])]
            name = name.iloc[0][1]
        elif (text in list(self.blocks['code'])):
            self.code = text
            name = self.blocks[self.blocks['code'].isin([text])]
            name = name.iloc[0][1]
        if (self.code !=  os.path.splitext(os.path.basename(self.file))[0]):
            if (self.code in list(self.blocks['code'])):
                self.file = "{}\\{}.csv".format(os.path.dirname(self.file), self.code)
                drawChart(self.graphicsView,self.file,name=name,kNumber=self.kNumber)
            elif (self.code in list(self.tickers['code'])):
                self.file = "{}\\{}.csv".format(os.path.dirname(self.file), self.code)
                drawChart(self.graphicsView,self.file,name=name,kNumber=self.kNumber)

    def read_parameter_ini(self):
        try:
            with open(get_parameter_file(), 'r', encoding="utf-8-sig") as csv_file:
                reader = csv.reader(skip_comments(csv_file))
                para = dict(reader)
        except Exception as e:
            para = {}
            print("Decode \"parameter.ini\" failed! ERR:{}".format(e))
        return para

    # ======= operation =======
    def tools(self):
        if self.sender() == self.collectDate:
            # os.system(get_cur_dir()+"\\collect_silence.bat")
            # subprocess.call('start /wait collect_silence.bat', shell=True)
            subprocess.call('python collect_silence.py', shell=False)
        elif self.sender() == self.autoFix:
            subprocess.call('python collect_autofix.py', shell=False)
        elif self.sender() == self.openFile:
            os.startfile('.\\_para\\')
        elif self.sender() == self.setParameter:
            os.startfile(get_parameter_file())
            self.kNumber = self.read_parameter_ini().get('K_NUMBER', 'all')
        elif self.sender() == self.tickersCsv:
            subprocess.call('python collect_data.py "shares_dl_csv"', shell=False)
        elif self.sender() == self.blocksCsv:
            subprocess.call('python collect_data.py "blocks_dl_csv"', shell=False)
        elif self.sender() == self.blocksFolder:
            subprocess.call('python collect_data.py "blocks_folder"', shell=False)

    def completerActivated(self):
        self.codeChoosed()

    def editFinished(self):
        if (self.lineEditSticker.hasFocus()):   # 解决触发两次的问题
            self.codeChoosed()

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
                    if (row < 0):
                        row=0
                    if (self.isTableBlocks):
                        if (row >= len(self.blocks)):
                            row -= 1
                        text = self.blocks.values[row][column]
                    else:
                        if (row >= len(self.tickers)):
                            row -= 1
                        text = self.tickers.values[row][column]
                    self.lineEditSticker.setText(text)
                    self.codeChoosed()
        return False

    def tableClicked(self, mi):
        row = mi.row()
        column = mi.column()
        if (column > 1):
            column = 1
        # print (row, column)
        if (self.isTableBlocks):
            text = self.blocks.values[row][column]
        else:
            text = self.tickers.values[row][column]
        self.lineEditSticker.setText(text)
        self.codeChoosed()

    def tableDoubleClicked(self, mi):
        if (self.isTableBlocks):
            block = self.blocks.values[mi.row()]
            if block[0] not in self.index:
                dialog = GuiSub(block, self.kNumber, parent=self)
                dialog.show()
        else:
            pass
            # /////////////////////////显示基本面

    def moreClicked(self):
        code_list = list(self.blocks.code)
        if (self.code in code_list) and (self.code not in self.index.keys()):
            row = code_list.index(self.code)
            dialog = GuiSub(self.blocks.values[row], self.kNumber, parent=self)
            dialog.show()
        else:
            pass
            # //////////////////////显示基本面

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
        self.tableView.pressed.connect(self.sTableClicked)
        self.tableView.doubleClicked.connect(self.sTableDoubleClicked)
        self.tableView.installEventFilter(self) # eventFilter

        # 初始化GUI
        self.setWindowTitle("{} {}".format(self.block_code,self.block_name))
        model = PandasModel(self.stickers)
        self.tableView.setModel(model)
        drawChart(self.graphicsView,self.sfile,name=self.block_name,kNumber=self.spara)

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
                    code = self.stickers.values[row][0]
                    name = self.stickers.values[row][1]
                    if (code != os.path.splitext(os.path.basename(self.sfile))[0]):
                        self.sfile = "{}\\{}.csv".format(os.path.dirname(self.sfile), code)
                        drawChart(self.graphicsView, self.sfile, name=name, kNumber=self.spara)
        return False

    def sTableClicked(self, mi):
        # row = mi.row()
        # column = mi.column()
        # print (row, column)
        code = self.stickers.values[mi.row()][0]
        name = self.stickers.values[mi.row()][1]
        if (code !=  os.path.splitext(os.path.basename(self.sfile))[0]):
            self.sfile = "{}\\{}.csv".format(os.path.dirname(self.sfile), code)
            drawChart(self.graphicsView, self.sfile, name=name, kNumber=self.spara)

    def sTableDoubleClicked(self, mi):
        pass
        # /////////////////////////显示基本面
        # url2 = "http://f10.eastmoney.com/IndustryAnalysis/Index?type=web&code=SH601006#gsgm-0"
        # http://data.eastmoney.com/stockcalendar/601006.html 个股日历, 直接打开网页即可  / 个股解禁等等信息, 多个标签

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui_action = GuiMain()
    gui_action.show()
    sys.exit(app.exec_())
