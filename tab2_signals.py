import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import numpy as np
import matplotlib.pyplot as plt
from measures import *
from Models import *
import time



class tab2_signals(models):
    def __init__(self, plot, pathEdit2, x_val, y_val, S_val, dB_val, original, x_min, x_max,\
        y_min, y_max, check_fit, fit_choice):
        self.pathEdit2 = pathEdit2
        self.x_val = x_val
        self.y_val = y_val
        self.S_val = S_val
        self.dB_val = dB_val
        self.original = original
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.check_fit = check_fit
        self.fit_choice = fit_choice
        
        self.original.toggled.connect(self.original_button)
        self.check_fit.toggled.connect(self.check_button)
        plot.clicked.connect(self.plot_button)
        
    
    def original_button(self):
        if self.original.isChecked() == True:
            self.x_min.setDisabled(True)
            self.x_max.setDisabled(True)
            self.y_min.setDisabled(True)
            self.y_max.setDisabled(True)
            
        else:
            self.x_min.setDisabled(False)
            self.x_max.setDisabled(False)
            self.y_min.setDisabled(False)
            self.y_max.setDisabled(False)
            
            
    
    def check_button(self):
        if self.check_fit.isChecked() == False:
            self.fit_choice.setDisabled(True)
            
        else:
            self.fit_choice.setDisabled(False)
    
    
    
    def plot_button(self):
        path = self.pathEdit2.text()
        x_text = self.x_val.currentText()
        y_text = self.y_val.currentText()
        dB_text = self.dB_val.currentText()
        if dB_text == 'Intensity':
            S_unit = '[dB]'
        else:
            S_unit = '[deg]'
            
            
        try:
            x_val = np.genfromtxt(path + '/' + x_text + '_values.txt', names=True, delimiter = '\n')
            x_val_name = x_val.dtype.names[0]
            x_val = x_val[x_val_name]
            
            try:
                y_val = np.genfromtxt(path + '/' + y_text + '_values.txt', names=True, delimiter = '\n')
                y_val_name = y_val.dtype.names[0]
                y_val = y_val[y_val_name]
                
                
                try:
                    index = self.S_val.currentIndex()
                    if index == 0:
                        S_index = '/S/S11/' + dB_text + '.txt'
                    elif index == 1:
                        S_index = '/S/S12/' + dB_text + '.txt'
                    elif index == 2:
                        S_index = '/S/S21/' + dB_text + '.txt'
                    else:
                        S_index = '/S/S22/' + dB_text + '.txt'
                
                
                    S_val = np.genfromtxt(path + S_index, delimiter = ',')
                    Y_val, X_val = np.meshgrid(y_val, x_val)
                    
                    s_val = np.ravel(S_val)
    
                    
                    
                    def find_nearest(array, value):
                        array = np.asarray(array)
                        return (np.abs(array - value)).argmin()
                    
                    
                    
                    def goplot(X_val, Y_val, S_val, x_val):
                        self.len_x = len(X_val)
                        self.len_y = len(Y_val[0])


                        S_val_fit = np.ravel(S_val)
                    
                        self.S_min = min(S_val_fit)
                        self.S_max = max(S_val_fit)


                        fig, ax = plt.subplots(figsize=(12, 12))
                        im = ax.pcolormesh(X_val, Y_val, S_val, cmap='hot', vmin=0.8*self.S_min, vmax=1.2*self.S_max,\
                            shading='auto')
                        
                        ax.set_xlabel('Magnetic Field [T]', fontsize=30)
                        ax.set_ylabel('Frequency [GHz]', fontsize=30)
                        
                        cb = plt.colorbar(im, ax=ax, boundaries=np.linspace(self.S_min, self.S_max, 500),\
                            ticks=np.linspace(-2*self.S_min, 0, 11))
                        cb.ax.set_ylabel('S\u2082\u2081 [dB]', rotation=90, size=30, labelpad=10)
                        cb.ax.tick_params(labelsize=30)

                        plt.show()
                            
                                              
                                              
                            
                            
                            
                            
                    def gofit(X_val, Y_val, S_val, x_val):
                        self.len_x = len(X_val)
                        self.len_y = len(Y_val[0])
                        
                        
                        grid_fit = list(zip(np.ravel(X_val), np.ravel(Y_val)))
                        S_val_fit = np.ravel(S_val)
                        
                        self.S_min = min(S_val_fit)
                        self.S21_min = self.S_min
                        self.S_max = max(S_val_fit)
                        
                        S_tick = int(abs(self.S_max - self.S_min)/6)*6 + int(self.S_min)
                        
                        
                        self.search_freq_c(Y_val[0], [S_val[0], S_val[int(self.len_x/2)]])

                        
                        fittor_3D = getattr(self, self.fit_choice.currentText() + '_model_3D')
                        fittor_2D = getattr(self, self.fit_choice.currentText() + '_model_2D')
                        
                        popt, pcov = scp.curve_fit(fittor_3D, grid_fit, S_val_fit,\
                            bounds=(0, 10), maxfev=600)
                        popt = popt[0]
                        
                        
                        fig, ax = plt.subplots()
                        im = ax.pcolormesh(X_val, Y_val, S_val, cmap='hot', vmin=-100, vmax=-20,\
                            shading='auto')
                        
                        ax.set_xlabel('Magnetic Field [T]', fontsize=30)
                        ax.set_ylabel('Frequency [GHz]', fontsize=30)
                        
                        cb = plt.colorbar(im, ax=ax, boundaries=np.linspace(self.S_min, self.S_max, 500),\
                            ticks=np.linspace(-200, 0, 11))
                        cb.ax.set_ylabel('S\u2082\u2081 [dB]', rotation=90, size=30, labelpad=10)
                        cb.ax.tick_params(labelsize=30) 
                        
                        over2 = fittor_2D(X_val[:, 0], popt)
                        ax.plot(X_val[:, 0], over2[0], 'g', X_val[:, 0], over2[1], 'g', X_val[:, 0], over2[2], 'g--',\
                            [X_val[0, 0], X_val[-1, 0]], [over2[3], over2[3]], 'g--', lw=1)
                        
                        ax.arrow(over2[4], over2[3], 0, popt, length_includes_head = True,\
                            linewidth = 0.01, head_width=0.006, head_length=0.2, color='w')
                        ax.arrow(over2[4], over2[3], 0, -popt, length_includes_head = True,\
                            linewidth = 0.01, head_width=0.006, head_length=0.2, color='w')
                        
                        ax.annotate(f'g/\u03C0 = {round(popt, 2)}', (over2[4]+0.01, over2[3]+0.1),\
                            fontsize=30, c='w')
                        
                        ax.annotate(f'f\u209A = {round(over2[3], 2)}', (X_val[0, 0]+1e-3, over2[3]+0.1),\
                            fontsize=30, c='w')
                        
                        ax.annotate('f\u2098', (X_val[0, 0]+1e-3, Y_val[0, -1]-0.5), fontsize=30, c='k')
                        
                        ax.annotate('f\u208A', (-over2[4], over2[3]+0.1+popt), fontsize=30, c='w')
                        
                        ax.annotate('f\u208B', (-over2[4], over2[3]-0.4-popt), fontsize=30, c='w')
                        
                        ax.set_ylim(Y_val[0, 0], Y_val[0, -1])
                        ax.tick_params(axis='both', which='major', labelsize=30)
                        
                        plt.show()
                    
                    
                    
                    
                    
                    
                    
                    
                    if self.original.isChecked() == False:
                        try:
                            ind_x_min = find_nearest(X_val[:, 0], float(self.x_min.text()))
                            try:
                                ind_x_max = find_nearest(X_val[:, 0], float(self.x_max.text()))
                                try:
                                    ind_y_min = find_nearest(Y_val[0], float(self.y_min.text()))
                                    try:
                                        ind_y_max = find_nearest(Y_val[0], float(self.y_max.text()))
                                        
                                        X_val = X_val[ind_x_min: ind_x_max, ind_y_min: ind_y_max]
                                        Y_val = Y_val[ind_x_min: ind_x_max, ind_y_min: ind_y_max]
                                        S_val = S_val[ind_x_min: ind_x_max, ind_y_min: ind_y_max]
                                        
                                          
                                        x_val = x_val[ind_x_min: ind_x_max]
                                        y_val = y_val[ind_y_min: ind_y_max]
                                            
                                        if self.check_fit.isChecked() == False:
                                            goplot(X_val, Y_val, S_val, s_val)
                                               
                                        else:
                                            gofit(X_val, Y_val, S_val, x_val)
                                            
                                        return X_val, Y_val, S_val
                             
                                    except OSError:
                                        QMessageBox.about(self, "Warning", "y<sub>max</sub> is not a number")
                                except OSError:
                                    QMessageBox.about(self, "Warning", "y<sub>min</sub> is not a number")
                            except OSError:
                                QMessageBox.about(self, "Warning", "x<sub>max</sub> is not a number")
                        except OSError:
                                QMessageBox.about(self, "Warning", "x<sub>min</sub> is not a number")
                                    
                    else:
                        if self.check_fit.isChecked() == False:
                            goplot(X_val, Y_val, S_val, s_val)
                                                
                        else:
                            gofit(X_val, Y_val, S_val, x_val)
                        
                                        
            
                except OSError:
                    QMessageBox.about(self, "Warning", self.S_val.currentText() +\
                    '_values.txt file does not exist in the path : ' + path)
                
                
            except OSError:
                QMessageBox.about(self, "Warning", self.y_val.currentText() +\
                '_values.txt file does not exist in the path : ' + path)
               
        except OSError:
            QMessageBox.about(self, "Warning", self.x_val.currentText() +\
                '_values.txt file does not exist in the path : ' + path)
            
        
            
        