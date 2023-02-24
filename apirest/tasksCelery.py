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

@appCelery.task(name='tasks.enviarCorreo')
def enviarCorreo(email_to):
    # port number and server name
    smtp_port = 587                     #standard secure SMTP port
    smtp_server = "smtp.gmail.com"      #Google SMTP Server
    email_from = "cloud2023g1@gmail.com"
    pswd = "rzvszrwcvwumbriy"
    # content of message
    message1 = "Por favor ingrese a nuestra plataforma para descargar su archivo."
    subject = "Sus archivos comprimidos están listos"
    message = 'Subject: {}\n\n{}'.format(subject, message1)
    simple_email_context = ssl.create_default_context()
    try: 
        print("Conectando al servidor...")
        TIE_server = smtplib.SMTP(smtp_server, smtp_port)
        TIE_server.starttls(context=simple_email_context)
        TIE_server.login(email_from, pswd)
        print("Conectado al servidor ...")
        print()
        print(f"Enviando notificación a - {email_to}")
        TIE_server.sendmail(email_from, email_to, message)
        print(f"La notificación fue enviada a - {email_to} ")
    except Exception as e:
        print(e)
    finally: 
        TIE_server.quit()
    return "función enviarCorreo terminada"


