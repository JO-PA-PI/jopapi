import pygame
import sys


# Inicializar pygame
pygame.init()

# Definir colores
GRIS = (169, 169, 169)
ROJO = (255, 0, 0)
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
CARNE = (252, 208, 180)
BLUE = (0,0,255)
YELLOW = 	(255, 255, 0)
# Crear la pantalla
pantalla = pygame.display.set_mode((1000, 1000))
pygame.display.set_caption("CARA GRACIOSA")

# Bucle principal
while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    pantalla.fill(BLANCO)

    # Dibuja la cabeza del personaje
    pygame.draw.ellipse(pantalla, ROJO, (300, 500, 450, 300))
    pygame.draw.ellipse(pantalla, CARNE, (320, 300, 400, 300))
    pygame.draw.circle(pantalla,BLANCO, (470,450),50)
    pygame.draw.circle(pantalla, NEGRO, (470, 450), 50,1)
    pygame.draw.circle(pantalla, NEGRO, (470, 450), 10,)
    pygame.draw.circle(pantalla, BLANCO, (570, 450), 50)
    pygame.draw.circle(pantalla, NEGRO, (570, 450), 50,1)
    pygame.draw.circle(pantalla, NEGRO, (570, 450), 10, )
    pygame.draw.arc(pantalla, BLUE, (340, 300, 370, 200), 6.28, 3.14, 100)
    pygame.draw.circle(pantalla, YELLOW, (525, 295  ), 10)
    pygame.draw.arc(pantalla, NEGRO, (500, 520, 90, 100), 6.28, 3.14, 100)
    pygame.draw.line(pantalla, NEGRO, (500, 400), (410, 350), 11)
    pygame.draw.line(pantalla, NEGRO, (590, 350), (550, 400), 11)

    pygame.display.update()
