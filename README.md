# Cloud_Entrega1

Estudiantes:

-m.zapatal2@uniandes.edu.co
-fo.ramirez50@uniandes.edu.co
-pa.calvache@uniandes.edu.co
-da.vasquez11@uniandes.edu.co

Descripcion de los endpoints:

1. /api/auth/signup (POST)
    Permite crear una cuenta de usuario, con los campos usuario, correo electrónico y
    contraseña. El usuario y el correo electrónico deben ser únicos en la plataforma, la
    contraseña debe seguir unos lineamientos mínimos de seguridad, además debe ser
    Universidad de los Andes
    solicitada dos veces para que el usuario confirme que ingresa la contraseña
    correctamente. 

2. /api/auth/login (POST)
    Permite recuperar el token de autorización para consumir los recursos del API
    suministrando un nombre de usuario y una contraseña correcta de una cuenta
    registrada.

3. /api/tasks (GET)
    Permite recuperar todas las tareas de conversión de un usuario autorizado en la
    aplicación.

4. /api/tasks (POST)
    Permite crear una nueva tarea de conversión de formatos. El usuario requiere
    autorización.

5. /api/tasks/<int:id_task> (GET)
    Permite recuperar la información de una tarea en la aplicación. El usuario requiere
    autorización.

6. /api/tasks/<int:id_task> (DELETE)
    Permite eliminar una tarea en la aplicación. El usuario requiere autorización.

7. /api/files/<filename> (GET)
    Permite recuperar el archivo original o procesado.

8. /api/files (POST)
    Permite cargar archivos a una ruta especifica.

9. /api/files/delete/<string:filename> (DELETE)
    Permite eliminar archivos de una ruta especifica.

10. /api/files/comprimir (POST)
    Permite comprimir archivos de 3 maneras diferentes y enviar correos de confirmacion.


Ejecutar el codigo:
Recordar que se debe correro los containers en docker para tener los servicios de postgres, pg4admin y redis.
(Abrir terminal de comandos)

1. clonar el repositorio https://github.com/mzapatal2/Cloud_Entrega1.git
2. crear un ambiente de python python -m <nombre ambiente> .venv
3. Activar el ambiente .\<nombre ambiente>\Scripts\activate.ps1
4. Instalar requirements.txt pip install -r requirements.txt
5. Correr los workers: 
    -dirigirse al directorio apirest cd ./apirest
    -celery -A tasksCelery worker --loglevel=INFO --pool=eventlet
6. abrir otra terminal de comandos y correr la aplicacion:
    -$env:FLASK_APP="apirest"
    -$env:FLASK_DEBUG=1
    -flask run --host=0.0.0.0
7. dirigirse a POSTMAN para probar los endpoints.


En el archivo Entrega1Cloud.postman_collection.json encontrara la coleccion para cargarla a POSTMAN y realizar pruebas.