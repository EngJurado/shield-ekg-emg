# -*- coding: utf-8 -*-
"""
Este es un programa para adquirir y procesar señales de ecg

@author: mateo y yeindy

Comentado por mateo
"""

import sys  # libreria para ejecutar en el sistea opetarivo
from PyQt5 import QtWidgets, QtCore, uic  # librerias para la creacion y manipulacion de la interfax grafica
import serial  # libreri para comunicar el puerto serial del arduino con python
import numpy as np # libreria usada para manipular los arrays y lguardar artchivos .npy
import time # libreria para hacer el timer
import pyqtgraph as pg # libreria usada para la visualizacion de graficas en el qgraphicsview
from PyQt5.QtWidgets import QFileDialog # libreria para seleccionar graficamente un archivo y que arroje su ubicacion completa
from numpy import savetxt # libreria para guardar archivos txt
from biosppy.signals import ecg # libreria de filtros
import dropbox                                     #------------------------------------------------
from dropbox.files import WriteMode                # librerias usadas para subir archivos a la nube
from dropbox.exceptions import ApiError, AuthError #------------------------------------------------
import os # libreria usada para obtener el nombre del archivo

class ECGmain(QtWidgets.QMainWindow):   #-------------------------------------------
    def __init__(self):                 # se crea la clase EGCmain y su constructor
        super(ECGmain, self).__init__() #-------------------------------------------
        uic.loadUi('main.ui', self) # carga el archivo .ui creado con el Qt designer
        self.show()  # muestra la interfaz cargada en la linea anterior
        
        self.pushButton.clicked.connect(self.adquirirop) # conecta el pushbutton con la funcion adquirirop
        self.pushButton_2.clicked.connect(self.filtrarop) # conecta el pushbutton 2 con la funcion filtrarop
        self.pushButton_3.clicked.connect(self.nubeop) # conecta el pushbutton 3 con la funcion nubeop

    def adquirirop(self): # se crea la funcion adquirirop
        self.ad = adquirir() # se iguala self.ad a la clase adquirir
        self.ad.show() # muestra la interfaz de la clase adquirir
        
    def filtrarop(self): # se crea la funcion filtrarop
        self.fil = filtrar() # se iguala self.fill a la clase filtrar
        self.fil.show() # se muestra la interfaz de la clase filtrar

    def nubeop(self): # se crea la funcion nubeop
        self.nub = nubes() # se iguala self.nub a la clase nubes
        self.nub.show() # se muestra la interfaz de la clase nube

