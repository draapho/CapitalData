# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui_sub.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(850, 450)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Dialog)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.splitter = QtWidgets.QSplitter(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.widget = QtWidgets.QWidget(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setMinimumSize(QtCore.QSize(0, 0))
        self.widget.setObjectName("widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.graphicsView = GraphicsLayoutWidget(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.graphicsView.sizePolicy().hasHeightForWidth())
        self.graphicsView.setSizePolicy(sizePolicy)
        self.graphicsView.setMinimumSize(QtCore.QSize(0, 0))
        self.graphicsView.setObjectName("graphicsView")
        self.verticalLayout.addWidget(self.graphicsView)
        self.widget_2 = QtWidgets.QWidget(self.splitter)
        self.widget_2.setMinimumSize(QtCore.QSize(290, 0))
        self.widget_2.setMaximumSize(QtCore.QSize(690, 16777215))
        self.widget_2.setObjectName("widget_2")
        self.gridLayout = QtWidgets.QGridLayout(self.widget_2)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName("gridLayout")
        self.tableView = QtWidgets.QTableView(self.widget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableView.sizePolicy().hasHeightForWidth())
        self.tableView.setSizePolicy(sizePolicy)
        self.tableView.setMinimumSize(QtCore.QSize(0, 0))
        self.tableView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableView.setObjectName("tableView")
        self.tableView.horizontalHeader().setDefaultSectionSize(40)
        self.tableView.horizontalHeader().setMinimumSectionSize(5)
        self.gridLayout.addWidget(self.tableView, 0, 0, 1, 2)
        self.horizontalLayout.addWidget(self.splitter)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))


from pyqtgraph import GraphicsLayoutWidget


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
