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
from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtGui import *
import sys
from eeprom_num_serie import cargar_num_serie

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
        
        # Iniciamos pruebas
        self.verificar_memoria_eeprom()
        
    def verificar_memoria_eeprom(self):
        estado = cargar_num_serie()
        if 'ERR' in str(estado['state_num_serie']) or 'NSxxxxx' in str(estado['state_num_serie']) and 'ERR' in str(estado['state_num_version']) or 'NVxxxxx' in str(estado['state_num_version']):
            self.label_resultado_eeprom.setPixmap(QPixmap("../img/incorrecto.png"))
            print("Error en la memoria EEPROM")
        else:
            self.label_resultado_eeprom.setPixmap(QPixmap("../img/comprobado.png"))
            print("Memoria EEPROM correcta")
            
    def verificar_rfid(self):
        estado = subprocess.run("nfc-poll", stdout=subprocess.PIPE, shell=True)
        print(estado.stdout.decode())
        
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