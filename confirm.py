# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'confirm.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Confirm(object):
    def setupUi(self, Confirm):
        Confirm.setObjectName("Confirm")
        Confirm.resize(344, 173)
        self.gridLayout = QtWidgets.QGridLayout(Confirm)
        self.gridLayout.setObjectName("gridLayout")
        self.textBrowser = QtWidgets.QTextBrowser(Confirm)
        self.textBrowser.setObjectName("textBrowser")
        self.gridLayout.addWidget(self.textBrowser, 0, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.OKpushButton = QtWidgets.QPushButton(Confirm)
        self.OKpushButton.setObjectName("OKpushButton")
        self.horizontalLayout.addWidget(self.OKpushButton)
        self.CancelpushButton = QtWidgets.QPushButton(Confirm)
        self.CancelpushButton.setObjectName("CancelpushButton")
        self.horizontalLayout.addWidget(self.CancelpushButton)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)

        self.retranslateUi(Confirm)
        QtCore.QMetaObject.connectSlotsByName(Confirm)

    def retranslateUi(self, Confirm):
        _translate = QtCore.QCoreApplication.translate
        Confirm.setWindowTitle(_translate("Confirm", "Form"))
        self.OKpushButton.setText(_translate("Confirm", "确认"))
        self.CancelpushButton.setText(_translate("Confirm", "取消"))