class nubes(QtWidgets.QMainWindow):    #------------------------------------------
    def __init__(self):                # se crea kla clase nubes y su constructor
        super(nubes, self).__init__()  #-----------------------------------------
        uic.loadUi('nube.ui', self) # se carga la interfaz desde un archivo .ui proveniente del Qt designer
        self.pushButton.clicked.connect(self.nube) # se conecta el pushbutton con la funcion nube
        self.fichero_actual = "" # se inicializa el string que contiene la ruta del archivo a subir como un string vacio
        
    def nube(self): # se crea la funcion nube

        TOKEN = 'tHtpWfnXqSAAAAAAAAAAdLSCCatRKTvaaAkVTI2Hqq1qj9GS1xy8sUhbDioVUqQt' # este es el token de autentificacion usado para conectar la cuenta de dropbox con python, dentro de la carpeta Tokendropbox hay un video que explic como obtenerlo 

        options = QFileDialog.Options()               # crea la opcion options y se configura para no usar
        options |= QFileDialog.DontUseNativeDialog    # el explorador de archivos por defecto sino usar el de QT
        nombre_fichero, _ = QFileDialog.getOpenFileName(self, "Abrir fichero", options=options) #-----------------------------------------------------------------------------
        if nombre_fichero:                                                                      # almacen en self.fichero_actual la ruta del archivo seleccionado graficamente
            self.fichero_actual = nombre_fichero                                                #-----------------------------------------------------------------------------

        LOCALFILE = self.fichero_actual # se iguala LOCALFILE a la ruta del archivo que vamos a subir

        nombre = os.path.basename(self.fichero_actual) # se optiene el nombre del archivo a subir
        
        BACKUPPATH = '/PIS/'+ nombre # Esta es la ruta en donde sera almacenado dentro de dropbox

        def backup(): # se crea la funcion que sube el archivo a la nube
            
            with open(LOCALFILE, 'rb') as f: # se abre el archivo a subir en modo lectura

                self.label.setText("subiendo " + LOCALFILE + " a Dropbox como " + BACKUPPATH + "...") # muestra en el label que archivo se esta subiendo a la nube y en que parte de la nube se esta subiendo
                try:
                    dbx.files_upload(f.read(), BACKUPPATH, mode=WriteMode('overwrite')) # este comando es el que lo sube a la nube, si el archivo ya existe lo sobrescribe
                except ApiError as err:                                                     #---------------------------------------------------------------
                    if (err.error.is_path() and                                             #
                            err.error.get_path().error.is_insufficient_space()):            #
                        sys.exit("ERROR: No se puesde subir; no tiene espacio suficiente.") # Todo esto es para que si sale un error
                    elif err.user_message_text:                                             # se deje de ejecutar el programa, y si
                        print(err.user_message_text)                                        # el error es de que no se tiene espacio
                        sys.exit()                                                          # suficiente en dropbox, muestre un mensaje
                    else:                                                                   # en el que se informe eso
                        print(err)                                                          #
                        sys.exit()                                                          #-----------------------------------------------------------------

        def checkFileDetails(): # se define una funcion para mostrar las carpetas creadas en dropbox
            
            self.label.setText("subiendo " + LOCALFILE + " a Dropbox como " + BACKUPPATH + "...\nConfirmando detalles") # se actualiza el label para que muestre adicionalmente a lo que ya mostraba el mensaje de confirmando detalles
    
            for self.entry in dbx.files_list_folder('').entries: # Recorre las carpetas que se tienen en dropbox
                self.label.setText("subiendo " + LOCALFILE + " a Dropbox como " + BACKUPPATH + "...\nConfirmando detalles\nLa lista de carpetas es : \n" + self.entry.name) # se actualiza el label para que muestre adicionalmente a lo que ya mostraba con las carpetas presentes en Dropbox

        if (len(TOKEN) == 0): # se chekea el token, si no se a ingresado uno se muestra el siguiente mensaje
            sys.exit("ERROR: No se ha ingresado el Token de autentificacion, por favor ingreselo en la linea 61.") # muestra un mensaje en el que se indica en donde ingresar el token

        dbx = dropbox.Dropbox(TOKEN) # se conecta python con Dropbox usando el Token de autentificacion
        for self.entry in dbx.files_list_folder('').entries:
            self.label.setText("subiendo " + LOCALFILE + " a Dropbox como " + BACKUPPATH + "...\nConfirmando detalles\nLa lista de carpetas es : \n" + self.entry.name + "\nCreando Dropbox object...")  # actualiza el label mostrando el mensaje de creando el Dropbox objet

        try:                                      #--------------------------------------------------------------------------------------------------
            dbx.users_get_current_account()       # Se confirma que el Token sea correcto usando la funcion que muestra la informacion de la cuenta,
        except AuthError as err:                  # pero esta no se muestra, se usa solo para que si da error mostrar un mensaje de que el 
            sys.exit(                             # Token ingresado es invalido.
                "ERROR: El Token es invalido.")   #----------------------------------------------------------------------------------------------------

        try:                                                                         #-------------------------------------------------------------------        
            checkFileDetails()                                                       # Se ejecuta la funcion que muestra las carpetas creadas en Dropbox
        except Error as err:                                                         # y muestra un error si hay errores al ejecutar dicha funcion 
            sys.exit("Error mientras se confirmaba la informacion de las carpetas")  #-------------------------------------------------------------------

        self.label.setText("subiendo " + LOCALFILE + " a Dropbox como " + BACKUPPATH + "...\nConfirmando detalles\nLa lista de carpetas es : \n" + self.entry.name + "\nCreando Dropbox object...\nsubiendo a la nube...") # muestra el mensaje de subiendo a la nube
  
        backup() # se ejecuta la funcion que sube el archivo a la nube

        self.label.setText("subiendo " + LOCALFILE + " a Dropbox como " + BACKUPPATH + "...\nConfirmando detalles\nLa lista de carpetas es : \n" + self.entry.name + "\nCreando Dropbox object...\nsubiendo a la nube...\nTerminado!") # muestra el mensaje de que se termino de subir a la nube
        
