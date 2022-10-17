from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import importlib



###############################################################################
# This program is working with Interface.py file for SoftMeasure.
# It contains useful code allowing to operate the GaussMeter (GM).
###############################################################################



class GM_settings():
    def __init__(self):
        """
        Settings of the GM which are generalized for any brand
        """

        self.instr = None
        self.widget()


    def widget(self):
        """
        Display of GM widgets in the graphics interface
        """

        self.GM_box = QGroupBox('GaussMeter')
        self.unit = QComboBox()
        self.unit.addItems(['G', 'T', 'Oe', 'A.m\u207B\u00B9'])
        self.unit.setCurrentIndex(0)

        GM_layout = QGridLayout()

        GM_layout.addWidget(QLabel('Unit::'), 0, 0)
        GM_layout.addWidget(self.unit, 0, 1)

        self.GM_box.setLayout(GM_layout)


    def connection(self, gm):
        """
        Connection to the chosen GM (see the linked GM file)

        ---------
        Parameter:
        gm: str
            File name of the chosen GM
        """

        self.instr = importlib.__import__('GM/' + gm.replace(' ', '_')).GM()

    
    def initialization(self):
        """
        GM initialization with the following parameter (chosen in the interface, see Interface.py):
        self.unit: Number linked to the magnetic field unit (donner les valeurs)
        """

        self.instr.initialization(self.unit.currentIndex())


    def read_mag_field(self):
        """
        Recording of magnetic field in the variable self.instr.mag_value.
        """
        
        self.instr.read_mag_field()