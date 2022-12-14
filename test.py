from PyQt5.QtCore import QPoint, QSize, Qt, QTime, QTimer, QPropertyAnimation, QPointF, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QColor, QPainter, QPolygon, QRegion, QPen, QFont, QPolygonF
from PyQt5.QtWidgets import QAction, QApplication, QWidget, QDesktopWidget


class EmergencyShape(QWidget):
    #Nearly everything scales with that variable, so adjust it as you like
    size = 300
    #hexagon.height = hexagon.width * x
    x = (3**0.5 / 2)
    #text = "UNITY NOT US\n:^)"
    text = "AYY LMAO"
    font = QFont('Arial', int(size*0.08))
    font.setWeight(500)
    font.setHintingPreference(3)
    font.setStyleStrategy(QFont.PreferAntialias)
    #font.setFixedPitch(True)
    hexaPoints = [QPoint(int(size/4),0),
                    QPoint(int(size/4 + size/2),0),
                    QPoint(int(size),int(size*0.5*x)),
                    QPoint(int(size/4 + size/2),int(size*x)),
                    QPoint(int(size/4),int(size*x)),
                    QPoint(int(0),int(size*0.5*x))]
    hexaPointsF = [QPointF(size/4,0),
                    QPointF(size/4 + size/2,0),
                    QPointF(size,size*0.5*x),
                    QPointF(size/4 + size/2,size*x),
                    QPointF(size/4,size*x),
                    QPointF(0,size*0.5*x)]
    hexa = QPolygon(hexaPoints)
    hexaF = QPolygonF(hexaPoints)
    trianglePointsF = [QPointF(0, 0),
                        QPointF(size/8, (size*x)/4),
                        QPointF(-size/8, (size*x)/4)]

    def __init__(self, parent=None, xPos=0, yPos=0):
        super(EmergencyShape, self).__init__(parent,
                Qt.FramelessWindowHint | Qt.WindowSystemMenuHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        quitAction = QAction("E&xit", self, shortcut="Ctrl+Q",
                triggered=QApplication.instance().quit)
        self.addAction(quitAction)
        self.setGeometry(int(xPos), int(yPos), int(EmergencyShape.size), int(EmergencyShape.size))

        self.hideAnimation = QPropertyAnimation(self, "windowOpacity")
        self.hideAnimation.setDuration(300)
        self.hideAnimation.setEndValue(0.0)
        self.showAnimation = QPropertyAnimation(self, "windowOpacity")
        self.showAnimation.setDuration(300)
        self.showAnimation.setEndValue(1.0)


    @pyqtSlot()
    def toggle(self):
        if self.windowOpacity() == 1.0:
            self.hideAnimation.start()
        else:
            self.showAnimation.start()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.toggle()
            #self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            #self.move(event.globalPos() - self.dragPosition)
            event.accept()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        #Draw red polygon
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 0, 0))
        painter.drawPolygon(*EmergencyShape.hexaF)

        #Draw inner black border line
        plist = EmergencyShape.hexaPointsF + [EmergencyShape.hexaPointsF[0]]
        s = 0.95
        painter.translate(QPointF(EmergencyShape.size*(1-s)*0.5, EmergencyShape.size*(1-s)*0.5*EmergencyShape.x))
        painter.scale(s, s)
        painter.setPen(QPen(QColor(0,0,0), (EmergencyShape.size*0.016)*(1/s)))
        painter.drawPolyline(*plist)
        painter.resetTransform()

        #Draw triangles
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0))
        painter.translate(EmergencyShape.size*0.5, EmergencyShape.size*EmergencyShape.x/16)
        painter.drawPolygon(*EmergencyShape.trianglePointsF)
        painter.translate(0, EmergencyShape.size*EmergencyShape.x - EmergencyShape.size*EmergencyShape.x/8)
        painter.scale(1, -1)
        painter.drawPolygon(*EmergencyShape.trianglePointsF)
        painter.resetTransform()

        #Draw text
        pen_text = QPen()
        pen_text.setBrush(QColor(0,0,0))
        painter.setPen(pen_text)
        painter.setFont(EmergencyShape.font)
        painter.drawText(0, 0, EmergencyShape.size, EmergencyShape.size*EmergencyShape.x, Qt.AlignCenter, EmergencyShape.text)

    def resizeEvent(self, event):
        self.setMask(QRegion(EmergencyShape.hexa))

    def sizeHint(self):
        return QSize(EmergencyShape.size, EmergencyShape.size)

class Worker(QThread):
    trigger = pyqtSignal()
    def __init__(self, shapes=[], running=True, intervall=0.3):
        super(Worker, self).__init__()
        self.shapes = shapes
        self.running = running
        self.intervall = intervall

    def run(self):
        time.sleep(1)
        r = 0
        while self.running:
            #r = random.randint(0, len(self.shapes)-1)
            print("shape:", r, self.shapes[r].windowOpacity(), self.shapes[r].hideAnimation.state())
            self.trigger.connect(self.shapes[r].toggle)
            self.trigger.emit()
            self.trigger.disconnect(self.shapes[r].toggle)
            time.sleep(self.intervall)
            r = (r+1)%len(shapes)

if __name__ == '__main__':

    import sys
    import time
    import random

    app = QApplication(sys.argv)

    screen = QDesktopWidget().screenGeometry()
    dy = screen.height()//int(EmergencyShape.size * EmergencyShape.x) + 1
    dx = screen.width()//int(EmergencyShape.size * 0.75) + 1

    shapes = []
    margin = EmergencyShape.size/50
    xOffset = -EmergencyShape.size*0.4
    yOffset = -EmergencyShape.size*0.4

    #dx = dy = 2

    for i in range(dx):
        for j in range(dy):
            shape = EmergencyShape(xPos=(EmergencyShape.size*i*0.75) + i*margin + xOffset,
                                yPos=(EmergencyShape.size*EmergencyShape.x*j)
                                    + margin*j 
                                    + (i%2)*EmergencyShape.size*0.5*EmergencyShape.x
                                    + (i%2)*margin*0.5
                                    + yOffset)
            shapes.append(shape)
            shape.show()


    th = Worker(shapes, intervall=0.033)
    th.start()
    sys.exit(app.exec_())