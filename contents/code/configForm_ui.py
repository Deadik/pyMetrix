# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(310, 163)

        self.lblApiKey = QtGui.QLabel(Dialog)
        self.lblApiKey.setGeometry(QtCore.QRect(11, 33, 41, 20))
        self.lblApiKey.setObjectName("lblApiKey")

        self.apiKey = QtGui.QLineEdit(Dialog)
        self.apiKey.setGeometry(QtCore.QRect(80, 30, 171, 24))
        self.apiKey.setObjectName("apiKey")

        self.lblAppId = QtGui.QLabel(Dialog)
        self.lblAppId.setGeometry(QtCore.QRect(11, 63, 41, 20))
        self.lblAppId.setObjectName("lblAppId")

        self.appId = QtGui.QLineEdit(Dialog)
        self.appId.setGeometry(QtCore.QRect(80, 60, 171, 24))
        self.appId.setObjectName("appId")

        self.lblTimer = QtGui.QLabel(Dialog)
        self.lblTimer.setGeometry(QtCore.QRect(11, 93, 41, 20))
        self.lblTimer.setObjectName("lblTimer")

        self.timerCount = QtGui.QSpinBox(Dialog)
        self.timerCount.setGeometry(QtCore.QRect(80, 90, 171, 24))
        self.timerCount.setObjectName("timerCount")
        self.timerCount.setMinimum(10)

        self.lblPeriod = QtGui.QLabel(Dialog)
        self.lblPeriod.setGeometry(QtCore.QRect(11, 123, 41, 20))
        self.lblPeriod.setObjectName("lblPeriod")

        self.period = QtGui.QSpinBox(Dialog)
        self.period.setGeometry(QtCore.QRect(80, 120, 171, 24))
        self.period.setObjectName("period")
        self.period.setMinimum(7)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.lblApiKey.setText(QtGui.QApplication.translate("Dialog", "apiKey:", None, QtGui.QApplication.UnicodeUTF8))
        self.lblAppId.setText(QtGui.QApplication.translate("Dialog", "counterId:", None, QtGui.QApplication.UnicodeUTF8))
        self.lblTimer.setText(QtGui.QApplication.translate("Dialog", "timeout:", None, QtGui.QApplication.UnicodeUTF8))
        self.lblPeriod.setText(QtGui.QApplication.translate("Dialog", "Период:", None, QtGui.QApplication.UnicodeUTF8))