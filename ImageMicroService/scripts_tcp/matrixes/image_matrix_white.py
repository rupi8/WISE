# Image matrix for white in RGB565 format (native byte order)
# White: RGB(255, 255, 255) → r5=31, g6=63, b5=31 → value = 65535
image_matrix = [[65535 for _ in range(320)] for _ in range(640)]
