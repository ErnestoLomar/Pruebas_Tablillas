from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication
import sys

class principal(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("../ui/inicio.ui", self)
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    GUI = principal()
    GUI.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
    GUI.show()
    sys.exit(app.exec_())