
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def rgb888_to_rgb565(image_array):
    r = image_array[:, :, 0].astype(np.uint16) >> 3
    g = image_array[:, :, 1].astype(np.uint16) >> 2
    b = image_array[:, :, 2].astype(np.uint16) >> 3
    rgb565 = (r << 11) | (g << 5) | b
    return rgb565

def wrap_text(text, font, draw, max_width):
    """Divide el texto en múltiples líneas si es necesario."""
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        if draw.textsize(test_line, font=font)[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)
    return lines

def text_to_image(text, width=320, height=64, font_size=32,
                  output_folder="/home/iot/Desktop/PAE/intento1/matrixes"):
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default()

    # Reducir un poco el tamaño si el texto completo en una línea no cabe
    text_width, _ = draw.textsize(text, font=font)
    while text_width > width * 1.2 and font_size > 10:
        font_size -= 2
        font = ImageFont.truetype(font_path, font_size)
        text_width, _ = draw.textsize(text, font=font)

    # Dividir el texto en líneas
    lines = wrap_text(text, font, draw, width)

    # Calcular altura total del texto
    line_height = font.getbbox("Ag")[3] + 2  # alto de una línea
    total_text_height = line_height * len(lines)

    # Posición Y inicial: centrado si hay pocas líneas, arriba si muchas
    if total_text_height < height:
        y = (height - total_text_height) // 2
    else:
        y = 0

    # Dibujar cada línea
    for line in lines:
        line_width = draw.textsize(line, font=font)[0]
        x = (width - line_width) // 2  # centrar horizontalmente
        draw.text((x, y), line, font=font, fill="black")
        y += line_height

    img_array = np.array(img, dtype=np.uint8)
    matrix = rgb888_to_rgb565(img_array)
    matrix_list = matrix.tolist()

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    file_path = os.path.join(output_folder, "image_matrix_text.py")
    with open(file_path, "w") as f:
        f.write(f"# Image matrix for text: '{text}' (RGB565 format)\n")
        f.write("image_matrix = " + repr(matrix_list) + "\n")

    print(f"Matrix for text '{text}' saved at: {file_path}")
    return file_path

if __name__ == "__main__":
    text = input("Enter the text message: ").strip()
    output_folder = "/home/iot/Desktop/PAE/intento1/matrixes"
    text_to_image(text, output_folder=output_folder)



