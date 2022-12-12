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



###############################################################################
# This program is working with Interface.py file for SoftMeasure.
# It contains useful code allowing to display measurements in live.
###############################################################################



class Plot_GUI(QWidget):
    def __init__(self, parent):
        """
        New window integrating plots.
        """

        super().__init__()
        self.parent = parent
        self.xdata = []
        self.widget()

        layout = QGridLayout()
        layout.addWidget(self.box, 0, 0)
        self.setLayout(layout)
        self.show()


    def widget(self):
        """
        Display of plot frame windgets.
        """

        self.box = QGroupBox('Plots')
        layout = QGridLayout()

        if self.parent.vna.box.isChecked():
            # Adding of the VNA plot
            self.xdata = np.linspace(float(self.parent.vna.f_start.text()), float(self.parent.vna.f_stop.text()), int(self.parent.vna.nb_step.text()))
            self.S_plot = Graph_2D('f [GHz]', '$S_{21}$ [dB]')
            layout.addWidget(self.S_plot, 0, 0)

            if self.parent.sm.box.isChecked():
                # Adding of the SM plot
                self.V_plot = Graph_2D('f [GHz]', '$V_{iSHE}$ [µV]')
                layout.addWidget(self.V_plot, 1, 0)

        elif self.parent.ps.box.isChecked() and self.parent.sm.box.isChecked():
            # Adding of the SM plot
            self.xdata = np.linspace(float(self.parent.ps.I_start.text()), float(self.parent.ps.I_stop.text()), int(self.parent.ps.nb_step.text()))
            self.V_plot = Graph_2D('f [GHz]', '$V_{iSHE}$ [µV]')
            layout.addWidget(self.V_plot, 0, 0)

        self.box.setLayout(layout)


    def S_QT(self, watch_Sfile):
        """
        Qthread bound to the reading of the S21 file.

        ---------
        Parameter:
        watch_Sfile: class
        """

        self.watch_Sfile = watch_Sfile
        self.Swatcher = Watcher(watch_Sfile)
        self.Sthread = QThread()

        self.Swatcher.moveToThread(self.Sthread)
        self.Swatcher.read_data.connect(self.read_Sdata)
        self.Swatcher.finished.connect(self.Sthread.quit)
        self.Swatcher.finished.connect(self.Swatcher.deleteLater)
        self.Swatcher.finished.connect(self.Sthread.deleteLater)

        self.Sthread.start()


    def V_QT(self, watch_Vfile):
        """
        Qthread bound to the reading of the V file.

        ---------
        Parameter:
        watch_Vfile: class
        """

        self.watch_Vfile = watch_Vfile
        self.Vwatcher = Watcher(watch_Vfile)
        self.Vthread = QThread()

        self.Vwatcher.moveToThread(self.Vthread)
        self.Vwatcher.read_data.connect(self.read_Vdata)
        self.Vwatcher.finished.connect(self.Vthread.quit)
        self.Vwatcher.finished.connect(self.Vwatcher.deleteLater)
        self.Vwatcher.finished.connect(self.Vthread.deleteLater)

        self.Vthread.start()


    def S_curve(self, color):
        """
        Create new trace for S.

        ---------
        Parameter:
        color: tuple
        """

        self.S_trace, = self.S_plot.graph.axes.plot([], [], c=color, marker='o')
        self.S_plot.graph.draw()

        
    def V_curve(self, color):
        """
        Create new trace for V.

        ---------
        Parameter:
        color: tuple
        """

        self.V_trace, = self.V_plot.graph.axes.plot([], [], c=color, marker='o')
        self.V_plot.graph.draw()


    def read_Sdata(self, idx):
        """
        Event function to trace S when Sfile is modified.

        ---------
        Parameter:
        idx: int
            idx of the last index value in the last row in the Sfile
        """

        ydata = np.genfromtxt(self.watch_Sfile, skip_header=1)
        ydata = ydata[idx*len(self.xdata):]

        self.S_trace.set_data(self.xdata[:len(ydata)], ydata)
        self.S_plot.graph.axes.relim()
        self.S_plot.graph.axes.autoscale_view()
        self.S_plot.graph.draw()

    
    def read_Vdata(self, idx):
        """
        Event function to trace V when Vfile is modified.

        ---------
        Parameter:
        idx: int
            idx of the last index value in the last row in the Vfile
        """
        
        ydata = np.genfromtxt(self.watch_Vfile, skip_header=1)
        
        try:
            ydata = ydata[idx*len(self.xdata):]
            self.V_trace.set_data(self.xdata[:len(ydata)], ydata)
            self.V_plot.graph.axes.relim()
            self.V_plot.graph.axes.autoscale_view()
            self.V_plot.graph.draw()
        
        except TypeError:
            self.V_trace.set_data(self.xdata[0], ydata)

        except IndexError:
            self.V_trace.set_data(self.xdata[0], ydata)



class Watcher(QObject):
    read_data = pyqtSignal(int)
    change_color = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, watch_file):
        """
        Watch targeted file.

        ---------
        Parameter:
        watch_file: str
            Path of the targeted file
        """

        self.watch_file = watch_file
        super().__init__()


class Canva_2D(FigureCanvasQTAgg):
    def __init__(self, width, height, dpi):
        """
        Plot frame.

        ---------
        Parameter:
        width: float
        
        height: float

        dpi: int
        """

        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(Canva_2D, self).__init__(fig)


class Graph_2D(QWidget):
    def __init__(self, xlabel, ylabel, width=10, height=12, dpi=80):
        super().__init__()
        """
        Graph creation in a frame.

        ---------
        Parameter:
        xlabel: str

        ylabel: str

        width: float

        height: float

        dpi: int
        """

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