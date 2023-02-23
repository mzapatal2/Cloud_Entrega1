import sqlite3
import zipfile
from datetime import datetime
from celery import Celery
import bz2

import psycopg2


appCelery = Celery('tasks' , backend = 'redis://192.168.0.13:6379/0', broker = 'redis://192.168.0.13:6379/0')
appCelery.conf.broker_url = 'redis://192.168.0.13:6379/0'
# Creamos una tarea llamada sumar_numeros usando el decorador @app.task
# Se imprime un mensaje con la fecha simulando un LOG

@appCelery.task(name='tasks.comprimir')
def comprimir(filename, zipname, new_path):
    print ('/n-> Se va a comprimir el archivo: {}'.format(filename))
    zfile = zipfile.ZipFile(new_path + '/' + zipname, 'w')
    zfile.write(filename, compress_type = zipfile.ZIP_DEFLATED)
    zfile.close()
    print ('/n-> El archivo comprimido se copió a : {}'.format(new_path))

@appCelery.task(name='tasks.comprimir_bz2')
def comprimir_bz2(filename, zipname, new_path):
    f_in = open(filename, "rb")
    f_out.write(bz2.compress(f_in.read()))
    f_out = open(new_path + '/' + zipname, "wb")
    f_out.close()
    f_in.close()
