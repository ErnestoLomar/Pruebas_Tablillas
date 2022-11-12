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
import board
import digitalio
import neopixel

rfid_ya_verificado = False

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
class QuectelWorker(QObject):
    def __init__(self, ser):
        super().__init__()
        self.ser = ser
    
    finished = pyqtSignal()
    progress = pyqtSignal(dict)
    
    def run(self):
        while True:
            diccionario = {}
            print("Iniciando prueba Quectel")
            self.ser.flushInput()
            self.ser.flushOutput()
            comando = "AT\r\n"
            print("Enviando comando: " + comando)
            self.ser.write(comando.encode())
            self.ser.readline()
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
                self.ser.readline()
                time.sleep(1)
                respuesta = self.ser.readline().decode()
                if(respuesta.startswith("+CSQ: ")):
                    comando = respuesta.replace("+CSQ: ", "")
                    comando = comando.rstrip("\r\n")
                    comando = comando[:-3]
                    respuesta = float(comando)
                    diccionario['CSQ'] = str(respuesta)
                else:
                    diccionario['CSQ'] = respuesta
                
                self.ser.flushInput()
                self.ser.flushOutput()
                comando = "AT+QGPSLOC=2\r\n"
                print("Enviando comando: " + comando)
                self.ser.write(comando.encode())
                self.ser.readline()
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
                    respuesta = respuesta.decode()
                    comando = respuesta.replace("+CME ERROR: ", "")
                    comando = comando.rstrip("\r\n")
                    diccionario['error'] = comando
                    
                self.ser.flushInput()
                self.ser.flushOutput()
                comando = "AT+CCID\r\n"
                print("Enviando comando: " + comando)
                self.ser.write(comando.encode())
                self.ser.readline()
                time.sleep(1)
                respuesta = self.ser.readline().decode()
                if(respuesta.startswith("+CCID: ")):
                    comando = respuesta.replace("+CCID: ", "")
                    comando = comando.rstrip("\r\n")
                    diccionario['CCID'] = comando
                else:
                    diccionario['CCID'] = respuesta
                
                print("Finalizando prueba Quectel")
                self.progress.emit(diccionario)
            else:
                print("Error en el comando AT")
                print(respuesta)
                diccionario['AT'] = respuesta.decode()
                self.progress.emit(diccionario)
                
