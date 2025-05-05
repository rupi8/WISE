# Image matrix for green in RGB565 format (native byte order)
# Blue: RGB(0, 0, 255) → r5=0, g6=0, b5=31 → value = (0 << 11) | (0 << 5) | 31 = 31
image_matrix = [[31 for _ in range(320)] for _ in range(640)]