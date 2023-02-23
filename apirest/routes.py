from apirest import api
from apirest.views import RecursoArchivo, RecursoCarga, RecursoComprimir, RecursoMiTask, RecursoRegistro, RecursoLogin, RecursoDelete, RecursoTasks

api.add_resource(RecursoRegistro, '/api/auth/signup')
api.add_resource(RecursoLogin, '/api/auth/login')
api.add_resource(RecursoTasks, '/api/tasks')
api.add_resource(RecursoMiTask, '/api/tasks/<int:id_task>')
api.add_resource(RecursoArchivo, '/api/files/<string:filename>')
api.add_resource(RecursoCarga, '/api/files')
api.add_resource(RecursoDelete, '/api/files/delete/<string:filename>')
api.add_resource(RecursoComprimir, '/api/files/comprimir')