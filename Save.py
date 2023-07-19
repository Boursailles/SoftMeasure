from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *



###############################################################################
# This program permits to get the path of a directory, existing or not.
# It comes from the answer in a forum:
# https://stackoverflow.com/questions/64355895/choose-directory-to-create-directory-in-pyqt5
###############################################################################



class Save(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.box = QGroupBox()
        self.box.setStyleSheet('QGroupBox {  border: none;}')
        
        layout = QGridLayout()

        self.pathEdit = QLineEdit(placeholderText='Select path...')
        self.button = QToolButton(text='...')

        layout.addWidget(self.pathEdit, 0, 0)
        layout.addWidget(self.button, 0, 1)

        self.button.clicked.connect(self.selectTarget)

        self.box.setLayout(layout)


    def selectTarget(self):
        dialog = QFileDialog(self)

        if self.pathEdit.text():
            dialog.setDirectory(self.pathEdit.text())

        dialog.setFileMode(dialog.Directory)

        # we cannot use the native dialog, because we need control over the UI
        options = dialog.Options(dialog.DontUseNativeDialog | dialog.ShowDirsOnly)
        dialog.setOptions(options)

        def checkLineEdit(path):
            if not path:
                return
            if path.endswith(QDir.separator()):
                return checkLineEdit(path.rstrip(QDir.separator()))
            path = QFileInfo(path)
            if path.exists() or QFileInfo(path.absolutePath()).exists():
                button.setEnabled(True)
                return True

        # get the "Open" button in the dialog
        button = dialog.findChild(QDialogButtonBox).button(
            QDialogButtonBox.Open)

        # get the line edit used for the path
        lineEdit = dialog.findChild(QLineEdit)
        lineEdit.textChanged.connect(checkLineEdit)

        # override the existing accept() method, otherwise selectedFiles() will 
        # complain about selecting a non existing path
        def accept():
            if checkLineEdit(lineEdit.text()):
                # if the path is acceptable, call the base accept() implementation
                QDialog.accept(dialog)
        dialog.accept = accept

        if dialog.exec_() and dialog.selectedFiles():
            path = QFileInfo(dialog.selectedFiles()[0]).absoluteFilePath()
            self.pathEdit.setText(path)





if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    w = Save()
    w.show()

    sys.exit(app.exec_())