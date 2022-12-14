import sys
import matplotlib
matplotlib.use('Qt5Agg')
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
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure



###############################################################################
# This program is working with Interface.py and Validate.py files as parents for SoftMeasure.
# It contains useful code allowing to display measurement in live.
###############################################################################



class Plot_GUI(QWidget):
    def __init__(self, parent):
        """
        New window integrating plots.

        ---------
        Parameter:
        parent: class
        """

        super().__init__()
        self.parent = parent
        self.setWindowTitle('SoftMeasure')
        self.xdata = []
        self.widget()

        layout = QGridLayout()
        layout.addWidget(self.box, 0, 0)
        self.setLayout(layout)
        self.show()


    def widget(self):
        """
        Display of plot frame widgets.
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

        self.Sthread.start()


    def V_QT(self, watch_Vfile, watch_DVfile):
        """
        Qthread bound to the reading of the V file.

        ---------
        Parameter:
        watch_Vfile: class
        """

        self.watch_Vfile = watch_Vfile
        self.watch_DVfile = watch_DVfile
        self.Vwatcher = Watcher(watch_Vfile)
        self.Vthread = QThread()

        self.Vwatcher.moveToThread(self.Vthread)
        self.Vwatcher.read_data.connect(self.read_Vdata)
        self.Vwatcher.finished.connect(self.Vthread.quit)

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

        self.V_trace = self.V_plot.graph.axes.errorbar([], [], [], c=color, marker='o')
        self.V_plot.graph.draw()


    def read_Sdata(self, idx):
        """
        Event function to trace S when Sfile is modified.

        ---------
        Parameter:
        idx: int
            Index of the last row in the file.
        """
        
        ydata = np.genfromtxt(self.watch_Sfile, skip_header=1+idx, delimiter=', ')

        try:
            self.S_trace.set_data(self.xdata[:len(ydata)], ydata)

        except TypeError:
            self.S_trace.set_data(self.xdata[0], ydata)

        except IndexError:
            self.S_trace.set_data(self.xdata[0], ydata)
        
        self.S_plot.graph.axes.relim()
        self.S_plot.graph.axes.autoscale_view()
        self.S_plot.graph.draw()

    
    def read_Vdata(self, idx):
        """
        Event function to trace V when Vfile is modified.

        ---------
        Parameter:
        idx: int
            Index of the last row in the file.
        """
        
        ydata = np.genfromtxt(self.watch_Vfile, skip_header=1+idx, delimiter=', ')
        Dydata = np.genfromtxt(self.watch_DVfile, skip_header=1+idx, delimiter=', ')

        try:
            self.update_errorbar(self.V_trace, self.xdata[:len(ydata)], ydata, None, Dydata)

        except TypeError:
            self.update_errorbar(self.V_trace, np.array([self.xdata[0]]), np.array([ydata]), None, np.array([Dydata]))

        except IndexError:
            self.update_errorbar(self.V_trace, np.array([self.xdata[0]]), np.array([ydata]), None, np.array([Dydata]))
        
        self.V_plot.graph.axes.relim()
        self.V_plot.graph.axes.autoscale_view()
        self.V_plot.graph.draw()


    def update_errorbar(self, errobj, x, y, xerr=None, yerr=None):
        """
        Method allowing to update errorbar

        ---------
        Parameter:
        errobj: class
            Errorbar from matplotlib

        x: np.ndarray

        y: np.ndarray

        xerr: any

        yerr: any
        """

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
            Path of the targeted file.
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
    

    plot_gui = Plot_GUI(1)

    watch_Sfile = r'C:\Users\guill\OneDrive\Bureau\test.txt'.replace('\\', '/')

    plot_gui.S_curve(watch_Sfile)
    Timer(20, plot_gui.Swatcher.stop_watching).start()


    sys.exit(app.exec_())