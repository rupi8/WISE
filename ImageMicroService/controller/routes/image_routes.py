from flask_restx import Namespace, Resource, fields
from service.image_service import ImageService

# Namespace para operaciones relacionadas con imágenes
ns = Namespace(
    'image',
    description='Operaciones para controlar y procesar imágenes',
    path='/api/image'
)

# Instancia del servicio
image_service = ImageService()

# Modelos para la documentación Swagger
command_model = ns.model('Command', {
    'command': fields.String(
        required=True,
        description='Comando a ejecutar',
        example='subir brillo',
        enum=['subir brillo', 'bajar brillo', 'cambiar imagen']
    )
})

response_model = ns.model('Response', {
    'result': fields.String(
        description='Resultado de la operación',
        example='Brillo subido con éxito'
    )
})

change_image_model = ns.model('Response', {
    'result': fields.String(
        description='Resultado de la operación',
        example='Imagen cambiada'
    )
})


error_model = ns.model('Error', {
    'error': fields.String(
        description='Descripción del error',
        example='Comando no válido'
    )
})

@ns.route('/test')
class TestResource(Resource):
    @ns.doc(
        'test_endpoint',
        description='Prueba si el microservicio está funcionando correctamente.',
        responses={
            200: 'Microservicio funcionando'
        }
    )
    @ns.marshal_with(ns.model('TestResponse', {
        'message': fields.String(
            description='Mensaje de confirmación',
            example='Microservicio funcionando!'
        )
    }), code=200)
    def get(self):
        """Prueba la disponibilidad del microservicio"""
        return {"message": "Microservicio funcionando!"}, 200

@ns.route('/command')
class CommandResource(Resource):
    @ns.doc(
        'handle_command',
        description=(
            'Procesa un comando para ajustar la imagen, como subir o bajar el brillo. '
            'El comando debe ser enviado en el cuerpo de la petición en formato JSON.'
        ),
        responses={
            200: 'Comando procesado con éxito',
            400: 'Error: Comando no válido o mal formado'
        }
    )
    @ns.expect(command_model, validate=True)
    @ns.marshal_with(response_model, code=200, description='Comando procesado')
    @ns.marshal_with(error_model, code=400, description='Error en la solicitud')
    def post(self):
        """Procesa un comando para ajustar la imagen"""
        data = ns.payload  # Obtiene el cuerpo JSON de la petición
        if not data or "command" not in data:
            return {"error": "Comando no válido"}, 400
        
        command = data["command"]
        result = image_service.adjust_brightness(command)
        return {"result": result}, 200

@ns.route('/command/<string:command>')
class CommandByPathResource(Resource):
    @ns.doc(
        'handle_command_by_path',
        description=(
            'Procesa un comando pasado como parámetro en la URL. '
            'Útil para pruebas rápidas o integraciones simples.'
        ),
        params={
            'command': 'Comando a ejecutar (ej. "subir brillo")'
        },
        responses={
            200: 'Comando procesado con éxito',
            400: 'Error: Comando no válido'
        }
    )
    @ns.marshal_with(response_model, code=200, description='Comando procesado')
    @ns.marshal_with(error_model, code=400, description='Error en la solicitud')
    def get(self, command):
        """Procesa un comando pasado en la URL"""
        if not command:
            return {"error": "Comando no válido"}, 400
        
        result = image_service.adjust_brightness(command)
        return {"result": result}, 200
    
    change_image_model = ns.model('ChangeImage', {
    'image_name': fields.String(
        required=True,
        description='Nombre de la nueva imagen',
        example='new_image.jpg'
    )
})

@ns.route('/change-image')
class ChangeImageResource(Resource):
    @ns.doc(
        'change_image',
        description='Cambia la imagen actual que se está procesando.',
        responses={
            200: 'Imagen cambiada con éxito',
            400: 'Error: Nombre de imagen no válido'
        }
    )
    @ns.expect(change_image_model, validate=True)
    @ns.marshal_with(response_model, code=200, description='Imagen cambiada')
    @ns.marshal_with(error_model, code=400, description='Error en la solicitud')
    def post(self):
        """Cambia la imagen actual"""
        data = ns.payload
        if not data or "image_name" not in data:
            return {"error": "Nombre de imagen no válido"}, 400
        
        image_name = data["image_name"]
        result = image_service.change_image(image_name)
        return {"result": result}, 200