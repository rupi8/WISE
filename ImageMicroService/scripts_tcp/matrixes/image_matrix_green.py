# Image matrix for green in RGB565 format (native byte order)
# Green: RGB(0, 255, 0) → r5=0, g6=63, b5=0 → value = (0 << 11) | (63 << 5) | 0 = 2016
image_matrix = [[2016 for _ in range(320)] for _ in range(640)]
