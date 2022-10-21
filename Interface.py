import sys
import os
import pyvisa as visa
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import numpy as np
from VNA_settings import *
from PS_settings import *
from GM_settings import *
from Validate import *



class Interface(QWidget):
    def __init__(self):
        self.vna = None
        self.ps = None
        self.gm = None

        # Main graphic window
        super().__init__()
        self.setWindowTitle('SoftMeasure')
        

        layout = QGridLayout()

        # Settings display
        self.widget_settings()
        layout.addWidget(self.setting_box, 0, 0)

        # Validation display
        self.widget_valid()
        layout.addWidget(self.valid.box, 1, 0)

        self.setLayout(layout)


    def widget_settings(self):
        self.vna = VNA_settings()
        self.ps = PS_settings()
        self.gm = GM_settings()

        self.setting_box = QGroupBox('Settings')
        self.setting_box.setFlat(True)

        setting_layout = QGridLayout()

        setting_layout.addWidget(self.vna.box, 0, 0)
        setting_layout.addWidget(self.ps.box, 0, 1)
        setting_layout.addWidget(self.gm.box, 1, 0)

        self.setting_box.setLayout(setting_layout)


    def widget_valid(self):
        self.valid = Valid(self, self.vna, self.ps, self.gm)





if __name__ == '__main__':
    app = QApplication.instance() 
    if not app:
        app = QApplication(sys.argv)
    
    soft = Interface()
    soft.show()

    sys.exit(app.exec_())