from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import importlib

# IMPORTANT VOIR LES CHEMINS POUR OUVRIR LE FICHIER VNA CAR DANS UN SOUS-DOSSIER

###############################################################################
# This program is working with Interface.py file for SoftMeasure.
# It contains useful code allowing to operate the VNA
###############################################################################



class VNA_settings():
    def __init__(self):
        """
        Settings of the VNA which are generalized for any brand
        """

        self.instr = None
        self.widget()


    def widget(self):
        """
        Display of VNA widgets in the graphics interface
        """

        self.VNA_box = QGroupBox('VNA settings')
        self.f_start = QLineEdit()
        self.f_stop = QLineEdit()
        self.nb_point = QSpinBox()
        self.nb_point.setMaximum(10000)
        self.nb_point.setValue(2)
        self.IFBW = QLineEdit()
        # Faire le bouton power: -10, 0, 10
        # Faire le bouton choix du VNA: RS ou Anritsu pour l'instant

        VNA_layout = QGridLayout()

        VNA_layout.addWidget(QLabel('Start [GHz]:'), 0, 0)
        VNA_layout.addWidget(self.f_start, 0, 1)

        VNA_layout.addWidget(QLabel('Stop [GHz]:'), 1, 0)
        VNA_layout.addWidget(self.f_stop, 1, 1)

        VNA_layout.addWidget(QLabel('Values number:'), 2, 0)
        VNA_layout.addWidget(self.nb_point, 2, 1)

        VNA_layout.addWidget(QLabel('IFBW [kHz]:'), 3, 0)
        VNA_layout.addWidget(self.IFBW, 3, 1)

        VNA_layout.addWidget(QLabel('Power[dBm]:'), 4, 0)
        VNA_layout.addWidget(self.power, 4, 1)

        self.VNA_box.setLayout(VNA_layout)


    def connection(self, vna):
        """
        Connection to the chosen VNA (see the linked VNA file)

        ---------
        Parameter:
        vna: str
            File name of the chosen VNA
        """

        self.instr = importlib.__import__('VNA/' + vna.replace(' ', '_')).VNA()

    
    def initialization(self):
        """
        VNA initialization with following parameters (chosen in the interface, see Interface.py):
        self.f_start: Starting frequency
        self.f_stop: Stopping frequency
        self.nb_point: Step number
        self.IFBW: Intermediate Frequency Band Width
        self.power: Signal power
        """

        self.instr.initialization(self.f_start.text(), self.f_stop.text(), self.nb_point.text(), self.IFBW.text(), self.power.text())


    def read_s_param(self):
        """
        Recording of S-parameters in the following dictionaries:
        self.instr.s11
        self.instr.s12
        self.instr.s21
        self.instr.s22

        Each are sorted like:
        self.instr.sij = {'dB': array, 'phase': array}
        """
        
        self.instr.read_s_param()







if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    win = QWidget()
    win.show()
    vna = VNA_settings()
    vna.VNA_connection('RS ZNB40 VNA')
    vna.VNA.initialization()


    sys.exit(app.exec_())

    
                

