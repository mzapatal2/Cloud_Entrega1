from datetime import datetime, timedelta
import os
from os import getcwd
from flask import Response, flash, render_template, request, current_app, send_from_directory
import psycopg2
from werkzeug.utils import secure_filename
from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager
from flask_restful import Api

from apirest import api, db
from apirest.models import Task, TaskSchema, Usuario, task_schema, tasks_schema
from apirest.tasksCelery import comprimir, comprimir_bz2, comprimir_gz

from google.cloud import storage

#OJO hay que revisar ruta
PATH_FILE = getcwd() + "/archivos/users/"
PATH_FILE_COMPRESS = getcwd() + "/archivosComprimidos/users/"

def crear_carpeta(usuario):
    try:
        file = PATH_FILE+usuario
        fileCompress = PATH_FILE_COMPRESS+usuario
        os.makedirs(file)
        os.makedirs(fileCompress)
    except print(0):
        pass

def write_read(bucket_name, blob_name):
    """Write and read a blob from GCS using file-like IO"""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"

    # The ID of your new GCS object
    # blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    # Mode can be specified as wb/rb for bytes mode.
    # See: https://docs.python.org/3/library/io.html
    with blob.open("w") as f:
        f.write("Hello world")

    with blob.open("r") as f:
        print(f.read())


'''
Recurso que administra el servicio de login
'''
class RecursoLogin(Resource):
    def post(self):
        request.get_json(force=True)
        usuario = Usuario.query.get(request.json['usuario'])
        
        if usuario is None:
            return {'message':'El email ingresado no está registrado'}, 400
        
        if not usuario.verificar_clave(request.json['password']):
            return {'message': 'Contraseña incorrecta'}, 400
        
        try:
            access_token = create_access_token(identity = request.json['usuario'], expires_delta = timedelta(days = 1))
            return {
                'message':'Sesion iniciada',
                'access_token':access_token
            }
        
        except:
            return {'message':'Ha ocurrido un error'}, 500
    
'''
Recurso que administra el servicio de registro
'''
class RecursoRegistro(Resource):
    def post(self):
        if Usuario.query.filter_by(email=request.json['email']).first() is not None:
            return {'message': f'El correo({request.json["email"]}) ya está registrado'}, 400
        
        if request.json['email'] == '' or request.json['password'] == '' or request.json['password1'] == '' or request.json['usuario'] == '':
            return {'message': 'Campos invalidos'}, 400
        
        if request.json['password'] != request.json['password1']:
            return {'message': 'contraseña no coincide'}, 400
        
        nuevo_usuario = Usuario(
            email = request.json['email'],
            password = request.json['password'],
            usuario = request.json['usuario'],
        )
        
        nuevo_usuario.hashear_clave()

        try:
            db.session.add(nuevo_usuario)
            db.session.commit()
            access_token = create_access_token(identity = request.json['email'], expires_delta = timedelta(days = 1))
            crear_carpeta(nuevo_usuario.usuario)
            storage_client = storage.Client()
            write_read('cloudentrega4', 'archivos/'+nuevo_usuario.usuario+'/')
            write_read('cloudentrega4', 'archivosComprimidos/'+nuevo_usuario.usuario+'/')
            return {
                'message': f'El correo {request.json["email"]} ha sido registrado',
                'access_token': access_token 
            }

        except:
            return {'message':'Ha ocurrido un error'}, 500

    
class RecursoTasks(Resource):
    @jwt_required()
    def get(self):        
        usuario = get_jwt_identity() 
        args = request.args
        order = args.get('order')
        max = args.get('max')      
        if int(order) == 0:
            tasks = Task.query.filter_by(usuario_task = usuario).order_by(db.asc(Task.id_task)).limit(int(max)).all()
        if int(order) == 1:
            tasks = Task.query.filter_by(usuario_task = usuario).order_by(db.desc(Task.id_task)).limit(int(max)).all()
        return tasks_schema.dump(tasks)   
    
    @jwt_required()
    def post(self):
        usuario = get_jwt_identity()

        if Task.query.filter_by(filename=request.json['filename']).first() is not None:
            return {'message': f'El filename({request.json["filename"]}) ya está registrado'}, 400
        
        new_task = Task(
            filename = request.json['filename'],
            rutaArchivo = PATH_FILE,
            rutaCompresion = PATH_FILE_COMPRESS,
            status = "uploaded",
            tipoConversion = request.json['tipoConversion'],
            fechaCarga = datetime.now(),         
            usuario_task = usuario
            )
        
        db.session.add(new_task)
        db.session.commit()
        
        return task_schema.dump(new_task)

'''
Recurso que administra el servicio de una publicación (Detail)
'''

