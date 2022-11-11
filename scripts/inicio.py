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
import serial
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
            if "UID" in estado.stdout.decode():
                print("Finalizando prueba RFID")
                break
            
class QuectelWorker(QObject):
    def __init__(self, ser):
        super().__init__()
        self.ser = ser
    
    finished = pyqtSignal()
    progress = pyqtSignal(dict)
    
    def run(self):
        diccionario = {}
        while True:
            print("Iniciando prueba Quectel")
            self.ser.flushInput()
            self.ser.flushOutput()
            comando = "AT\r\n"
            print("Enviando comando: " + comando)
            self.ser.write(comando.encode())
            time.sleep(1)
            respuesta = self.ser.readline()
            if 'OK' in respuesta.decode():
                diccionario['AT'] = respuesta.decode()
                
                self.ser.readline()
                self.ser.readline()
                self.ser.flushInput()
                self.ser.flushOutput()
                comando = "AT+CSQ\r\n"
                print("Enviando comando: " + comando)
                self.ser.write(comando.encode())
                time.sleep(1)
                respuesta = self.ser.readline()
                diccionario['CSQ'] = respuesta.decode()
                
                self.ser.flushInput()
                self.ser.flushOutput()
                comando = "AT+QGPSLOC=2\r\n"
                print("Enviando comando: " + comando)
                self.ser.write(comando.encode())
                time.sleep(1)
                respuesta = self.ser.readline()
                Tam = len(respuesta.decode())
                if Tam > 27:
                    Cortada = respuesta.decode()
                    aux1 = Cortada.split(",")
                    Latitud = aux1[1]
                    Longitud = aux1[2]
                    diccionario['Latitud'] = Latitud
                    diccionario['Longitud'] = Longitud
                else:
                    diccionario['error'] = respuesta.decode()
                    
                self.ser.flushInput()
                self.ser.flushOutput()
                comando = "AT+CCID\r\n"
                print("Enviando comando: " + comando)
                self.ser.write(comando.encode())
                time.sleep(1)
                respuesta = self.ser.readline()
                diccionario['CCID'] = respuesta.decode()
                
                print("Finalizando prueba Quectel")
                self.progress.emit(diccionario)
            else:
                print("Error en el comando AT")
                diccionario['AT'] = respuesta.decode()
                self.progress.emit(diccionario)

class principal(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Cargar la interfaz gráfica
        uic.loadUi("../ui/inicio.ui", self)
        
        # Iniciamos comunicación con serial
        try:
            self.ser = serial.Serial('/dev/serial0', 115200, timeout=1)
        except Exception as e:
            print("Error al abrir el puerto serial: ", e)
            self.label_estado_quectel.setTexts(str(e))
        
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
        self.runQuectel()
        
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
            print("Error al iniciar el hilo de RFID: " + str(e))
            
    def reportProgressRIFD(self, res: dict):
        try:
            if 'UID' in res["estado"]:
                self.label_resultado_rfid.setPixmap(QPixmap(""))
                time.sleep(.5)
                self.label_resultado_rfid.setPixmap(QPixmap("../img/comprobado.png"))
                print("RFID correcto")
            elif '30000' in res["estado"]:
                self.label_resultado_rfid.setPixmap(QPixmap(""))
                print("RFID en espera")
            else:
                self.label_resultado_rfid.setPixmap(QPixmap(""))
                time.sleep(.5)
                self.label_resultado_rfid.setPixmap(QPixmap("../img/incorrecto.png"))
                print("RFID incorrecto")
        except Exception as e:
            print("inicio.py, linea 160: "+str(e))
            
    def runQuectel(self):
        try:
            self.quectelThread = QThread()
            self.quectelWorker = QuectelWorker(self.ser)
            self.quectelWorker.moveToThread(self.quectelThread)
            self.quectelThread.started.connect(self.quectelWorker.run)
            self.quectelWorker.finished.connect(self.quectelThread.quit)
            self.quectelWorker.finished.connect(self.quectelWorker.deleteLater)
            self.quectelThread.finished.connect(self.quectelThread.deleteLater)
            self.quectelWorker.progress.connect(self.reportProgressQuectel)
            self.quectelThread.start()
        except Exception as e:
            print("Error al iniciar el hilo de quectel: " + str(e))
            
    def reportProgressQuectel(self, res: dict):
        try:
            if 'OK' in res["AT"]:
                self.label_estado_quectel.setText("Iniciando...")
                self.label_intensidad_sim.setText(res["CSQ"])
                if ("error" not in res.keys()):
                    self.label_latitud.setText(res["Latitud"])
                    self.label_longitud.setText(res["Longitud"])
                else:
                    self.label_latitud.setText(res["error"])
                self.label_numero_sim.setText(res["CCID"])
            else:
                self.label_estado_quectel.setText("Error")
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