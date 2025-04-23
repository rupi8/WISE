from repository.database import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    
    # Relación con las imágenes
    images = db.relationship('Image', backref='user', lazy=True)

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"

class Image(db.Model):
    __tablename__ = 'images'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    image_name = db.Column(db.String(100), nullable=False)
    brightness_level = db.Column(db.Float, default=1.0)  # Nivel de brillo (1.0 = normal)

    def __repr__(self):
        return f"<Image(image_name='{self.image_name}', brightness_level={self.brightness_level})>"