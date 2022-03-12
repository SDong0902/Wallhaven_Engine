from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QDialog
import sys
from Download_Engine.downloader import WallHeavenDownloader


class Ui_Dialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setObjectName("Dialog")
        self.resize(413, 250)

        self.gridLayoutWidget = QtWidgets.QWidget(self)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 0, 371, 41))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")

        self.MainTitle = QtWidgets.QLabel(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(24)
        self.MainTitle.setFont(font)
        self.MainTitle.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.MainTitle.setTextFormat(QtCore.Qt.AutoText)
        self.MainTitle.setObjectName("MainTitle")
        self.gridLayout.addWidget(self.MainTitle, 0, 0, 1, 1)

        self.frame = QtWidgets.QFrame(self)
        self.frame.setGeometry(QtCore.QRect(10, 40, 371, 151))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")

        # Start page box UI
        self.startLabel = QtWidgets.QLabel(self.frame)
        self.startLabel.setGeometry(QtCore.QRect(30, 20, 71, 16))
        self.startLabel.setObjectName("startLabel")

        self.startPage = QtWidgets.QSpinBox(self.frame)
        self.startPage.setGeometry(QtCore.QRect(30, 40, 61, 21))
        self.startPage.setMinimum(1)
        self.startPage.setMaximum(500)
        self.startPage.setObjectName("startPage")
        # When start page > end page, update end page to be equal to start page
        self.startPage.valueChanged.connect(self.update_endpage_value)

        # End page box UI
        self.endLabel = QtWidgets.QLabel(self.frame)
        self.endLabel.setGeometry(QtCore.QRect(160, 20, 61, 16))
        self.endLabel.setObjectName("endLabel")

        self.endPage = QtWidgets.QSpinBox(self.frame)
        self.endPage.setGeometry(QtCore.QRect(160, 40, 61, 21))
        self.endPage.setMinimum(1)
        self.endPage.setMaximum(500)
        # End page value should be equal or greater than start page value
        self.endPage.setValue(self.startPage.value())
        self.endPage.setObjectName("endPage")
        # When end page < start page, reduce start page to end page value
        self.endPage.valueChanged.connect(self.update_start_value)

        # "All Pages" checkbox
        self.checkBox = QtWidgets.QCheckBox(self.frame)
        self.checkBox.setGeometry(QtCore.QRect(260, 40, 85, 22))
        self.checkBox.setObjectName("checkBox")
        self.checkBox.stateChanged.connect(lambda: self.checkbox_state())

        # Path box
        self.pathLabel = QtWidgets.QLabel(self.frame)
        self.pathLabel.setGeometry(QtCore.QRect(30, 100, 31, 16))
        self.pathLabel.setObjectName("pathLabel")
        # Path text box
        self.pathText = QtWidgets.QTextEdit(self.frame)
        self.pathText.setGeometry(QtCore.QRect(65, 93, 265, 23))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pathText.setFont(font)
        self.pathText.setObjectName("pathText")
        self.pathText.setReadOnly(True)

        # Save button
        self.saveButton = QtWidgets.QPushButton(self)
        self.saveButton.setGeometry(QtCore.QRect(301, 204, 80, 24))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.saveButton.setFont(font)
        self.saveButton.setObjectName("saveButton")
        self.saveButton.clicked.connect(self.create_downloader)

        # Cancel button
        self.cancelButton = QtWidgets.QPushButton(self)
        self.cancelButton.setGeometry(QtCore.QRect(215, 204, 80, 24))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.cancelButton.setFont(font)
        self.cancelButton.setObjectName("cancelButton")
        self.cancelButton.clicked.connect(self.reject)

        # Browse path button
        self.browsePath = QtWidgets.QPushButton(self.frame)
        self.browsePath.setGeometry(QtCore.QRect(324, 88, 35, 25))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.browsePath.setFont(font)
        self.browsePath.setObjectName("browsePath")
        self.browsePath.clicked.connect(self.show_file_dialog)

        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)

        self.check_path_box()

        self.url = ""

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Save Images"))
        self.MainTitle.setText(_translate("Dialog", "Save Images"))
        self.startLabel.setText(_translate("Dialog", "Start Page"))
        self.endLabel.setText(_translate("Dialog", "End Page"))
        self.pathLabel.setText(_translate("Dialog", "Path:"))
        self.browsePath.setText(_translate("Dialog", "..."))
        self.cancelButton.setText(_translate("Dialog", "Cancel"))
        self.saveButton.setText(_translate("Dialog", "Save"))
        self.checkBox.setText(_translate("Dialog", "All Pages"))

    def show_file_dialog(self):
        selected_dir = QFileDialog.getExistingDirectory(caption='Choose Directory', directory='~/')
        # Get the selected path
        self.pathText.setText(selected_dir)
        # path = self.pathText.toPlainText()
        self.check_path_box()

    def update_endpage_value(self):
        start_value = self.startPage.value()
        end_value = self.endPage.value()

        if start_value > end_value:
            self.endPage.setValue(start_value)

    def update_start_value(self):
        start_value = self.startPage.value()
        end_value = self.endPage.value()

        if end_value < start_value:
            self.startPage.setValue(end_value)

    def checkbox_state(self):

        if self.checkBox.isChecked():
            self.endPage.setEnabled(False)
        else:
            self.endPage.setEnabled(True)

    def check_path_box(self):
        if self.pathText.toPlainText() == '':
            self.saveButton.setEnabled(False)
        else:
            self.saveButton.setEnabled(True)

    def create_downloader(self):
        directory = self.pathText.toPlainText()
        start = self.startPage.value()
        if self.checkBox.isChecked():
            end = -1
        else:
            end = self.endPage.value()

        self.downloader = WallHeavenDownloader(url=self.url, directory=directory, start_page=start, end_page=end)
        print("Downloader created!")
        self.accept()
        self.downloader.start()


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    #Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    #ui.setupUi(Dialog)
    #Dialog.show()
    ui.show()
    sys.exit(app.exec_())
