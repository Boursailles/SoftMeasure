from time import sleep
from PyQt5.QtCore import QObject, pyqtSignal
import numpy as np
from Validate import *
from Interface import *


class SM_QT(QObject):
    finished = pyqtSignal()
    def __init__(self, sm):
        super().__init__()
        self.sm = sm

    
    def meas(self, meas_time, nb_step):
        V = np.zeros_like(nb_step)
        for i in range(nb_step):
            V[i] = self.sm.read_val()
            sleep(meas_time)
        
        self.finished.emit()
        return V


class Progressbar_QT(QObject):
    change_value = pyqtSignal(int)
    finished = pyqtSignal()
    def __init__(self, time):
        self.time = time
        super().__init__()


    def loading(self):
        for i in range(1, self.time + 1):
            sleep(1)
            self.change_value.emit(i)

        self.finished.emit()

    
class Plot_QT(QObject):
    change_value = pyqtSignal(int)
    finished = pyqtSignal()
    def __init__(self):
        super().__init__()

    def add_curve(self):
        for i in range(50):
            sleep(0.1)
            self.change_value.emit(i)
        self.finished.emit()
