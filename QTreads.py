from time import sleep
from PyQt5.QtCore import QObject, pyqtSignal
import numpy as np


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
