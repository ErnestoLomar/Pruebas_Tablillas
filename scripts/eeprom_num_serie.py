##########################################
# Autor: Ernesto Lomar
# Fecha de creación: 26/04/2022
# Ultima modificación: 15/08/2022
#
# Script para obtener número de serie y número de versión de la raspberry
##########################################

#Importamos librerías externas
import subprocess
import logging

#Función para obtener el número de serie y número de versión de la memoria EEPROM y mostrarlo en la GUI
def cargar_num_serie():
    try:
        ok = subprocess.run("i2cdetect -y 1", stdout=subprocess.PIPE, shell=True)
        state_num_serie = ""
        state_num_version = ""

        if ok.returncode == 0:
            try:
                num_serie_hex = []
                i = 0

                while True:
                    i_hex = hex(i)
                    valor = subprocess.run(f"i2cget -y 1 0x50 {i_hex}", stdout=subprocess.PIPE, shell=True)
                    if valor.stdout[2:4].decode() == "00":
                        break
                    num_serie_hex.append(valor.stdout[2:4].decode())
                    i+=1

                num_serie_utf8 = []
                j = 0

                for i in num_serie_hex:
                    byte_arr = bytearray.fromhex(num_serie_hex[j])
                    num_serie_utf8.append(byte_arr.decode())
                    j+=1
                
                num_version_hex = []
                i = 100

                while True:
                    i_hex = hex(i)
                    valor = subprocess.run(f"i2cget -y 1 0x50 {i_hex}", stdout=subprocess.PIPE, shell=True)
                    if valor.stdout[2:4].decode() == "00":
                        break
                    num_version_hex.append(valor.stdout[2:4].decode())
                    i+=1

                num_version_utf8 = []
                j = 0

                for i in num_version_hex:
                    byte_arr = bytearray.fromhex(num_version_hex[j])
                    num_version_utf8.append(byte_arr.decode())
                    j+=1
                
                state_num_serie = "".join(num_serie_utf8)
                state_num_version = "".join(num_version_utf8)
                return { 
                    "state_num_serie": state_num_serie, 
                    "state_num_version": state_num_version  
                }
            except:
                state_num_serie = "ERR"
                state_num_version = "ERR"
                return { 
                    "state_num_serie": state_num_serie,
                    "state_num_version": state_num_version
                }
        else:
            state_num_serie = "NSxxxxx"
            state_num_version = "NVxxxxx"
            return {
                "state_num_serie": state_num_serie,
                "state_num_version": state_num_version
            }
    except Exception as e:
        logging.error(e)
        state_num_serie = "ERR"
        state_num_version = "ERR"
        return {
            "state_num_serie": state_num_serie,
            "state_num_version": state_num_version
        }