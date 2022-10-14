import pyvisa as visa
from PyQt5.QtWidgets import *
import numpy as np







class EM_settings():
    def __init__(self):
        """
        Settings of the EM which are generalized for any brand
        """

        self.instr = None
        self.widget()


    def widget(self):
        """
        Display of EM widgets in the graphics interface
        """

        # Voltage settings
        self.EM_box = QGroupBox('EM settings')
            
        self.I_start = QLineEdit()
        self.I_stop = QLineEdit()
        self.nb_point = QSpinBox()
        self.nb_point.setMaximum(10000)
        self.nb_point.setValue(2)
        self.unit = QComboBox()
        self.unit.addItems(['G', 'T', 'Oe', 'A.m\u207B\u00B9'])
        self.unit.setCurrentIndex(1)
            
            
        EM_layout = QGridLayout()
        
        EM_layout.addWidget('Unit:', 0, 0)
        EM_layout.addWidget(self.unit, 0, 1)

        EM_layout.addWidget(QLabel('Start [A]:'), 1, 0)
        EM_layout.addWidget(self.I_start, 1, 1)
            
        EM_layout.addWidget(QLabel('Stop [A]:'), 2, 0)
        EM_layout.addWidget(self.I_stop, 2, 1)
            
        EM_layout.addWidget(QLabel('Values number:'), 3, 0)
        EM_layout.addWidget(self.v_step, 3, 1)
            
        self.EM_box.setLayout(EM_layout)