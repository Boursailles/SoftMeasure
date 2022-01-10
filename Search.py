from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class search(object):
    def __init__(self):
        self.pathEdit2 = QLineEdit(placeholderText='Select path...')
        self.button2 = QToolButton(text='...')
        
        self.button2.clicked.connect(self.selectTarget2)
        

    def selectTarget2(self):
        path = QFileDialog.getExistingDirectory()
        self.pathEdit2.setText(path)
        

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    w = search()
    sys.exit(app.exec_())