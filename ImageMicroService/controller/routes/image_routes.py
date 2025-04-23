from flask_restx import Namespace, Resource, fields
from service.image_service import ImageService

# Namespace for image-related operations
ns = Namespace(
    'image',
    description='Operations to control and process images',
    path='/api/image'
)

# Service instance
image_service = ImageService()

# Models for Swagger documentation
command_model = ns.model('Command', {
    'command': fields.String(
        required=True,
        description='Command to execute',
        example='increase brightness',
        enum=['increase brightness', 'decrease brightness', 'change image']
    )
})

response_model = ns.model('Response', {
    'result': fields.String(
        description='Result of the operation',
        example='Brightness increased successfully'
    )
})

change_image_model = ns.model('ChangeImage', {
    'image_name': fields.String(
        required=True,
        description='Name of the new image',
        example='new_image.jpg'
    )
})

user_model = ns.model('User', {
    'username': fields.String(
        required=True,
        description='Username of the user',
        example='john_doe'
    ),
    'email': fields.String(
        required=True,
        description='Email of the user',
        example='john@example.com'
    )
})

save_image_model = ns.model('SaveImage', {
    'user_id': fields.Integer(
        required=True,
        description='ID of the user',
        example=1
    ),
    'image_name': fields.String(
        required=True,
        description='Name of the image file',
        example='my_image.jpg'
    )
})

error_model = ns.model('Error', {
    'error': fields.String(
        description='Error description',
        example='Invalid command'
    )
})

@ns.route('/test')
class TestResource(Resource):
    @ns.doc(
        'test_endpoint',
        description='Tests if the microservice is running correctly.',
        responses={
            200: 'Microservice running'
        }
    )
    def get(self):
        """Tests the availability of the microservice"""
        test_response_model = ns.model('TestResponse', {
            'message': fields.String(
                description='Confirmation message',
                example='Microservice running!'
            )
        })
        return ns.marshal({"message": "Microservice running!"}, test_response_model), 200

@ns.route('/user')
class UserResource(Resource):
    @ns.doc(
        'create_user',
        description='Creates a new user in the database.',
        responses={
            201: 'User created successfully',
            400: 'Error: User already exists or email in use'
        }
    )
    @ns.expect(user_model, validate=True)
    def post(self):
        """Creates a new user"""
        data = ns.payload
        if not data or "username" not in data or "email" not in data:
            return ns.marshal({"error": "Invalid user data"}, error_model), 400
        
        username = data["username"]
        email = data["email"]
        result = image_service.create_user(username, email)
        if "error" in result.lower():
            return ns.marshal({"error": result}, error_model), 400
        return ns.marshal({"result": result}, response_model), 201

@ns.route('/save-image')
class SaveImageResource(Resource):
    @ns.doc(
        'save_image',
        description='Saves a new image for a user in the database.',
        responses={
            201: 'Image saved successfully',
            400: 'Error: Invalid data or user not found'
        }
    )
    @ns.expect(save_image_model, validate=True)
    def post(self):
        """Saves a new image for a user"""
        data = ns.payload
        if not data or "user_id" not in data or "image_name" not in data:
            return ns.marshal({"error": "Invalid image data"}, error_model), 400
        
        user_id = data["user_id"]
        image_name = data["image_name"]
        result = image_service.save_image(user_id, image_name)
        if "error" in result.lower():
            return ns.marshal({"error": result}, error_model), 400
        return ns.marshal({"result": result}, response_model), 201

@ns.route('/command')
class CommandResource(Resource):
    @ns.doc(
        'handle_command',
        description=(
            'Processes a command to adjust the image, such as increasing or decreasing brightness. '
            'The command must be sent in the request body in JSON format.'
        ),
        responses={
            200: 'Command processed successfully',
            400: 'Error: Invalid or malformed command'
        }
    )
    @ns.expect(command_model, validate=True)
    def post(self):
        """Processes a command to adjust the image"""
        data = ns.payload
        if not data or "command" not in data:
            return ns.marshal({"error": "Invalid command"}, error_model), 400
        
        command = data["command"]
        result = image_service.adjust_brightness(command)
        if "error" in result.lower():
            return ns.marshal({"error": result}, error_model), 400
        return ns.marshal({"result": result}, response_model), 200

@ns.route('/command/<string:command>')
class CommandByPathResource(Resource):
    @ns.doc(
        'handle_command_by_path',
        description=(
            'Processes a command passed as a parameter in the URL. '
            'Useful for quick tests or simple integrations.'
        ),
        params={
            'command': 'Command to execute (e.g., "increase brightness")'
        },
        responses={
            200: 'Command processed successfully',
            400: 'Error: Invalid command'
        }
    )
    def get(self, command):
        """Processes a command passed in the URL"""
        if not command:
            return ns.marshal({"error": "Invalid command"}, error_model), 400
        
        result = image_service.adjust_brightness(command)
        if "error" in result.lower():
            return ns.marshal({"error": result}, error_model), 400
        return ns.marshal({"result": result}, response_model), 200

@ns.route('/change-image')
class ChangeImageResource(Resource):
    @ns.doc(
        'change_image',
        description='Changes the current image being processed.',
        responses={
            200: 'Image changed successfully',
            400: 'Error: Invalid image name'
        }
    )
    @ns.expect(change_image_model, validate=True)
    def post(self):
        """Changes the current image"""
        data = ns.payload
        if not data or "image_name" not in data:
            return ns.marshal({"error": "Invalid image name"}, error_model), 400
        
        image_name = data["image_name"]
        result = image_service.change_image(image_name)
        if "error" in result.lower():
            return ns.marshal({"error": result}, error_model), 400
        return ns.marshal({"result": result}, response_model), 200