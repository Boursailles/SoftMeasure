from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import numpy as np
import matplotlib.pyplot as plt
from Search import *
from tab2_signals import *



class tab2(tab2_signals, search):
    def __init__(self):
        self.tab2 = QWidget()
        
        self.values_box()
        self.plot_box()
        self.Fit_box()
        
        
        self.tab2_layout = QGridLayout()
        
        self.tab2_layout.addWidget(QLabel(''), 0, 0)
        self.tab2_layout.addWidget(self.val_box, 1, 0)
        
        self.tab2_layout.addWidget(self.p_box, 1, 1)
        
        self.tab2_layout.addWidget(QLabel(''), 2, 0)
        self.tab2_layout.addWidget(self.fit_box, 3, 0)
        
        self.plot = QPushButton('Plot')
        self.tab2_layout.addWidget(self.plot, 3, 1)
        
        self.tab2_layout.addWidget(QLabel(''), 4, 0)
        
        self.tab2.setLayout(self.tab2_layout)
        
        
        super().__init__(self.plot, self.pathEdit2, self.x_val, self.y_val, self.S_val, self.dB_val,\
            self.original, self.x_min, self.x_max, self.y_min, self.y_max, self.check_fit, self.fit_choice)
    
    
    
    def values_box(self):
        # Launch settings
        self.val_box = QGroupBox('Values settings')
        
        values_layout = QGridLayout()
        search.__init__(self)
        values_layout.addWidget(QLabel('Directory :'), 0, 0)
        values_layout.addWidget(self.pathEdit2, 0, 1, 1, 2)
        values_layout.addWidget(self.button2, 0, 3)
        
        values_layout.addWidget(QLabel('x-axis :'), 1, 0)
        values_layout.addWidget(QLabel('y-axis :'), 1, 2)
        self.x_val = QComboBox()
        self.x_val.addItems(['H', 'V', 'f'])
        self.y_val = QComboBox()
        self.y_val.addItems(['f', 'V', 'H'])
        values_layout.addWidget(self.x_val, 1, 1)
        values_layout.addWidget(self.y_val, 1, 3)
        
        values_layout.addWidget(QLabel('colored :'), 2, 0)
        self.S_val = QComboBox()
        self.S_val.addItems(['S\u2081\u2081', 'S\u2081\u2082', 'S\u2082\u2081', 'S\u2082\u2082'])
        self.dB_val = QComboBox()
        self.dB_val.addItems(['Intensity', 'Phase'])
        values_layout.addWidget(self.S_val, 2, 1)
        values_layout.addWidget(self.dB_val, 2, 2, 1, 2)
        
        
        self.val_box.setLayout(values_layout)
        
        
    
    def plot_box(self):
        self.p_box = QGroupBox('Plot settings')
        plot_layout = QGridLayout()
        
        nb_group = QButtonGroup() # Number group
        self.original = QRadioButton("Original")
        self.original.setChecked(True)
        nb_group.addButton(self.original)
        self.cropped = QRadioButton("Cropped")
        nb_group.addButton(self.cropped)
        
        self.x_min = QLineEdit()
        self.x_max = QLineEdit()
        
        self.y_min = QLineEdit()
        self.y_max = QLineEdit()
        
        self.x_min.setDisabled(True)
        self.x_max.setDisabled(True)
        self.y_min.setDisabled(True)
        self.y_max.setDisabled(True)
        
        plot_layout.addWidget(self.original, 0, 0)
        plot_layout.addWidget(self.cropped, 0, 1)
        
        plot_layout.addWidget(QLabel('x<sub>min</sub> :'), 1, 0)
        plot_layout.addWidget(self.x_min, 1, 1)
        plot_layout.addWidget(QLabel('x<sub>max</sub> :'), 2, 0)
        plot_layout.addWidget(self.x_max, 2, 1)
        
        plot_layout.addWidget(QLabel('y<sub>min</sub> :'), 3, 0)
        plot_layout.addWidget(self.y_min, 3, 1)
        plot_layout.addWidget(QLabel('y<sub>max</sub> :'), 4, 0)
        plot_layout.addWidget(self.y_max, 4, 1)
        
        self.p_box.setLayout(plot_layout)
        
        
        
    def Fit_box(self):
        self.fit_box = QGroupBox('Fit settings')
        fit_layout = QGridLayout()
            
        self.check_fit = QCheckBox('Fit')
        self.fit_choice = QComboBox()
        self.fit_choice.setDisabled(True)
        self.fit_choice.addItems(['Slab', 'Sphere'])
         
        fit_layout.addWidget(self.check_fit, 0, 0)
        fit_layout.addWidget(self.fit_choice, 0, 1)
            
        self.fit_box.setLayout(fit_layout)