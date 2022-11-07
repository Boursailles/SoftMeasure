import sys
import matplotlib
matplotlib.use('Qt5Agg')
from time import sleep
from threading import Timer

import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from VNA_settings import *
from PS_settings import *
from GM_settings import *
from SM_settings import *
from Validate import *
from QThreads import *

from PyQt5.QtWidgets import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure



class Plot_GUI(QWidget):
    def __init__(self, parent, xdata):
        super().__init__()
        self.xdata = xdata
        self.parent = parent
        self.widget()

        layout = QGridLayout()
        layout.addWidget(self.box, 0, 0)
        self.setLayout(layout)
        self.show()


    def widget(self):
        self.box = QGroupBox('Plots')
        self.layout = QGridLayout()

        """if self.parent.ps.box.isChecked():
            self.V_plot = Graph_2D('f [GHz]', 'V [µV]')
            if self.parent.vna.box.isChecked():
                self.S_plot = Graph_2D('f [GHz]', '$S_{21}$ [dB]')

                self.layout.addWidget(self.S_plot, 0, 0)
                self.layout.addWidget(self.V_plot, 1, 0)
                
            else:
                self.layout.addWidget(self.V_plot, 0, 0)

        elif self.parent.vna.box.isChecked():
            self.S_plot = Graph_2D('f [GHz]', '$S_{21}$ [dB]', (0, 5), (-140, -20))
            self.layout.addWidget(self.S_plot, 0, 0)"""
        
        self.S_plot = Graph_2D('f [GHz]', '$S_{21}$ [dB]')
        self.V_plot = Graph_2D('f [GHz]', 'V [µV]')

        self.layout.addWidget(self.S_plot, 0, 0)
        self.layout.addWidget(self.V_plot, 1, 0)
        self.box.setLayout(self.layout)


    def S_QT(self, watch_Sfile):
        self.watch_Sfile = watch_Sfile
        self.Swatcher = Watcher(watch_Sfile)
        self.Sthread = QThread()

        self.Swatcher.moveToThread(self.Sthread)

        self.Swatcher.read_Sdata.connect(self.read_Sdata)

        '''self.Swatcher.finished.connect(self.Sthread.quit)'''

        self.Swatcher.finished.connect(self.Swatcher.deleteLater)

        self.Swatcher.finished.connect(self.Sthread.deleteLater)

        self.Sthread.start()


    def V_QT(self, watch_Vfile):
        self.watch_Vfile = watch_Vfile
        self.Vwatcher = Watcher(watch_Vfile)
        self.Vthread = QThread()

        self.Vwatcher.moveToThread(self.Vthread)

        self.Vwatcher.read_Vdata.connect(self.read_Vdata)

        '''self.Vwatcher.finished.connect(self.Vthread.quit)'''

        self.Vwatcher.finished.connect(self.Vwatcher.deleteLater)

        self.Vwatcher.finished.connect(self.Vthread.deleteLater)

        self.Vthread.start()


    def S_curve(self, color):
        self.S_trace, = self.S_plot.graph.axes.plot([], [], c=color)
        self.S_plot.graph.draw()

        
    def V_curve(self, color):
        self.V_trace, = self.V_plot.graph.axes.plot([], [], c=color)
        self.V_plot.graph.draw()


    def read_Sdata(self):
        ydata = np.genfromtxt(self.watch_Sfile, names=True)

        self.S_trace.set_data(self.xdata[:len(ydata)], ydata)
        self.S_plot.graph.axes.relim()
        self.S_plot.graph.axes.autoscale_view()
        self.S_plot.graph.draw()

    
    def read_Vdata(self, val):
        '''with open(self.watch_Vfile, 'a') as f:
                            f.write(val + '\n')
        '''
        ydata = np.genfromtxt(self.watch_Vfile, names=True)

        self.V_trace.set_data(self.xdata[:len(ydata)], ydata)
        self.V_plot.graph.axes.relim()
        self.V_plot.graph.axes.autoscale_view()
        self.V_plot.graph.draw()



class Watcher(QObject):
    read_Vdata = pyqtSignal(str)
    read_Sdata = pyqtSignal()
    change_color = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, watch_file):
        self.watch_file = watch_file
        super().__init__()


        

class Canva_2D(FigureCanvasQTAgg):
    def __init__(self, width, height, dpi):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(Canva_2D, self).__init__(fig)



class Graph_2D(QWidget):
    def __init__(self, xlabel, ylabel, width=10, height=12, dpi=80):
        super().__init__()
        self.graph = Canva_2D(width=width, height=height, dpi=dpi)
        self.graph.axes.set_xlabel(xlabel)
        self.graph.axes.set_ylabel(ylabel)

        '''self.graph.axes.set_xlim(xlim)
        self.graph.axes.set_ylim(ylim)'''

        # Create toolbar, passing canvas as first parament, parent (self, the MainWindow) as second.
        toolbar = NavigationToolbar(self.graph, self)

        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.graph)

        # Create a placeholder widget to hold our toolbar and canvas.
        self.setLayout(layout)





if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = QWidget()
    

    plot_gui = Plot_GUI(1)

    watch_Sfile = r'C:\Users\guill\OneDrive\Bureau\test.txt'.replace('\\', '/')

    plot_gui.S_curve(watch_Sfile)
    Timer(20, plot_gui.Swatcher.stop_watching).start()
    

   

    sys.exit(app.exec_())