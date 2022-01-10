import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import numpy as np
import matplotlib.pyplot as plt
from measures import *
from Models import *
import time
from QLed import QLed



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
                    
                    
                    
                    def goplot(X_val, Y_val, S_val, s_val):
                            min_S = min(s_val)
                            max_S = max(s_val)
                            
                            plt.ion()
                            
                            fig, ax = plt.subplots()

                            im = ax.pcolormesh(X_val, Y_val, S_val, cmap='hot', vmin=min_S+60,\
                                vmax=max_S+20, shading='auto')
                            ax.set_xlabel(x_val_name.replace('_', ' ').replace('cg', '[').replace('cd', ']'))
                            ax.set_ylabel(y_val_name.replace('_', ' ').replace('cg', '[').replace('cd', ']'))
                            cb = plt.colorbar(im, ax=ax, boundaries=np.linspace(min_S, max_S, 500))
                            cb.set_label(self.S_val.currentText() + ' ' + S_unit)
                            """fig.canvas.draw()
                            fig.canvas.flush_events()
                            time.sleep(2)
                            
                            cb.remove()
                            cb = plt.colorbar(im, ax=ax, boundaries=np.linspace(-0.2, 0.1, 500))
                            cb.set_label(self.S_val.currentText() + ' ' + S_unit)"""
                            fig.canvas.draw()
                            
                                              
                                              
                            
                            
                            
                            
                    def gofit(X_val, Y_val, S_val, x_val):
                        self.len_x = len(X_val)
                        self.len_y = len(Y_val[0])
                        
                        index_c1 = np.where(S_val[0] == max(S_val[0]))
                        index_c2 = np.where(S_val[-1] == max(S_val[-1]))
                        print(Y_val[0, index_c1][0, 0])
                        self.freq_c = (Y_val[0, index_c1][0, 0] + Y_val[-1, index_c2][0, 0])/2
                        print(self.freq_c)
                        
                        grid_fit = list(zip(np.ravel(X_val), np.ravel(Y_val)))
                        S_val_fit = np.ravel(S_val)
                        self.S_min = min(S_val_fit)
                        self.S_max = max(S_val_fit)
                        
                        fittor_3D = getattr(self, self.fit_choice.currentText() + '_model_3D')
                        fittor_2D = getattr(self, self.fit_choice.currentText() + '_model_2D')
                        
                        popt, pcov = scp.curve_fit(fittor_3D, grid_fit, S_val_fit,\
                            bounds=(1e-3, self.freq_c/2), p0=1, maxfev=800)
                    
                        print(popt)
                        grid_fit = np.array(list(zip(np.ravel(X_val), np.ravel(Y_val))))
                        fig, ax = plt.subplots(2, 1)

                        im = ax[0].pcolormesh(X_val, Y_val, S_val, cmap='hot', vmin=self.S_min+60,\
                            vmax=self.S_max+20, shading='auto')
                        ax[0].set_xlabel(x_val_name.replace('_', ' ').replace('cg', '[').replace('cd', ']'))
                        ax[0].set_ylabel(y_val_name.replace('_', ' ').replace('cg', '[').replace('cd', ']'))
                        cb = plt.colorbar(im, ax=ax[0], boundaries=np.linspace(self.S_min, self.S_max, 500))
                        cb.ax.set_title(self.S_val.currentText() + ' ' + S_unit)
                        
                        
                        im = ax[1].pcolormesh(X_val, Y_val, fittor_3D(grid_fit, popt[0]).\
                            reshape(len(X_val), len(Y_val[0])),\
                            cmap='hot', vmin=self.S_min+60, vmax=self.S_max+20, shading='auto')
                        ax[1].set_xlabel(x_val_name.replace('_', ' ').replace('cg', '[').replace('cd', ']'))
                        ax[1].set_ylabel(y_val_name.replace('_', ' ').replace('cg', '[').replace('cd', ']'))
                        cb = plt.colorbar(im, ax=ax[1], boundaries=np.linspace(self.S_min, self.S_max, 500))
                        cb.ax.set_title(self.S_val.currentText() + ' ' + S_unit)

                        plt.show()
                    
                    
                        fig, ax = plt.subplots()
                        im = ax.pcolormesh(X_val, Y_val, S_val, cmap='hot',\
                            vmin=self.S_min+60, vmax=self.S_max+20, shading='auto')
                        ax.set_xlabel(x_val_name.replace('_', ' ').replace('cg', '[').replace('cd', ']'))
                        ax.set_ylabel(y_val_name.replace('_', ' ').replace('cg', '[').replace('cd', ']'))
                        cb = plt.colorbar(im, ax=ax, boundaries=np.linspace(self.S_min, self.S_max, 500))
                        cb.ax.set_title('S\u2082\u2081 [dB]')

                        over = fittor_2D(x_val, popt[0])
                        ax.plot(x_val, over[0], 'b', x_val, over[1], 'b', x_val, over[2], 'b--',\
                            [x_val[0], x_val[-1]], [over[3], over[3]], 'b--',lw=0.5)
                        
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
            
        
            
        