import gzip
import shutil
import sqlite3
import tarfile
import zipfile
from datetime import datetime
from celery import Celery
import bz2

import psycopg2


appCelery = Celery('tasks' , backend = 'redis://192.168.0.4:6379/0', broker = 'redis://192.168.0.4:6379/0')
appCelery.conf.broker_url = 'redis://192.168.0.4:6379/0'
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
    with open(filename, mode='rb') as fin, bz2.open(new_path + '/' + zipname, 'wb') as fout:
        fout.write(fin.read())

@appCelery.task(name='tasks.comprimir_gz')
def comprimir_gz(filename, zipname, new_path):
    with open(filename, "rb") as fin, gzip.open(new_path + '/' + zipname, "wb") as fout:
        shutil.copyfileobj(fin, fout)

