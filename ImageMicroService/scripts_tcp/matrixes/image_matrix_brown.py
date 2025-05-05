# Image matrix for brown in RGB565 format (native byte order)
# Brown (assumed): RGB(165, 42, 42) → r5=floor(165/8)=20, g6=floor(42/4)=10, b5=floor(42/8)=5
# value = (20 << 11) | (10 << 5) | 5 = (20*2048) + (10*32) + 5 = 40960 + 320 + 5 = 41285
image_matrix = [[41285 for _ in range(320)] for _ in range(640)]
