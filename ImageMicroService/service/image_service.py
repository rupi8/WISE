class ImageService:
    def __init__(self):
        self.current_image = "image.jpg"

    def adjust_brightness(self, command):
        if command.lower() == "subir brillo":
            return "Brillo subido con éxito"
        elif command.lower() == "bajar brillo":
            return "Brillo bajado con éxito"
        else:
            return "Comando no reconocido"

    def change_image(self, image_name):
        if not image_name:
            return "Nombre de imagen no válido"
        self.current_image = image_name
        return f"Imagen cambiada a {image_name}"