import sys
import matplotlib
matplotlib.use('Qt5Agg')
from time import sleep

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



class plot_gui:
    def __init__(self, parent):
        self.parent = parent


    def widget(self):
        self.box = QGroupBox('Plots')
        self.layout = QGridLayout()

        """if self.parent.ps.box.isChecked():
            self.V_plot = Graph_2D('f [GHz]', 'V [µV]', (0, 5), (0, 100))
            if self.parent.vna.box.isChecked():
                self.S_plot = Graph_2D('f [GHz]', '$S_{21}$ [dB]', (0, 5), (-140, -20))

                self.layout.addWidget(self.S_plot, 0, 0)
                self.layout.addWidget(self.V_plot, 1, 0)
                
            else:
                self.layout.addWidget(self.V_plot, 0, 0)

        elif self.parent.vna.box.isChecked():
            self.S_plot = Graph_2D('f [GHz]', '$S_{21}$ [dB]', (0, 5), (-140, -20))
            self.layout.addWidget(self.S_plot, 0, 0)"""

        self.S_plot = Graph_2D('f [GHz]', '$S_{21}$ [dB]', (0, 5), (-140, -20))
        self.V_plot = Graph_2D('f [GHz]', 'V [µV]', (0, 5), (0, 100))

        self.S_plot.graph.axes.plot(np.linspace(0, 5, 101), np.linspace(-140, -100, 101))
        self.V_plot.graph.axes.plot(np.linspace(0, 5, 101), np.linspace(-2, 200, 101))

        self.layout.addWidget(self.S_plot, 0, 0)
        self.layout.addWidget(self.V_plot, 1, 0)
        self.box.setLayout(self.layout)


    def S_curve(self, data):
        self.S_trace, = self.S_plot.graph.axes.plot([], [], 'r')
        self.S_plot.graph.draw()

        self.thread = QThread()
        self.plot_qt = Plot_QT()

        self.plot_qt.moveToThread(self.thread)
        self.thread.started.connect(self.plot_qt.add_curve)

        self.plot_qt.change_value.connect(self.test)

        self.plot_qt.finished.connect(self.thread.quit)

        self.plot_qt.finished.connect(self.plot_qt.deleteLater)

        self.plot_qt.finished.connect(self.thread.deleteLater)

        self.x = np.linspace(0, 5, 50)
        self.y = np.linspace(-140, -20, 50)

        self.thread.start()


    def test(self, i):
        self.S_trace.set_data(self.x[:i+1], self.y[:i+1])
        self.S_plot.graph.draw()


class Canva_2D(FigureCanvasQTAgg):
    def __init__(self, width, height, dpi):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(Canva_2D, self).__init__(fig)


class Graph_2D(QWidget):
    def __init__(self, xlabel, ylabel, xlim, ylim, width=10, height=12, dpi=80):
        super().__init__()
        self.graph = Canva_2D(width=width, height=height, dpi=dpi)
        self.graph.axes.set_xlabel(xlabel)
        self.graph.axes.set_ylabel(ylabel)

        self.graph.axes.set_xlim(xlim)
        self.graph.axes.set_ylim(ylim)

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
    

    plot_gui = plot_gui(1)
    plot_gui.widget()

    layout = QGridLayout()
    layout.addWidget(plot_gui.box, 0, 0)
    win.setLayout(layout)
    win.show()
    plot_gui.S_curve(1)


    sys.exit(app.exec_())