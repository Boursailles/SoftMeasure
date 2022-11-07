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
import matplotlib.pyplot as plt



class Plot_GUI(QWidget):
    def __init__(self, parent):
        super().__init__()
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


    def S_curve(self, watch_Sfile):
        self.watch_Sfile = watch_Sfile
        self.S_trace, = self.S_plot.graph.axes.plot([], [], 'b')
        self.S_plot.graph.draw()

        
        self.Swatcher = Watcher(watch_Sfile)
        self.Sthread = QThread()

        self.Swatcher.moveToThread(self.Sthread)
        self.Sthread.started.connect(self.Swatcher.watch)

        self.Swatcher.change_value.connect(self.read_Sdata)

        self.Swatcher.finished.connect(self.Sthread.quit)

        self.Swatcher.finished.connect(self.Swatcher.stop_watching)

        self.Swatcher.finished.connect(self.Swatcher.deleteLater)

        self.Swatcher.finished.connect(self.Sthread.deleteLater)

        self.Sthread.start()

    
    def V_curve(self, watch_Vfile):
        self.watch_Vfile = watch_Vfile
        self.V_trace, = self.V_plot.graph.axes.plot([], [], 'r')
        self.V_plot.graph.draw()

        
        self.Vwatcher = Watcher(watch_Vfile)
        self.Vthread = QThread()

        self.Vwatcher.moveToThread(self.Vthread)
        self.Vthread.started.connect(self.Vwatcher.watch)

        self.Vwatcher.change_value.connect(self.read_Vdata)

        self.Vwatcher.finished.connect(self.Vthread.quit)

        self.Vwatcher.finished.connect(self.Vwatcher.stop_watching)

        self.Vwatcher.finished.connect(self.Vwatcher.deleteLater)

        self.Vwatcher.finished.connect(self.Vthread.deleteLater)

        self.Vthread.start()


    def read_Sdata(self):
        data = np.genfromtxt(self.watch_Sfile, names=True)
        self.S_trace.set_data(data['f'], data['S'])
        
        self.S_plot.graph.axes.relim()
        self.S_plot.graph.axes.autoscale_view()
        self.S_plot.graph.draw()

    
    def read_Vdata(self):
        data = np.genfromtxt(self.watch_Vfile, names=True)
        self.V_trace.set_data(data['f'], data['V'])
        self.V_plot.graph.draw()


class Watcher(QObject):
    running = True
    refresh_delay_secs = 1
    change_value = pyqtSignal()
    finished = pyqtSignal()

    # Constructor
    def __init__(self, watch_file):
        super().__init__()
        self._cached_stamp = 0
        self.filename = watch_file

    # Look for changes
    def look(self):
        stamp = os.stat(self.filename).st_mtime
        if stamp != self._cached_stamp:
            self._cached_stamp = stamp
            # File has changed, so do something...
            print('File changed')
            self.change_value.emit()

    # Keep watching in a loop        
    def watch(self):
        while self.running: 
            try: 
                # Look for changes
                sleep(self.refresh_delay_secs) 
                self.look() 
            except KeyboardInterrupt: 
                print('\nDone') 
                break 
            except FileNotFoundError:
                print('File not Found')
                # Action on file not found
                break
            '''except: 
                print('Unhandled error: %s' % sys.exc_info()[0])
                break'''

    def stop_watching(self):
        print('Watch is over')
        self.running = False
        

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