class RecursoMiTask(Resource):
    @jwt_required()
    def get(self, id_task):
        usuario = get_jwt_identity()
        task = Task.query.get(id_task)

        if task is None:
            return {'message':'La tarea no está registrada'}, 400
        else:
            return task_schema.dump(task)
        
    @jwt_required()
    def put(self, id_task):
        email = get_jwt_identity()
        task = Task.query.get_or_404(id_task)        
        
        if Task.usuario_task != email:
            return {'message':'No tiene acceso a esta tarea'}, 401

        if 'filename' in request.json:
            Task.filename = request.json['filename']
        
        if 'status' in request.json:
            Task.status = request.json['status']

        if 'tipoConversion' in request.json:
            Task.tipoConversion = request.json['tipoConversion']

        db.session.commit()
        return TaskSchema.dump(task)

    @jwt_required()
    def delete(self, id_task):
        usuario = get_jwt_identity()
        task = Task.query.get(id_task)
        
        if task is None:
            return {'message':'La tarea no está registrada'}, 400
        else:
            db.session.delete(task)
            db.session.commit()      
            return 'El resgistro ha sido eliminado'
    
class RecursoArchivo(Resource):
    @jwt_required()
    def get(self, filename):
        usuario = get_jwt_identity()
        extension = filename.split(".")[-1]
        if extension.lower() in ('rar', 'zip', '7z'):
            return send_from_directory(PATH_FILE_COMPRESS+usuario, path=filename, as_attachment=True)
        else:
            return send_from_directory(PATH_FILE+usuario, path=filename, as_attachment=True)
        
class RecursoDelete(Resource): 
    @jwt_required()
    def delete(self, filename):
        usuario = get_jwt_identity()
        extension = filename.split(".")[-1]
        try:
            if extension.lower() in ('rar', 'zip', '7z'):
                fileCompress = PATH_FILE_COMPRESS+usuario+'/'+filename
                os.remove(fileCompress)
            else:
                file = PATH_FILE+usuario+'/'+filename
                os.remove(file)
            return {'message':'Archivo eliminado'}
        except Exception as e:
            return {'message':'El Archivo no existe'}
    
class RecursoCarga(Resource):
    @jwt_required()
    def post(self):
        usuario = get_jwt_identity()
        try:
            if 'file' not in request.files:
                print('No file part')
            file = request.files['file']
            if file.filename == '':
                print('No selected file')
            storage_client = storage.Client()
            write_read('cloudentrega4', 'archivos/'+usuario+'/'+file.filename)
            #write_read('cloudentrega4', file.filename)
            file.save(PATH_FILE + usuario +'/'+ file.filename)
            return {'message':'Archivo Cargado'}
        except Exception as e:
            pass

class RecursoComprimir(Resource):
    def post(self):
        tasksUploaded = Task.query.filter_by(status = 'uploaded').all()
        for task in tasksUploaded:
            id_task = task.id_task
            usuario_tarea = task.usuario_task
            tipoConversion = task.tipoConversion
            filename = task.filename
            nombreArchivo = filename.split('.')[0]

            try:
                a = "/home/chechojuli/Cloud_Entrega1/archivos/users/"+usuario_tarea+"/"+filename
                b = nombreArchivo+"."+tipoConversion
                c = "/home/chechojuli/Cloud_Entrega1/archivos/users/"+usuario_tarea
                email_to = Usuario.query.filter_by(usuario = usuario_tarea).first()
                d = email_to.email
                #d = 'paulcalvache3000@gmail.com'
                if tipoConversion == 'zip':
                    comprimir.delay(a, b, c, d, usuario_tarea, filename)
                if tipoConversion == 'bz2':
                    comprimir_bz2.delay(a, b, c, d, usuario_tarea, filename)
                if tipoConversion == 'gz':
                    comprimir_gz.delay(a, b, c, d, usuario_tarea, filename)
                conn = psycopg2.connect(host="34.29.121.22", database="libros", user="postgres",password="libros",port="5432")
                with conn.cursor() as cursor:
                    query = "UPDATE public.task SET status='processed' WHERE id_task ={}".format(id_task)
                    cursor.execute(query)
                    conn.commit()
                    conn.close()

            except Exception as e:
                return {'message':'El Archivo no se pudo comprimir'+str(e)}
            
        return {'message':'El Archivo se comprimio'}
    

class RecursoRegistroWeb(Resource):
    def get(self):
        return Response(render_template("sing_up.html"))
    
class RecursoLoginWeb(Resource):
    def get(self):
        return Response(render_template("login.html"))      

class RecursoTasksWeb(Resource):
    def get(self):
        return Response(render_template("task.html")) 
    
class RecursoUploadWeb(Resource):
    def get(self):
        return Response(render_template("upload.html"))
    
class RecursoindexWeb(Resource):
    def get(self):
        return Response(render_template("index.html"))
