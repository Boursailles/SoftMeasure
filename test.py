import sys
import matplotlib
matplotlib.use('Qt5Agg')
from threading import Timer
import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from Validate import *
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import random



###############################################################################
# This program is working with Interface.py and Validate.py files as parents for SoftMeasure.
# It contains useful code allowing to display measurement in live.
###############################################################################



class Plot_GUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('SoftMeasure')
        self.xdata = []
        self.widget()

        layout = QGridLayout()
        layout.addWidget(self.box, 0, 0)
        self.setLayout(layout)
        self.show()

    def widget(self):
        self.box = QGroupBox('Plots')
        layout = QGridLayout()

        self.xdata = np.linspace(1, 10, 101)
        self.S_plot = Graph_2D('f [GHz]', '$S_{21}$ [dB]')
        layout.addWidget(self.S_plot, 0, 0)

        self.V_plot = Graph_2D('f [GHz]', '$V_{iSHE}$ [µV]')
        layout.addWidget(self.V_plot, 1, 0)
        self.box.setLayout(layout)

    def S_curve(self):
        self.S_trace, = self.S_plot.graph.axes.plot([], [], c='r', marker='o')
        self.S_plot.graph.draw()

    def V_curve(self):
        self.V_trace = self.V_plot.graph.axes.errorbar([], [], [], c='b', marker='o')
        self.V_plot.graph.draw()

    def read_Sdata(self):
        ydata = np.random.rand(len(self.xdata))
        self.S_trace.set_data(self.xdata, ydata)
        
        self.S_plot.graph.axes.relim()
        self.S_plot.graph.axes.autoscale_view()
        self.S_plot.graph.draw()

    def read_Vdata(self):
        ydata = np.random.rand(len(self.xdata))
        Dydata = np.random.rand(len(self.xdata))
        self.update_errorbar(self.V_trace, self.xdata, ydata, None, Dydata)

        self.V_plot.graph.axes.relim()
        self.V_plot.graph.axes.autoscale_view()
        self.V_plot.graph.draw()

    def update_errorbar(self, errobj, x, y, xerr=None, yerr=None):
        ln, caps, bars = errobj

        if len(bars) == 2:
            assert xerr is not None and yerr is not None, "Your errorbar object has 2 dimension of error bars defined. You must provide xerr and yerr."
            barsx, barsy = bars  # bars always exist (?)
            try:  # caps are optional
                errx_top, errx_bot, erry_top, erry_bot = caps

            except ValueError:  # in case there is no caps
                pass


        elif len(bars) == 1:
            assert (xerr is     None and yerr is not None) or (xerr is not None and yerr is     None), "Your errorbar object has 1 dimension of error bars defined. You must provide xerr or yerr."
            if xerr is not None:
                barsx, = bars  # bars always exist (?)
                try:
                    errx_top, errx_bot = caps

                except ValueError:  # in case there is no caps
                    pass

            
            else:
                barsy, = bars  # bars always exist (?)
                try:
                    erry_top, erry_bot = caps

                except ValueError:  # in case there is no caps
                    pass

        ln.set_data(x,y)

        try:
            errx_top.set_xdata(x + xerr)
            errx_bot.set_xdata(x - xerr)
            errx_top.set_ydata(y)
            errx_bot.set_ydata(y)

        except NameError:
            pass


        try:
            barsx.set_segments([np.array([[xt, y], [xb, y]]) for xt, xb, y in zip(x + xerr, x - xerr, y)])

        except NameError:
            pass


        try:
            erry_top.set_xdata(x)
            erry_bot.set_xdata(x)
            erry_top.set_ydata(y + yerr)
            erry_bot.set_ydata(y - yerr)

        except NameError:
            pass


        try:
            barsy.set_segments([np.array([[x, yt], [x, yb]]) for x, yt, yb in zip(x, y + yerr, y - yerr)])

        except NameError:
            pass



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
        fig = Figure(figsize=(width, height), dpi=dpi, constrained_layout=True)
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
    plot_gui = Plot_GUI()
    plot_gui.S_curve()
    plot_gui.V_curve()
    
    timer = QTimer()
    timer.timeout.connect(lambda: plot_gui.read_Sdata())
    timer.start(1)
    
    timer2 = QTimer()
    timer2.timeout.connect(lambda: plot_gui.read_Vdata())
    timer2.start(1) 


    sys.exit(app.exec_())