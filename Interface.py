import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from tab1 import *
from tab2 import *



class Interface(QTabWidget, tab1, tab2):
    def __init__(self, parent=None):
        # Main graphic window
        self.app = QApplication.instance() 
        if not self.app:
            self.app = QApplication(sys.argv)
        
        
        super(Interface, self).__init__(parent)
        tab2.__init__(self)
        
        self.addTab(self.tab1,'Measures')
        self.addTab(self.tab2, 'Graphics')
        
        
        
    def apply(self):
        # Launch main window
        self.show()
        sys.exit(self.app.exec_())



x = Interface()
x.apply()