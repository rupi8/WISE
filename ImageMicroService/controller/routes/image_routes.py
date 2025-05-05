from flask_restx import Namespace, Resource, fields
from service.image_service import ImageService
from models.models import User, Image  # Import the User and Image models

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
    ),
    'image_path': fields.String(
        required=True,
        description='Path to the image file',
        example='/path/to/image.png'
    ),
    'brightness_level': fields.Float(
        description='Initial brightness level',
        example=1.0
    )
})

adjust_brightness_model = ns.model('AdjustBrightness', {
    'image_id': fields.Integer(
        required=True,
        description='ID of the image',
        example=1
    ),
    'adjustment': fields.String(
        required=True,
        description='Adjustment type',
        example='increase',
        enum=['increase', 'decrease']
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

    @ns.doc(
        'get_users',
        description='Retrieves all users from the database.',
        responses={
            200: 'List of users retrieved successfully',
            500: 'Error retrieving users'
        }
    )
    def get(self):
        """Retrieves all users from the database"""
        try:
            users = User.query.all()
            users_list = [
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email
                }
                for user in users
            ]
            return {"users": users_list}, 200
        except Exception as e:
            return {"error": str(e)}, 500

@ns.route('/save-image')
class SaveImageResource(Resource):
    @ns.doc(
        'save_image',
        description='Saves an image to the database.',
        responses={
            201: 'Image saved successfully',
            400: 'Error saving image'
        }
    )
    @ns.expect(save_image_model, validate=True)
    def post(self):
        """Saves an image to the database"""
        data = ns.payload
        return image_service.save_image(
            data['image_path'], data['user_id'], data['image_name'], data.get('brightness_level', 1.0)
        )

@ns.route('/adjust-brightness')
class AdjustBrightnessResource(Resource):
    @ns.expect(adjust_brightness_model, validate=True)
    def post(self):
        """Adjusts the brightness of an image."""
        data = ns.payload
        return image_service.adjust_brightness(data['image_id'], data['adjustment'])

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
        result = image_service.change_image(data['image_name'])
        return ns.marshal({"result": result}, response_model), 200


@ns.route('/images')
class ImagesResource(Resource):
    @ns.doc(
        'get_images',
        description='Retrieves all images stored in the database.',
        responses={
            200: 'List of images retrieved successfully',
            500: 'Error retrieving images'
        }
    )
    def get(self):
        """Retrieves all images from the database"""
        try:
            images = Image.query.all()
            images_list = [
                {
                    "id": image.id,
                    "user_id": image.user_id,
                    "image_name": image.image_name,
                    "brightness_level": image.brightness_level
                }
                for image in images
            ]
            return {"images": images_list}, 200
        except Exception as e:
            return {"error": str(e)}, 500