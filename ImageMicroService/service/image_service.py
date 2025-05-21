from models.models import User, Image
from extensions import db
from scripts_tcp.Server_Code1 import main
from controller.shared_state import clients

class ImageService:
    def __init__(self):
        self.current_image = None  # Imagen actual (objeto Image)

    def create_user(self, username, email):
        """Creates a new user in the database."""
        if User.query.filter_by(username=username).first():
            return "User already exists"
        if User.query.filter_by(email=email).first():
            return "Email already in use"

        new_user = User(username=username, email=email)
        db.session.add(new_user)
        db.session.commit()
        return "User created successfully"

    def save_image(self, image_path, user_id, image_name, brightness_level=1.0):
        """Saves an image to the database."""
        with open(image_path, 'rb') as file:
            image_binary = file.read()

        new_image = Image(
            user_id=user_id,
            image_name=image_name,
            brightness_level=brightness_level,
            image_data=image_binary
        )
        db.session.add(new_image)
        db.session.commit()
        return f"Image '{image_name}' saved successfully"

    def adjust_brightness(self, image_id, adjustment):
        """Adjusts the brightness of an image."""
        """image = Image.query.get(image_id)"""
        image = Image.query.filter_by(id=image_id).first()
        """ajustar els atributs per el main"""
        if adjustment == "increase brightness":
            main(clients, inputString = "INCREASE")
        elif adjustment == "decrease brightness":
            main(clients, inputString = "DECREASE")

        db.session.commit()
        return f"Brightness adjusted to {image}"

    def change_image(self, image_name):
        """Changes the current image."""
        image = image_name
        if image == None:
            return "Image not found"
        main(clients, inputString=f"SEND {image_name}")
        return f"Image changed to {image_name}"
    
    def gesture_adjust(self, command):
        print(f"Gesture command received: {command}")
        return "Nice command!"
    
    def control_screen(self, command):
        """Controls the screen state based on the text provided."""
        if command == "turn on":
            main(clients, inputString=f"TEXT {command}")
            print("(screen ON)")
            return "Screen turned ON"
        elif command == "turn off":
            main(clients, inputString=f"TEXT {command}")
            print("(screen OFF)")
            return "Screen turned OFF"
        else:
            return "Error: Invalid text value. Use 'ON' or 'OFF'."
