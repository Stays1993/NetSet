from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(642, 475)
        self.listWidget = QtWidgets.QListWidget(parent=Form)
        self.listWidget.setGeometry(QtCore.QRect(100, 40, 371, 311))
        self.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.MultiSelection)
        self.listWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.listWidget.setViewMode(QtWidgets.QListView.ViewMode.IconMode)
        self.listWidget.setWordWrap(True)
        self.listWidget.setObjectName("listWidget")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
