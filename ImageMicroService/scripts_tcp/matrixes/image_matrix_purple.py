# Image matrix for purple in RGB565 format (native byte order)
# Purple (assumed): RGB(128, 0, 128) → r5=16, g6=0, b5=16 → value = (16 << 11) | (0 << 5) | 16 = 32768 + 16 = 32784
image_matrix = [[32784 for _ in range(320)] for _ in range(640)]
