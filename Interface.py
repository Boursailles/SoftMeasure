import sys
import os
import pyvisa as visa
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from VNA_settings import *
from PS_settings import *
from GM_settings import *

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Launch'))
from Save import *



class Interface(QWidget):
    def __init__(self):
        # Main graphic window
        QWidget.__init__(self)
        self.setWindowTitle('SoftMeasure')

        # For now it is just a test
        self.kill = False

        layout = QGridLayout()

        # Settings display
        self.widget_settings()
        layout.addWidget(self.setting_box, 0, 0)

        # Launch display
        self.widget_launch()
        layout.addWidget(self.launch_box, 1, 0)

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


    def widget_launch(self):
        self.buttons()

        self.launch_box = QGroupBox('')
        self.launch_box.setFlat(True)

        launch_layout = QGridLayout()

        launch_layout.addWidget(self.save.box, 0, 0)
        launch_layout.addWidget(self.okay, 0, 1)
        launch_layout.addWidget(self.cancel, 0, 2)

        self.launch_box.setLayout(launch_layout)


    def buttons(self):
        self.save = Save()
        self.okay = QPushButton('Okay')
        self.okay.clicked.connect(self.okay_event)

        self.cancel = QPushButton('Close')
        self.cancel.clicked.connect(self.close)


    def okay_event(self):
        self.connection()
        if self.kill:
            self.kill = False
            return
        
        self.initialization()
        if self.kill:
            self.kill = False
            return


    def folder(self, path):

        # Creating parent folder.
        try:
            os.makedirs(s)
        except FileExistsError:
            pass

        if self.vna.box.isChecked:
            # Creating S and Sij folders if they did not exist.
            s_path = os.path.join(path, 'S')
            try:
                os.makedirs(s_path)
            except FileExistsError:
                pass
                
            sij = ('S11', 'S12', 'S21', 'S22')
            for s in sij:
                try:
                    os.makedirs(os.path.join(s_path, s))
                except FileExistsError:
                    continue
        
        if self.ps.box.isChecked:
            # Creating current file.
            with open(os.path.join(path, 'I_values.txt'), 'w') as f:
                f.write('Current [A]\n')

        if self.gm.box.isChecked:
            # Creating magnetic field file.
            with open(os.path.join(path, 'H_values.txt'), 'w') as f:
                f.write('Magnetic Field cg' + self.gm.unit.currentText() + 'cd\n')


    def connection(self):
        self.rm = visa.ResourceManager()

        if self.vna.box.isChecked:
            try:
                self.vna.connection(self.rm)
            
            except:
                # Search how and when to put it
                return self.msg_error('VNA')

        if self.ps.box.isChecked:
            try:
                self.ps.connection(self.rm)

            except:
                return self.msg_error('PS')

        if self.gm.box.isChecked:
            try:
                self.gm.connection(self.rm)

            except:
                return self.msg_error('GM')

        # Possibility to have last_status?
        '''if self.ps.box.isChecked:
            try:
                self.ps.connection(self.rm)

            except visa.VisaIOError as e:
                QMessageBox.about(self, "Warning", "Connection issue with electromagnet\nError Codes: " + self.rm.last_status+"\t" + self.rm.visalib.last_status)

        if self.gm.box.isChecked:
            try:
                self.gm.connection(self.rm)

            except visa.VisaIOError as e:
                QMessageBox.about(self, "Warning", "Connection issue with gaussmeter\nError Codes: " + self.rm.last_status+"\t" + self.rm.visalib.last_status)'''


    def initialization(self):
        if self.vna.box.isChecked:
            try:
                self.vna.initialization()
            except:
                return self.msg_error('VNA')

        if self.ps.box.isChecked:
            try:
                self.ps.initialization()
            except:
                return self.msg_error('PS')

        if self.gm.box.isChecked:
            try:
                self.gm.initialization()
            except:
                # If vna and/or ps are connected, then put them off.
                self.off()
                return self.msg_error('GM')
        

    def msg_error(self, device):
        if device == 'VNA':
            word = 'VNA'
        elif device == 'PS':
            word = 'power supply'
        elif device == 'GM':
            word = 'gaussmeter'

        self.kill = True

        QMessageBox.about(self, 'Warning', f'Connection issue with {word}.')
        

    def off(self):
        if self.vna.box.isChecked:
            self.vna.off()

        if self.ps.box.isChecked:
            self.ps.off()



if __name__ == '__main__':
    app = QApplication.instance() 
    if not app:
        app = QApplication(sys.argv)
        
    soft = Interface()
    soft.show()

    sys.exit(app.exec_())