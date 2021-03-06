# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\ui\mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtChart import QChartView


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(500, 200)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setBaseSize(QtCore.QSize(500, 200))
        MainWindow.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        MainWindow.setWindowTitle("ConnTester")
        MainWindow.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.chartWidget = QChartView(self.centralwidget)
        self.chartWidget.setObjectName("chartWidget")
        self.verticalLayout.addWidget(self.chartWidget)
        self.labelsLayout = QtWidgets.QHBoxLayout()
        self.labelsLayout.setObjectName("labelsLayout")
        self.lossLabel = QtWidgets.QLabel(self.centralwidget)
        self.lossLabel.setObjectName("lossLabel")
        self.lossLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.labelsLayout.addWidget(self.lossLabel)
        self.currLabel = QtWidgets.QLabel(self.centralwidget)
        self.currLabel.setObjectName("currLabel")
        self.currLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.labelsLayout.addWidget(self.currLabel)
        self.meanLabel = QtWidgets.QLabel(self.centralwidget)
        self.meanLabel.setObjectName("meanLabel")
        self.meanLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.labelsLayout.addWidget(self.meanLabel)
        self.verticalLayout.addLayout(self.labelsLayout)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        self.lossLabel.setText(_translate("MainWindow", "TextLabel"))
        self.currLabel.setText(_translate("MainWindow", "TextLabel"))
        self.meanLabel.setText(_translate("MainWindow", "TextLabel"))
