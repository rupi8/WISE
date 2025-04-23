from repository.database import db
from models.models import User, Image

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

    def save_image(self, user_id, image_name):
        """Saves a new image for a user in the database."""
        user = User.query.get(user_id)
        if not user:
            return "User not found"
        
        new_image = Image(user_id=user_id, image_name=image_name, brightness_level=1.0)
        db.session.add(new_image)
        db.session.commit()
        self.current_image = new_image
        return f"Image {image_name} saved for user {user_id}"

    def adjust_brightness(self, command):
        """Adjusts the brightness of the current image and updates the database."""
        if not self.current_image:
            return "No image selected"

        if command.lower() == "increase brightness":
            self.current_image.brightness_level += 0.1
            db.session.commit()
            return "Brightness increased successfully"
        elif command.lower() == "decrease brightness":
            self.current_image.brightness_level -= 0.1
            if self.current_image.brightness_level < 0:
                self.current_image.brightness_level = 0
            db.session.commit()
            return "Brightness decreased successfully"
        else:
            return "Unrecognized command"

    def change_image(self, image_name):
        """Changes the current image by selecting an existing image from the database."""
        if not image_name:
            return "Invalid image name"
        
        image = Image.query.filter_by(image_name=image_name).first()
        if not image:
            return "Image not found"
        
        self.current_image = image
        return f"Image changed to {image_name}"