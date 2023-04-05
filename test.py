import sys
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtChart import QChart, QChartView, QLineSeries

class ChartThread(QThread):
    chart_ready = pyqtSignal(QChart)

    def run(self):
        # Créer un graphique en ligne
        series = QLineSeries()
        series.append(0, 0)
        series.append(1, 1)
        chart = QChart()
        chart.legend().hide()
        chart.addSeries(series)
        chart.createDefaultAxes()
        chart.setTitle("Graphique en ligne")

        # Émettre le signal chart_ready avec le graphique créé
        self.chart_ready.emit(chart)

# Créer l'application et la fenêtre dans le thread principal
app = QApplication(sys.argv)
win = QMainWindow()
widget = QWidget()
layout = QVBoxLayout()
widget.setLayout(layout)
win.setCentralWidget(widget)

# Ajouter une vue de graphique dans le layout
chart_view = QChartView()
chart_view.setRenderHint(QPainter.Antialiasing)
layout.addWidget(chart_view)

# Démarrer le thread de graphique
chart_thread = ChartThread()
chart_thread.chart_ready.connect(chart_view.setChart)
chart_thread.start()

# Afficher la fenêtre
win.show()

# Lancer l'application
sys.exit(app.exec_())
