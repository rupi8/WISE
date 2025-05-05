import os
from PIL import Image
import numpy as np

def rgb888_to_rgb565(image_array):
    """
    Convert an image (a NumPy array of shape (height, width, 3)) from RGB888 
    to RGB565 (without swapping bytes).

    The conversion reduces:
      - Red from 8 bits to 5 bits (>> 3)
      - Green from 8 bits to 6 bits (>> 2)
      - Blue from 8 bits to 5 bits (>> 3)
      
    Then it packs the values into a single 16-bit integer (RGB565).
    
    Note: The resulting 16-bit value is stored in native order, i.e. the high byte
    comes first and the low byte second. This is what the ESP32 client code expects.
    """
    # Convert each channel to 16-bit integers to ensure proper shifting
    r = image_array[:, :, 0].astype(np.uint16) >> 3  # 5 bits for red
    g = image_array[:, :, 1].astype(np.uint16) >> 2  # 6 bits for green
    b = image_array[:, :, 2].astype(np.uint16) >> 3  # 5 bits for blue
    
    # Pack the bits into a single 16-bit number (RGB565 format)
    rgb565 = (r << 11) | (g << 5) | b
    return rgb565

def process_image(input_path, output_folder, output_filename="image_matrix_namex.py"):
    """
    Processes the image: opens it, converts to RGB, resizes to 320x640,
    converts the pixel data to RGB565 format (without byte swap),
    and saves the resulting matrix as a Python file containing a variable
    named 'image_matrix'.
    """
    # Open and convert the image to RGB
    with Image.open(input_path) as img:
        img = img.convert("RGB")
        # Resize the image to 320x640 (width x height)
        img = img.resize((320, 640), Image.LANCZOS)
        # Convert the image to a NumPy array
        img_array = np.array(img, dtype=np.uint8)
    
    # Convert the image from RGB888 to RGB565
    matrix = rgb888_to_rgb565(img_array)
    
    # Convert the matrix to a list of lists for storage
    matrix_list = matrix.tolist()
    
    # Create the content to write to the output file
    content = "# Image matrix in RGB565 format (native byte order)\n"
    content += "image_matrix = " + repr(matrix_list) + "\n"
    
    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    file_path = os.path.join(output_folder, output_filename)
    with open(file_path, "w") as f:
        f.write(content)
    
    print(f"File saved at: {file_path}")

if __name__ == "__main__":
    # Update these paths to your environment
    input_path = "/home/iot/Desktop/intento1/img1.jpg"  # Path to your input image
    output_folder = "/home/iot/Desktop/PAE/intento1/matrixes"         # Output folder for the Python file
    process_image(input_path, output_folder)