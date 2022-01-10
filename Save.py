from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class save(object):
    def __init__(self, layout):
        self.pathEdit = QLineEdit(placeholderText='Select path...')
        self.button = QToolButton(text='...')
        
        self.button.clicked.connect(self.selectTarget)
        
        layout.addWidget(self.pathEdit)
        layout.addWidget(self.button)
        
        

    def selectTarget(self):
        dialog = QFileDialog()

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
    w = save()
    sys.exit(app.exec_())