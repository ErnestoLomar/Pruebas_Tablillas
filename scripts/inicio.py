##########################################
# Autor: Ernesto Lomar
# Fecha de creación: 09/11/2022
# Ultima modificación: 11/11/2022
#
# Script principal del programa
#
##########################################

# Librerías importadas
import subprocess
import time
from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
from eeprom_num_serie import cargar_num_serie

class RFIDWorker(QObject):
    def __init__(self):
        super().__init__()
        pass
    
    finished = pyqtSignal()
    progress = pyqtSignal(dict)
    
    def run(self):
        while True:
            print("Iniciando prueba RFID")
            estado = subprocess.run("nfc-poll", stdout=subprocess.PIPE, shell=True)
            self.progress.emit({"estado": estado.stdout.decode()})

class principal(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Cargar la interfaz gráfica
        uic.loadUi("../ui/inicio.ui", self)
        
        # Conectar los botones con sus funciones
        self.label_img_reiniciar_prueba.mousePressEvent = self.reiniciar_prueba
        self.label_reiniciar_prueba.mousePressEvent = self.reiniciar_prueba
        self.label_img_reiniciar_raspberry.mousePressEvent = self.reiniciar_raspberry
        self.label_reiniciar_raspberry.mousePressEvent = self.reiniciar_raspberry
        self.label_img_apagar.mousePressEvent = self.apagar_raspberry
        self.label_apagar.mousePressEvent = self.apagar_raspberry
        
        # Iniciamos prueba de memoria EEPROM
        self.verificar_memoria_eeprom()
        
        # Iniciamos prueba de RFID
        self.runRFID()
        
    def verificar_memoria_eeprom(self):
        estado = cargar_num_serie()
        if 'ERR' in str(estado['state_num_serie']) or 'NSxxxxx' in str(estado['state_num_serie']) and 'ERR' in str(estado['state_num_version']) or 'NVxxxxx' in str(estado['state_num_version']):
            self.label_resultado_eeprom.setPixmap(QPixmap("../img/incorrecto.png"))
            print("Error en la memoria EEPROM")
        else:
            self.label_resultado_eeprom.setPixmap(QPixmap("../img/comprobado.png"))
            print("Memoria EEPROM correcta")
            
    def runRFID(self):
        try:
            self.rfidThread = QThread()
            self.rfidWorker = RFIDWorker()
            self.rfidWorker.moveToThread(self.rfidThread)
            self.rfidThread.started.connect(self.rfidWorker.run)
            self.rfidWorker.finished.connect(self.rfidThread.quit)
            self.rfidWorker.finished.connect(self.rfidWorker.deleteLater)
            self.rfidThread.finished.connect(self.rfidThread.deleteLater)
            self.rfidWorker.progress.connect(self.reportProgressRIFD)
            self.rfidThread.start()
        except Exception as e:
            print("Error al iniciar el hilo de minicom: " + str(e))
            
    def reportProgressRIFD(self, res: dict):
        try:
            if 'UID' in res["estado"]:
                self.label_resultado_rfid.setPixmap(QPixmap(""))
                time.sleep(.5)
                self.label_resultado_rfid.setPixmap(QPixmap("../img/comprobado.png"))
                print("RFID correcto")
            elif 'Success' in res["estado"]:
                self.label_resultado_rfid.setPixmap(QPixmap(""))
                time.sleep(.5)
                self.label_resultado_rfid.setPixmap(QPixmap("../img/comprobado.png"))
                print("RFID correcto")
            else:
                self.label_resultado_rfid.setPixmap(QPixmap(""))
                time.sleep(.5)
                self.label_resultado_rfid.setPixmap(QPixmap("../img/incorrecto.png"))
                print("RFID incorrecto")
        except Exception as e:
            print("inicio.py, linea 160: "+str(e))
        
    def reiniciar_prueba(self, event):
        print("Reiniciar prueba")
        
    def reiniciar_raspberry(self, event):
        print("Reiniciar raspberry")
        
    def apagar_raspberry(self, event):
        print("Apagar raspberry")        
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    GUI = principal()
    GUI.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
    GUI.show()
    sys.exit(app.exec_())