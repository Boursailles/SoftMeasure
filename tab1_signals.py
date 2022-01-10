import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import numpy as np
import matplotlib.pyplot as plt
from measures import *
import shutil



class tab1_signals(Measures):
    def __init__(self, path, okay, f_start, f_stop, f_point, IFBW, v_start, v_stop, v_step, mag_unit,\
        initialize, loading, end):
        self.f_start = f_start
        self.f_stop = f_stop
        self.f_point = f_point
        self.IFBW = IFBW
        self.v_start = v_start
        self.v_stop = v_stop
        self.v_step = v_step
        self.mag_unit = mag_unit
        self.path = path
        self.end = end
        
        okay.clicked.connect(self.okay_button)
    
    
    def okay_button(self):
        try:
            param1 = float(self.f_start.text())
            try:
                param2 = float(self.f_stop.text())
                try:
                    param3 = int(self.f_point.text())
                    try:
                        param4 = float(self.IFBW.text())
                        try:
                            param5 = float(self.v_start.text())
                            try:
                                param6 = float(self.v_stop.text())
                                try:
                                    param7 = float(self.v_step.text())
        
        
                                    params = [[self.f_start.text(), self.f_stop.text(), self.f_point.text(),\
                                        self.IFBW.text(), self.v_start.text(), self.v_stop.text(),\
                                            self.v_step.text(), self.mag_unit.currentIndex()]]
                                    
                                    np.savetxt(os.getcwd()+'/parameters', params,\
                                        header='f_start, f_stop, f_point, IFBW, v_start,'+\
                                        'v_stop, v_step, mag_unit', fmt='%s')
                                    
                                    
                                    super().__init__(*params[0])
                                    
                                    
                                    path = self.path.text()
                                    try:
                                        os.makedirs(path)
                                        self.lets_go(path)
                                        
                                    except FileExistsError:
                                        self.lets_go(path)
                                    
                                    except FileNotFoundError:
                                        QMessageBox.about(self, "Warning", "Please, choose a directory path")
                                        if self.address_gauss == None:
                                            QMessageBox.about(self, "Warning",\
                                                "Connection issue with Gaussmeter")
                                            
                                        if self.address_mag == None:
                                            QMessageBox.about(self, "Warning", "Connection issue with Kikusui")
        
        
                                except ValueError:
                                    QMessageBox.about(self, "Warning", "v<sub>step</sub> is not a number")
                            except ValueError:
                                QMessageBox.about(self, "Warning", "v<sub>stop</sub> is not a number")
                        except ValueError:
                            QMessageBox.about(self, "Warning", "v<sub>start</sub> is not a number")
                    except ValueError:
                        QMessageBox.about(self, "Warning", "IFBW is not an integer")    
                except ValueError:
                    QMessageBox.about(self, "Warning", "f<sub>point</sub> is not an integer")
            except ValueError:
                QMessageBox.about(self, "Warning", "f<sub>start</sub> is not a number")
        except ValueError:
            QMessageBox.about(self, "Warning", "f<sub>start</sub> is not a number")
        
        
        
        
        
    def lets_go(self, path):
        if self.address_gauss and self.address_mag and self.vna:
            
            self.initialize()  
            
            try:
                os.makedirs(path + '/S')
                os.makedirs(path + '/S/S11')
                os.makedirs(path + '/S/S12')
                os.makedirs(path + '/S/S21')
                os.makedirs(path + '/S/S22')
                os.makedirs(path + '/S/wrt_H')
                                        
            except FileExistsError:
                shutil.rmtree(path + '/S/wrt_H')
                os.makedirs(path + '/S/wrt_H')
            
                    
            
            with open(path + '/H_values.txt', 'w') as f:
                f.write('Magnetic Field cg' + self.mag_unit.currentText() + 'cd\n')
              
            
            for i, val in enumerate(self.v_list):
                
                if i != 0:
                    How_to_write = 'a'
                else:
                    How_to_write = 'w'
                
                self.loading(i)
                    
                self.S[i], self.H[i] = self.getData(val)
                
                with open(path + '/S/S11/Intensity.txt', How_to_write) as f:
                    f.write(str([val[0] for val in self.S[i][0]])[1: -1] + '\n')
                    
                with open(path + '/S/S11/Phase.txt', How_to_write) as f:
                    f.write(str([val[1] for val in self.S[i][0]])[1: -1] + '\n')

                    
                    
                with open(path + '/S/S12/Intensity.txt', How_to_write) as f:
                    f.write(str([val[0] for val in self.S[i][1]])[1: -1] + '\n')
                    
                with open(path + '/S/S12/Phase.txt', How_to_write) as f:
                    f.write(str([val[1] for val in self.S[i][1]])[1: -1] + '\n')
                    
                    
                with open(path + '/S/S21/Intensity.txt', How_to_write) as f:
                    f.write(str([val[0] for val in self.S[i][2]])[1: -1] + '\n')
                    
                with open(path + '/S/S21/Phase.txt', How_to_write) as f:
                    f.write(str([val[1] for val in self.S[i][2]])[1: -1] + '\n')
                
                    
                with open(path + '/S/S22/Intensity.txt', How_to_write) as f:
                    f.write(str([val[0] for val in self.S[i][3]])[1: -1] + '\n')
                    
                with open(path + '/S/S22/Phase.txt', How_to_write) as f:
                    f.write(str([val[1] for val in self.S[i][3]])[1: -1] + '\n')
                
                
                with open(path + '/H_values.txt', 'a') as f:
                    f.write(self.H[i]+ '\n')
                    
                    
                with open(path + '/S/wrt_H/' + self.H[i] + '.txt', 'w') as f:
                    f.write('S11 cgdBcd, S11 cgdegcd, S12 cgdBcd, S12 cgdegcd, S21 cgdBcd, S21 cgdegcd, \
S22 cgdBcd, S22 cgdegcd \n')
                    for j in range(len(self.S[i][0])):
                        f.write(str(self.S[i][0][j][0]) + ' ' + str(self.S[i][0][j][1]) + ' ' +\
                            str(self.S[i][1][j][0]) + ' ' + str(self.S[i][0][j][1]) + ' ' +\
                            str(self.S[i][2][j][0]) + ' ' + str(self.S[i][2][j][1]) + ' ' +\
                            str(self.S[i][3][j][0]) + ' ' + str(self.S[i][3][j][1]) + '\n')
                
                
            with open(path + '/f_values.txt', 'w') as f:
                f.write('Frequency cgGHzcd\n')
                for val in self.freq:
                    f.write(str(val*1e-9) + '\n')
                    
                    
            with open(path + '/V_values.txt', 'w') as f:
                f.write('Voltage cgVcd\n')
                for val in self.v_list:
                    f.write(str(val) + '\n')
                
                
            self.end()
                
            self.reset()
        
        
        else:
            if self.address_gauss == None:
                QMessageBox.about(self, "Warning", "Connection issue with Gaussmeter")
                
            if self.address_mag == None:
                QMessageBox.about(self, "Warning", "Connection issue with Kikusui")