# Image matrix for orange in RGB565 format (native byte order)
# Orange (assumed): RGB(255, 165, 0) → r5=31, g6=floor(165/4)=41, b5=0 
# value = (31 << 11) | (41 << 5) = 63488 + (41*32=1312) = 64800
image_matrix = [[64800 for _ in range(320)] for _ in range(640)]