class ZuLedsWorker(QObject):
    def __init__(self):
        super().__init__()
        pass
    
    finished = pyqtSignal()
    progress = pyqtSignal(dict)
    
    def run(self):
        pixels = neopixel.NeoPixel(board.D21, 4, brightness=0.1, auto_write=False, pixel_order=neopixel.GRB)
        zumbador = digitalio.DigitalInOut(board.D18)
        zumbador.direction = digitalio.Direction.OUTPUT
        while True:
            print("Iniciando prueba de Zumbador y Leds")
            
            zumbador.value = True
            time.sleep(0.1)
            zumbador.value = False
            
            for i in range(5):
                for j in range(255):
                    if i == 1:
                        pixels[0] = (j, 0, 0)
                        pixels[1] = (j, 0, 0)
                        pixels[2] = (j, 0, 0)
                        pixels[3] = (j, 0, 0)
                        pixels.show()
                        time.sleep(0.01)
                    if i == 2:
                        pixels[0] = (255-j, j, 0)
                        pixels[1] = (255-j, j, 0)
                        pixels[2] = (255-j, j, 0)
                        pixels[3] = (255-j, j, 0)
                        pixels.show()
                        time.sleep(0.01)
                    if i == 3:
                        pixels[0] = (0, 255-j, j)
                        pixels[1] = (0, 255-j, j)
                        pixels[2] = (0, 255-j, j)
                        pixels[3] = (0, 255-j, j)
                        pixels.show()
                        time.sleep(0.01)
                    if i == 4:
                        pixels[0] = (0, 0, 255-j)
                        pixels[1] = (0, 0, 255-j)
                        pixels[2] = (0, 0, 255-j)
                        pixels[3] = (0, 0, 255-j)
                        pixels.show()
                        time.sleep(0.01)
            time.sleep(3)

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
        self.runZumbadorLeds()
        
    def verificar_memoria_eeprom(self):
        self.label_resultado_eeprom.show()
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
            global rfid_ya_verificado
            self.label_resultado_rfid.show()
            if 'UID' in res["estado"]:
                self.label_resultado_rfid.setPixmap(QPixmap(""))
                time.sleep(.5)
                self.label_resultado_rfid.setPixmap(QPixmap("../img/comprobado.png"))
                rfid_ya_verificado = True
                print("RFID correcto")
            elif '30000' in res["estado"] and rfid_ya_verificado == False:
                self.label_resultado_rfid.setPixmap(QPixmap(""))
                print("RFID en espera")
            elif '30000' in res["estado"] and rfid_ya_verificado:
                self.label_resultado_rfid.setPixmap(QPixmap("../img/comprobado.png"))
                print("RFID correcto")
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
            self.label_estado_quectel.show()
            self.label_intensidad_sim.show()
            self.label_latitud.show()
            self.label_longitud.show()
            self.label_numero_sim.show()
            if 'OK' in res["AT"]:
                self.label_estado_quectel.setStyleSheet('color: #7cfc00; font: 16pt "Franklin Gothic Medium";')
                self.label_estado_quectel.setText("Iniciando...")
                if ("CSQ" in res.keys()):
                    self.label_intensidad_sim.setStyleSheet('color: #7cfc00; font: 16pt "Franklin Gothic Medium";')
                    self.label_intensidad_sim.setText(res["CSQ"])
                    if ("error" not in res.keys()):
                        self.label_latitud.setStyleSheet('color: #7cfc00; font: 16pt "Franklin Gothic Medium";')
                        self.label_latitud.setText(res["Latitud"])
                        self.label_longitud.setStyleSheet('color: #7cfc00; font: 16pt "Franklin Gothic Medium";')
                        self.label_longitud.setText(res["Longitud"])
                    else:
                        self.label_latitud.setStyleSheet('color: #CB4335; font: 16pt "Franklin Gothic Medium";')
                        self.label_latitud.setText(res["error"])
                        self.label_longitud.setText("")
                    if ("CCID" in res.keys()):
                        self.label_numero_sim.setStyleSheet('color: #7cfc00; font: 16pt "Franklin Gothic Medium";')
                        self.label_numero_sim.setText(res["CCID"])
            else:
                self.label_estado_quectel.setStyleSheet('color: #CB4335; font: 16pt "Franklin Gothic Medium";')
                self.label_estado_quectel.setText(res["AT"])
        except Exception as e:
            print("inicio.py, linea 160: "+str(e))
            
    def runZumbadorLeds(self):
        try:
            self.zuledsThread = QThread()
            self.zuledsWorker = ZuLedsWorker()
            self.zuledsWorker.moveToThread(self.zuledsThread)
            self.zuledsThread.started.connect(self.zuledsWorker.run)
            self.zuledsWorker.finished.connect(self.zuledsThread.quit)
            self.zuledsWorker.finished.connect(self.zuledsWorker.deleteLater)
            self.zuledsThread.finished.connect(self.zuledsThread.deleteLater)
            self.zuledsWorker.progress.connect(self.reportProgressZuLeds)
            self.zuledsThread.start()
        except Exception as e:
            print("Error al iniciar el hilo de RFID: " + str(e))
            
    def reportProgressZuLeds(self, res: dict):
        try:
            pass
        except Exception as e:
            print("inicio.py, linea 160: "+str(e))
        
    def reiniciar_raspberry(self, event):
        print("Reiniciar raspberry")
        zumbador = digitalio.DigitalInOut(board.D18)
        zumbador.direction = digitalio.Direction.OUTPUT
        zumbador.value = False
        subprocess.run("sudo reboot", shell=True)
        
    def apagar_raspberry(self, event):
        print("Apagar raspberry")
        zumbador = digitalio.DigitalInOut(board.D18)
        zumbador.direction = digitalio.Direction.OUTPUT
        zumbador.value = False
        subprocess.run("sudo shutdown -h now", shell=True)     
        
    def reiniciar_prueba(self, event):
        print("Reiniciar prueba")
        global rfid_ya_verificado
        self.label_resultado_eeprom.hide()
        self.label_resultado_rfid.hide()
        self.label_estado_quectel.hide()
        self.label_intensidad_sim.hide()
        self.label_latitud.hide()
        self.label_longitud.hide()
        self.label_numero_sim.hide()
        rfid_ya_verificado = False
        self.verificar_memoria_eeprom()
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    GUI = principal()
    GUI.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
    GUI.show()
    sys.exit(app.exec_())