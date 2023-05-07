import gzip
import shutil
import sqlite3
import tarfile
import zipfile
from datetime import datetime
from celery import Celery
import bz2
import smtplib
import ssl

import psycopg2

from apirest.DemoCloudStorage import write_read


appCelery = Celery('tasks' , backend = 'redis://127.0.0.1/0', broker = 'redis://127.0.0.1:6379/0')
appCelery.conf.broker_url = 'redis://127.0.0.1:6379/0'
# Creamos una tarea llamada sumar_numeros usando el decorador @app.task
# Se imprime un mensaje con la fecha simulando un LOG

def enviarCorreo(email_to):
    # port number and server name
    smtp_port = 587                     #standard secure SMTP port
    smtp_server = "smtp.gmail.com"      #Google SMTP Server
    email_from = "" #Se debe crear cuenta en gmail para enviar correos, la anterior fue utilizada para enviar phising.
    pswd = ""
    # content of message
    message1 = "Por favor ingrese a nuestra plataforma para descargar su archivo."
    subject = "Sus archivos comprimidos estan listos"
    message = 'Subject: {}\n\n{}'.format(subject, message1)
    simple_email_context = ssl.create_default_context()
    try: 
        print("Conectando al servidor...")
        TIE_server = smtplib.SMTP(smtp_server, smtp_port)
        TIE_server.starttls(context=simple_email_context)
        TIE_server.login(email_from, pswd)
        print("Conectado al servidor ...")
        print()
        print(f"Enviando notificacion a - {email_to}")
        TIE_server.sendmail(email_from, email_to, message)
        print(f"La notificacion fue enviada a - {email_to} ")
    except Exception as e:
        print(e)
    finally: 
        TIE_server.quit()
    return "función enviarCorreo terminada"

@appCelery.task(name='tasks.comprimir')
def comprimir(filename, zipname, new_path, email_to, usuario_tarea, filenameCloud):
    print ('/n-> Se va a comprimir el archivo: {}'.format(filename))
    zfile = zipfile.ZipFile(new_path + '/' + zipname, 'w')
    zfile.write(filename, compress_type = zipfile.ZIP_DEFLATED)
    zfile.close()
    write_read('cloudentrega4', 'archivosComprimidos/'+usuario_tarea+'/'+zfile)
    enviarCorreo(email_to)
    print ('/n-> El archivo comprimido se copió a : {}'.format(new_path))

@appCelery.task(name='tasks.comprimir_bz2')
def comprimir_bz2(filename, zipname, new_path, email_to, usuario_tarea, filenameCloud):
    with open(filename, mode='rb') as fin, bz2.open(new_path + '/' + zipname, 'wb') as fout:
        fout.write(fin.read())
        write_read('cloudentrega4', 'archivosComprimidos/'+usuario_tarea+'/'+fout)
        enviarCorreo(email_to)
        print ('/n-> El archivo comprimido se copió a : {}'.format(new_path))

@appCelery.task(name='tasks.comprimir_gz')
def comprimir_gz(filename, zipname, new_path, email_to, usuario_tarea, filenameCloud):
    with open(filename, "rb") as fin, gzip.open(new_path + '/' + zipname, "wb") as fout:
        shutil.copyfileobj(fin, fout)
        write_read('cloudentrega4', 'archivosComprimidos/'+usuario_tarea+'/'+fout)    
        enviarCorreo(email_to)
        print ('/n-> El archivo comprimido se copió a : {}'.format(new_path))