class adquirir(QtWidgets.QMainWindow):   #----------------------------------------------
    def __init__(self):                  # Se crea la clase adquirir con su constructor
        super(adquirir, self).__init__() #----------------------------------------------
        uic.loadUi('adquirir.ui', self) # se carga la interfaz desde un archivo .ui proveniente del Qt designer
        self.pushButton.clicked.connect(self.acquire) # se conecta el pushbutton con la funcion acquire
        self.pushButton_2.clicked.connect(self.detener) # se conecta el pushbutton 2 con la funcion detener
        self.pushButton_3.clicked.connect(self.guardar) # se conecta el pushbutton 3 con la funcion guarda
        self.permitir_detener = False # Es una variable boleana usada para permitir o no permitir la accion de un pushbutton
        self.permitir_guardar = False # Es una variable boleana usada para permitir o no permitir la accion de un pushbutton

    def guardar(self): # se crea la funcion guardar

        if self.permitir_guardar == True: # Solo sui la variable booleana es verdadera se ejecuta el codigo
            options = QFileDialog.Options()              # crea la opcion options y se configura para no usar
            options |= QFileDialog.DontUseNativeDialog   # el explorador de archivos por defecto sino usar el de QT
            fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName(self.ECG)","","All Files (*);;Text Files (*.txt)", options=options) # sirva para seleccionar una ruta y un nombre del archivo de forma grafica y lo almacena en filename

            if fileName != '': # si se selleciono una ruta se ejecuta lo siguiente
                savetxt(fileName,self.ECG); # guarda el archivo self.ECG como un archivo de texto en la ruta selleccionada anteriormente
    
    def acquire(self): # se crea la funcion acquire
        
        self.permitir_detener = True # desbloquea el boton detener
        self.permitir_guardar = False # bloquea el boton guardar
        self.arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=0.1) # hace uso del puerto serial y empieza a recibir datos
        self.ECG = np.ndarray((0),dtype=np.int); # se crea un array vacio

        self.timer = QtCore.QTimer(self) # se crea un timer
        self.timer.timeout.connect(self.acquire_asinc) # se conecta el timer con la funcion acquire_asinc, para que cada segundo la ejecute 1 vez
        self.timer.start(1000) # se ejecuta el timer y para a los 1000 segundos
        
    def acquire_asinc(self): # se crea la funcion que ejecutara el timer cada segundo
        
        datos = self.arduino.readlines(self.arduino.inWaiting()); # se leen los datos provenientes del arduino
        datos_por_leer = len(datos); # se obtiene el numero de datos leidos 
    
        print("Datos a convertir:" + str(len(datos))); # se muestra el numero de datos leidos

        valores_leidos = np.zeros(datos_por_leer,dtype = np.int); # se cre un array de zeros
    
        posicion = 0;                                                     #-------------------------
        for dato in datos:                                                # Transforma los datos
            try:                                                          # leidos en enteros, si
                valores_leidos[posicion] = int(dato.decode().strip());    # no se detecta un dato,
            except:                                                       # se reemplaza por una
                valores_leidos[posicion] = 0;                             # 0
                                                                          #
            posicion = posicion + 1;                                      #------------------------

        print(valores_leidos) # muestras los valores leidos ya convertidos a enteros
        self.ECG = np.append(self.ECG, valores_leidos) # agrega los datos leidos ya convertidos a enteros al final del array que contiene la señal
        t = np.linspace(0, 0.01*len(self.ECG), num = len(self.ECG)) # se crea un vector de tiempo, que empieza en 0, termina en la cantidad de datos de self. ECG 
        self.graphicsView.clear() # vacia el graphics view
        self.graphicsView.plot(t,self.ECG) # grafica la señal
        self.graphicsView.setYRange(0, 700) # modifica el rango predeterminado que se observa en el graficsview
        a = t[len(t)-1] # es un contador que depende del tamaño de t, se usa para que a medida que se grafic se mueva la señal
        self.graphicsView.setXRange(-6+a, a) # hace que solo se muestren 6 segundos y que la señal se desplaza a medida que se grafique

    def detener(self): # se crea la funcion detener
        
        if self.permitir_detener == True: # solo se ejecuta si la variable boleana es verdadera
            self.timer.stop() # para el timer
            self.arduino.close(); # cierra el puerto del arduino
            self.permitir_guardar = True # desbloquea el bton guardar
            self.permitir_detener = False # bloquea el boton detener

