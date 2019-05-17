
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import pyqtgraph as pg

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
        return [format(value, '.0e') for value in values]
