# Image matrix for red in RGB565 format (native byte order)
# Red: RGB(255, 0, 0) → r5=31, g6=0, b5=0 → value = (31 << 11) | (0 << 5) | 0 = 63488
image_matrix = [[63488 for _ in range(320)] for _ in range(640)]
