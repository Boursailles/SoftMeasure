import sys
from PyQt5.QtCore import * 
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from VNA_settings import *
from PS_settings import *
from GM_settings import *
from SM_settings import *
from Validate import *
from Plot_GUI import *


###############################################################################
# This program is working with VNA_settings.py, PS_settings.py, GM_settings.py, SM_settings.py, and Validate.py files as children for SoftMeasure.
# It contains useful code allowing to display main window.
###############################################################################


class Interface(QWidget):
    def __init__(self):
        """
        Main window of SoftMeasure.
        """

        # Adding of setting instruments tools in the main window.
        self.vna = VNA_settings()
        self.ps = PS_settings()
        self.gm = GM_settings()
        self.sm = SM_settings()
        
        # Main graphic window
        super().__init__()
        self.setWindowTitle('SoftMeasure')
        
        self.layout = QGridLayout()


    def widget_settings(self):
        """
        Placement of setting tools for all instruments.
        """

        self.setting_box = QGroupBox('Settings')
        self.setting_box.setFlat(True)

        setting_layout = QGridLayout()

        setting_layout.addWidget(self.vna.box, 0, 0)
        setting_layout.addWidget(self.ps.box, 0, 1)
        setting_layout.addWidget(self.gm.box, 1, 0)
        setting_layout.addWidget(self.sm.box, 1, 1)

        self.setting_box.setLayout(setting_layout)

        self.layout.addWidget(self.setting_box, 0, 0)
        self.setLayout(self.layout)


    def widget_valid(self):
        """
        Setting tools for the measure.
        """

        self.valid = Valid(self)
        self.valid.widget()

        self.layout.addWidget(self.valid.box, 1, 0)
        self.setLayout(self.layout)





if __name__ == '__main__':
    app = QApplication.instance() 
    if not app:
        app = QApplication(sys.argv)
    
    soft = Interface()
    soft.widget_valid()
    soft.widget_settings()
    soft.show()

    sys.exit(app.exec_())