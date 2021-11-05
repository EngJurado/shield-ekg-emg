import sys
import pyqtgraph as pg
from PyQt5 import QtWidgets, uic

class prueba(QtWidgets.QMainWindow):
    def __init__(self):
        super(prueba, self).__init__()
        uic.loadUi('prueba.ui', self)
        self.pushButton.clicked.connect(self.graficar)

    def graficar(self):
        L = [1, 2, 3, 4 ]
        self.graphicsView.plot(L)

def main():
    app = QtWidgets.QApplication(sys.argv)
    main = prueba()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
