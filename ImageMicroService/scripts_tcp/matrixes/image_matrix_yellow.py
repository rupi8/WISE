# Image matrix for yellow in RGB565 format (native byte order)
# Yellow: RGB(255, 255, 0) → r5=31, g6=63, b5=0 → value = (31 << 11) | (63 << 5) | 0 = 65504
image_matrix = [[65504 for _ in range(320)] for _ in range(640)]
