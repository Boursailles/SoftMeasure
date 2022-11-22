import os
import pyvisa as visa
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QPushButton, QSizePolicy
from PyQt5.QtCore import QObject, QThread, pyqtSignal, Qt
from time import sleep, time
import numpy as np
from Save import *
from Interface import *
from Plot_GUI2_test import *
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as cm



class Valid:
    def __init__(self, xdata):
        self.xdata = xdata
        self.kill = False


    def widget(self):
        self.save = Save()
        self.okay = QPushButton('Okay')
        self.okay.clicked.connect(self.okay_event)

        self.cancel = QPushButton('Close')
        self.cancel.clicked.connect(QCoreApplication.instance().quit)

        self.box = QGroupBox('')
        self.box.setFlat(True)

        self.progressbar = QProgressBar()
        self.progressbar.setVisible(False)
        retainsize = self.progressbar.sizePolicy()
        retainsize.setRetainSizeWhenHidden(True)
        self.progressbar.setSizePolicy(retainsize)

        self.estimated_time = QLabel('Estimated time:')
        self.estimated_time.setVisible(False)
        retainsize = self.estimated_time.sizePolicy()
        retainsize.setRetainSizeWhenHidden(True)
        self.estimated_time.setSizePolicy(retainsize)

        self.display_time = QLabel('')
        self.display_time.setVisible(False)
        retainsize = self.display_time.sizePolicy()
        retainsize.setRetainSizeWhenHidden(True)
        self.display_time.setSizePolicy(retainsize)


        layout = QGridLayout()

        layout.addWidget(self.save.box, 0, 0)
        layout.addWidget(self.okay, 0, 1)
        layout.addWidget(self.cancel, 0, 2)
        layout.addWidget(self.progressbar, 1, 0)
        layout.addWidget(self.estimated_time, 1, 1)
        layout.addWidget(self.display_time, 1, 2)

        self.box.setLayout(layout)


    def okay_event(self):
        self.meas_record(r'C:\Users\Guillaume\Documents\Python\test.txt'.replace('\\', '/'))


    def meas_record(self, file):
        # Create Plot GUI, with V and S graphs
        self.plot_gui = Plot_GUI(1, self.xdata)
        self.plot_gui.V_QT(file)
        self.plot_gui.S_QT(file)

        # Creating the QThread of the SourceMeter
        self.sm_thread = QThread()
        self.sm_qt = SM_QT()
        self.sm_qt.moveToThread(self.sm_thread)

        # When the measurent is done, read recorded data
        self.sm_qt.meas_done.connect(self.plot_gui.Vwatcher.read_Vdata.emit)
        self.sm_qt.meas_loop.connect(self.meas_loop)

        # Laucnh a measurement set
        self.sm_qt.launch_meas.connect(self.sm_qt.meas)
        
        # End of measurements
        self.sm_qt.finished.connect(self.sm_thread.quit)
        self.sm_qt.finished.connect(self.sm_qt.deleteLater)
        self.sm_thread.finished.connect(self.sm_thread.deleteLater)
        
        # Set of colors
        normalize = mcolors.Normalize(vmin=0, vmax=5)
        colormap = cm.jet
        self.colors = [colormap(normalize(n)) for n in range(5)]

        
        # Start sm measurement
        self.sm_thread.start()
        self.meas_loop(0)


    def meas_loop(self, idx):
        print('COUCOU ' + str(idx))
        if idx < 5:
            self.plot_gui.S_curve(self.colors[idx])
            self.plot_gui.V_curve(self.colors[idx])

            self.sm_qt.launch_meas.emit()
            
        else:
            self.sm_thread.quit()
        

        '''self.plot_gui.Swatcher.read_Sdata.emit()'''







class SM_QT(QObject):
    finished = pyqtSignal()
    meas_done = pyqtSignal(str)
    meas_loop = pyqtSignal(int)
    launch_meas = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.idx = 0
    
    def meas(self):
        for i in range(2):
            print(i)
            sleep(1)
            self.meas_done.emit(str(i))

        self.idx += 1
        self.meas_loop.emit(self.idx)
        





if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = QWidget()
    
    xdata = [0, 0.1, 0.2, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5]


    valid = Valid(xdata)
    valid.widget()

    layout = QGridLayout()
    layout.addWidget(valid.box, 0, 0)
    win.setLayout(layout)
    win.show()

    sys.exit(app.exec_())