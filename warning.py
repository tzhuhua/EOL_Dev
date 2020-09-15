# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'warning.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_warning(object):
    def setupUi(self, warning):
        warning.setObjectName("warning")
        warning.resize(255, 75)
        self.gridLayout = QtWidgets.QGridLayout(warning)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.Warninglabel = QtWidgets.QLabel(warning)
        self.Warninglabel.setObjectName("Warninglabel")
        self.horizontalLayout.addWidget(self.Warninglabel)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)

        self.retranslateUi(warning)
        QtCore.QMetaObject.connectSlotsByName(warning)

    def retranslateUi(self, warning):
        _translate = QtCore.QCoreApplication.translate
        warning.setWindowTitle(_translate("warning", "Warning"))
        self.Warninglabel.setText(_translate("warning", "TextLabel"))
