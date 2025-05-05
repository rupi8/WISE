from extensions import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    images = db.relationship('Image', backref='user', lazy=True)

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"

class Image(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    image_name = db.Column(db.String(120), nullable=False)
    brightness_level = db.Column(db.Float, default=1.0)
    image_data = db.Column(db.LargeBinary, nullable=True)  # Campo para almacenar la imagen

    def __repr__(self):
        return f"<Image(image_name='{self.image_name}', brightness_level={self.brightness_level})>"

def save_image_to_db(image_path, user_id, image_name, brightness_level=1.0):
    from models.models import Image
    from controller.app import db

    # Leer la imagen en modo binario
    with open(image_path, 'rb') as file:
        image_binary = file.read()

    # Crear un nuevo registro de imagen
    new_image = Image(
        user_id=user_id,
        image_name=image_name,
        brightness_level=brightness_level,
        image_data=image_binary
    )

    # Guardar en la base de datos
    db.session.add(new_image)
    db.session.commit()
    print(f"Imagen '{image_name}' guardada en la base de datos.")

def retrieve_image_from_db(image_id, output_path):
    from models.models import Image

    # Consultar la imagen por ID
    image = Image.query.get(image_id)
    if image and image.image_data:
        # Guardar la imagen en un archivo
        with open(output_path, 'wb') as file:
            file.write(image.image_data)
        print(f"Imagen guardada en '{output_path}'.")
    else:
        print("Imagen no encontrada o no tiene datos.")