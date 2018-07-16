# -*- coding: utf-8 -*-
"""
Created on Tue Jul 10 19:35:33 2018

@author: solis

Se asignan nombres a ciertas variables; el nombre de la variable, parte
    izquierda del signo =, no se puede cambiar, pero s� el contenido situado
    a la derecha del signo =.
"""
# PARAMETERS

# fichero xml de configuracion de proyectos
# nombre recomndado 'XYplus.xml'. Se puede asignarle otro nombre, pero el
# prefijo 'XYplus' debe estar siempre presente
# Se puede poner asignarle un directorio si se incluye en el nombre de la
# variable; en ese caso poner una r delante, por ej:
# r'C:\Users\solis\Documents\work\VM\umbrales_out\XYplus_alonso.xml'
f_xml = 'XYplus.xml'

# Directorio de salida; nombre de un directorio dentro de r'...'
dir_out = r'C:\Users\solis\Documents\work\VM\umbrales_out'

# grabar lineas horizontales (1: s�, 0: no)
show_hl = 1

# grabar series auxiliares upper plot
show_aux = 0

# rangos de fechas (formato dd/mm/yyyy) date1<date2
# date_2 puede tener el valor 'now', en cuyo caso se sustituye internamente
# por la fecha de ejecuci�n
date_1 = '1/1/1900'
date_2 = 'now'
