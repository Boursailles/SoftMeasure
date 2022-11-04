from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import sys
import numpy as np



class MyMplCanvas(FigureCanvas):

    def __init__(self, parent=None):
        self.fig = Figure()
        self.axes = self.fig.add_subplot(111)
        # plot empty line 
        self.line, = self.axes.plot([],[], color="orange")

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


class MainWindow(QMainWindow):
    send_fig = pyqtSignal(str)

    def __init__(self):
        super(MainWindow, self).__init__()

        self.main_widget = QWidget(self)
        self.myplot = MyMplCanvas(self.main_widget)
        self.editor = QLineEdit()
        self.display = QLabel("Vide")

        self.layout = QGridLayout(self.main_widget)
        self.layout.addWidget(self.editor)
        self.layout.addWidget(self.display)
        self.layout.addWidget(self.myplot)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        self.show()

        # plotter and thread are none at the beginning
        self.plotter = Plotter()
        self.thread = QThread()

        # connect signals
        self.editor.returnPressed.connect(self.start_update)
        self.send_fig.connect(self.plotter.replot)
        self.plotter.return_fig.connect(self.plot)
        #move to thread and start
        self.plotter.moveToThread(self.thread)
        self.thread.start()

    def start_update(self):
        ticker = self.editor.text()
        self.editor.clear()
        self.display.setText(ticker)
        # start the plotting
        self.send_fig.emit(ticker)


    # Slot receives data and plots it
    def plot(self, data):
        # plot data
        self.myplot.line.set_data([np.arange(len(data)), data])
        # adjust axes
        self.myplot.axes.set_xlim([0,len(data) ])
        self.myplot.axes.set_ylim([ data.min(),data.max() ])
        self.myplot.draw()


class Plotter(QObject):
    return_fig = pyqtSignal(object)

    @pyqtSlot(str)
    def replot(self, ticker):
        print(ticker)
        # do some random task
        data = np.random.rand(10000,10000)
        data = data.mean(axis=1)
        self.return_fig.emit(data)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    sys.exit(app.exec_())