class filtrar(QtWidgets.QMainWindow):    #---------------------------------------------
    def __init__(self):                  # Se crea la clase filtrar on su constructor
        super(filtrar, self).__init__()  #--------------------------------------------
        uic.loadUi('filtrar.ui', self) # se carga la interfaz desde un archivo .ui proveniente del Qt designer
        self.pushButton.clicked.connect(self.cargar) # se conecta el pushbuton con la funcion cargar
        self.pushButton_2.clicked.connect(self.filtradoruido) # se conecta el pushbutton 2 con la funcion filtradoruido
        self.pushButton_4.clicked.connect(self.picosr) # se conecta el pushbutton 4 con la funcion picosr
        self.pushButton_5.clicked.connect(self.ritmo) # se conecta el pushbutton 5 con la funcion ritmo
        self.pushButton_3.clicked.connect(self.guardar2) # se conecta el pushbutton 3 con la funcion guardar
        self.fichero_actual = "" # se inicializa el string que contiene la ruta del archivo a guardar como un string vacio
        self.permitir_filtradoruido = False # Es una variable boleana usada para permitir o no permitir la accion de un pushbutton
        self.permitir_picosr = False # Es una variable boleana usada para permitir o no permitir la accion de un pushbutton
        self.permitir_ritmo = False # Es una variable boleana usada para permitir o no permitir la accion de un pushbutton
        self.permitir_guardar2 = False # Es una variable boleana usada para permitir o no permitir la accion de un pushbutton

    def cargar(self): # se crea la funcion guardar

        options = QFileDialog.Options()              # crea la opcion options y se configura para no usar
        options |= QFileDialog.DontUseNativeDialog   # el explorador de archivos por defecto sino usar el de QT
        nombre_fichero, _ = QFileDialog.getOpenFileName(self, "Abrir fichero", options=options) # se obtiene la ruta del archivo que se quiere abrir de manera grafica
        if nombre_fichero: # si se selecciono algo se ejecuta lo siguiente
            self.fichero_actual = nombre_fichero # se iguala la ruta a self.fichero_actual
            self.signal = np.loadtxt(self.fichero_actual); # se abre el archivo en la variable signal
            self.signal = self.signal[100:] # se eliminan los 100 primeros datos, ya que en estos se registra mucho ruido
            self.out = ecg.ecg(signal=self.signal, sampling_rate=100, show=False) # se filtra la señal y se almacena en el archivo self.out
            self.permitir_filtradoruido = True # habilita el boton filtrar ruido
            self.permitir_ritmo = True # habilita el boton ritmo cardiaco
            self.permitir_guardar2 = True # habilita el boton guardar
            self.graphicsView.clear() # limpia el graphicsview

    def filtradoruido(self): # se crea la funcion filtradoruido
        
        if self.permitir_filtradoruido == True: # ejecuta lo siguiente si la variable boleana es verdadera
            self.graphicsView.clear() # limpia el graphicsview
            self.graphicsView.plot(self.out[0], self.out[1]) # grafica la señal filtrada
            self.permitir_picosr = True # permite usar el boton picosr 
            self.graphicsView.setYRange(-50, 200) # adapta el rango mostrado en el eje Y para visualizar la señal 
            self.graphicsView.setXRange(0, 3) # adapta el rango mostrado en el eje X para visualizar la señal 

    def picosr(self): # Se crea la funcion picosr
        
        if self.permitir_picosr == True: # Se ejecuta lo siguiente si la variable boleana es verdadera
            amplir = [-100, 500] # se crea una lista con 2 valores, qe se usan para señalar en donde estan los picosr
            picos = self.out[2] # se iguala picos a self.ou[2] que es donde esta almacenado los tiempos en donde estan los picos r
            for i in picos: # Recorre el vector de donde estan los picos
                tpicos = [i/100, i/100] # se crea el tiempo donde estan los picosr dividiendo los valores de picos entre la frecuencia
                self.graphicsView.plot(tpicos, amplir, pen = 'r') # Se muestra una barra roja de -100 a 500 en el tiempo en donde se detecta el picor
                self.graphicsView.setYRange(-50, 200) # adapta el rango mostrado en el eje Y para visualizar la señal 
                self.graphicsView.setXRange(0, 3) # adapta el rango mostrado en el eje X para visualizar la señal

    def ritmo(self): # Se crea la funcion ritmo
        
        if self.permitir_ritmo == True: # Si la variable boleana es verdadera se ejecuta lo siguiente
            self.graphicsView.clear() # Se limpia el graphicsview
            self.graphicsView.plot(self.out[5], self.out[6]) # se grafica el ritmo cardiaco
            self.permitir_picosr = False # Se bloquea el boton picosr
            self.graphicsView.setYRange(min(self.out[6])-5, max(self.out[6])+5) # adapta el rango mostrado en el eje Y para visualizar la señal 
            self.graphicsView.setXRange(0, max(self.out[5])+1) # adapta el rango mostrado en el eje X para visualizar la señal

    def guardar2(self): # Se crea la funcion guardar2

        if self.permitir_guardar2 == True: # Si la vareable booleana es verdadera se ejecuta lo siguiente
            options = QFileDialog.Options()              # crea la opcion options y se configura para no usar
            options |= QFileDialog.DontUseNativeDialog   # el explorador de archivos por defecto sino usar el de QT
            fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName(self.out)","","All Files (*);;Numpy Files (*.npy)", options=options) # sirva para seleccionar una ruta y un nombre del archivo de forma grafica y lo almacena en filename

            if fileName != '': # si se selecciono la ruta, se ejecuta lo siguiente
                np.save(fileName,self.out); # Se guarda como archivo .npy
 
def main():                                   #-----------------------
    app = QtWidgets.QApplication(sys.argv)    #
    main = ECGmain()                          #
    main.show()                               # Ejecuta el codigo
    sys.exit(app.exec_())                     #
                                              #
if __name__ == '__main__':                    #
    main()                                    #---------------------
