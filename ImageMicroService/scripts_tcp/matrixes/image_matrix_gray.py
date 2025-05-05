# Image matrix for gray in RGB565 format (native byte order)
# Gray (assumed): RGB(128, 128, 128) → r5=16, g6=32, b5=16
# value = (16 << 11) | (32 << 5) | 16 = (16*2048) + (32*32) + 16 = 32768 + 1024 + 16 = 33808
image_matrix = [[33808 for _ in range(320)] for _ in range(640)]
