# Si tienes archivos de audio, puedes reproducirlos cuando sea necesario. 
# Esto es útil si quieres emitir sonidos o clips específicos como notificaciones o alertas.


import pygame

def reproducir_audio(archivo):
    pygame.mixer.init()
    pygame.mixer.music.load(archivo)
    pygame.mixer.music.play()

# Reproducir un archivo de sonido
reproducir_audio("alerta.mp3")
