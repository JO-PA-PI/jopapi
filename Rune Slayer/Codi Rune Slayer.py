import time
import math
from pygame.locals import *
import pygame

# Tamany finestra
VIEW_WIDTH = 640
VIEW_HEIGHT = 360

# iniciem pygame
pygame.init()
pygame.mixer.init()  # Inicializamos el módulo de sonido
pantalla = pygame.display.set_mode((VIEW_WIDTH, VIEW_HEIGHT))
pygame.display.set_caption("Arcade")

# Estados del juego
LOADING_SCREEN = 0
MENU_SCREEN = 1
GAME_SCREEN = 2
BATTLE_SCREEN = 3
END_SCREEN = 4  # Nueva pantalla final
CREDITS_SCREEN = 5  # Nueva pantalla de créditos
current_state = LOADING_SCREEN

# Música para cada pantalla
menu_music = 'assets/menu.mp3'
game_music = 'assets/ambiente.mp3'  # Música ambiental para el juego
battle_music = 'assets/batalla.mp3'  # Música para la batalla
current_music = None  # Para seguimiento de la música actual

# Rutas de imágenes para cada pantalla
loading_image = 'assets/carga.jpg'  # Reemplaza con tu propia imagen
menu_image = 'assets/menu.jpg'  # Reemplaza con tu propia imagen
background_image = 'assets/Mapa2.jpg'
battle_image = 'assets/combate.jpg'  # Reemplaza con tu imagen de batalla
enemy_image = 'assets/goblin2.png'  # Reemplaza con tu imagen de enemigo
end_image = 'assets/final2.jpg'  # Reemplaza con tu imagen de fin
credits_image = 'assets/credits.jpg'  # Reemplaza con tu imagen de créditos

# Coordenadas del enemigo (puedes modificar estos valores)
ENEMY_X = 300  # Coordenada X del enemigo en el mapa
ENEMY_Y = 200  # Coordenada Y del enemigo en el mapa
ENEMY_DETECTION_RADIUS = 50  # Radio de detección para iniciar batalla

# Dimensiones del fondo de juego
background = pygame.image.load(background_image).convert()
background_width = background.get_width()
background_height = background.get_height()

# Variables para mostrar colisiones y coordenadas
show_collisions = False  # Nueva variable para mostrar/ocultar colisiones
show_coordinates = True  # Nueva variable para mostrar coordenadas

# Definir áreas de colisión básicas para que puedas modificarlas fácilmente
# El formato es [x, y, ancho, alto]
# Estas serán las áreas donde NO se puede caminar

# Colisiones simplificadas:
# - Solo los bordes del mapa
# - Una colisión en el centro
# - Una colisión en la parte superior derecha
obstacles = [
    # Bordes del mapa (límites para que el jugador no salga del mapa)
    [0, 0, background_width, 30],  # Borde superior
    [0, background_height - 100, background_width, 90],  # Borde inferior
    [0, 0, 30, background_height],  # Borde izquierdo
    [background_width - 90, 0, 30, background_height],  # Borde derecho

    # Obstáculo en el centro del mapa (para modificar)
    [430, 390, 310, 90],  # Colisión central

    # Obstáculo en la parte superior derecha (para modificar)
    [590, 90, 300, 200]  # Colisión superior derecha

]


# Función para verificar colisiones
def check_collision(player_rect, dx, dy):
    # Crear un rectángulo temporal con la posición futura del jugador
    # El rectángulo de colisión del jugador en coordenadas absolutas del mapa
    abs_player_rect = pygame.Rect(
        player_rect.x - bg_x + dx,
        player_rect.y - bg_y + dy,
        player_rect.width,
        player_rect.height
    )

    # Comprobar colisiones con obstáculos
    for obstacle in obstacles:
        obstacle_rect = pygame.Rect(obstacle)
        if abs_player_rect.colliderect(obstacle_rect):
            return True

    # No hay colisión
    return False


# Función para cambiar la música según la pantalla
def change_music(music_file):
    global current_music

    # Si es la misma música que está sonando, no hacemos nada
    if current_music == music_file:
        return

    # Si hay música sonando, la detenemos
    pygame.mixer.music.stop()

    # Cargamos y reproducimos la nueva música
    try:
        pygame.mixer.music.load(music_file)
        pygame.mixer.music.play(-1)  # -1 para reproducir en bucle
        current_music = music_file
    except pygame.error:
        print(f"No se pudo cargar la música: {music_file}")
        current_music = None


# Parámetros de batalla
player_hp = 100
enemy_hp = 80
player_attack = 15
enemy_attack = 10
battle_turn = "player"  # "player" o "enemy"
battle_message = ""
battle_action_cooldown = 0
BATTLE_COOLDOWN = 1000  # 1 segundo entre acciones

# Límits per moure el fons enlloc del personatge
MARGIN_X, MARGIN_Y = VIEW_WIDTH // 2, VIEW_HEIGHT // 2

# Carreguem imatge inicial personatge
player_image = pygame.image.load('assets/sprites/down0.png')
protagonist_speed = 8

# Posicions inicials del personatge i del fons
player_rect = player_image.get_rect(midbottom=(VIEW_WIDTH // 2, VIEW_HEIGHT // 2))
bg_x, bg_y = (-200, -400)

# Control de FPS
clock = pygame.time.Clock()
fps = 30

# Control de l'animació del personatge
# 1 up. 2 down. 3 right. 4 left
sprite_direction = "down"
sprite_index = 0
animation_protagonist_speed = 160
sprite_frame_number = 3
last_change_frame_time = 0
idle = False


def imprimir_pantalla(image):
    # Imprimo una imagen a pantalla completa
    try:
        background = pygame.image.load(image).convert()
        pantalla.blit(background, (0, 0))
    except pygame.error:
        # Si hay un error al cargar la imagen, mostramos un color de fondo y un texto
        pantalla.fill((0, 0, 0))
        font = pygame.font.SysFont(None, 36)
        text = font.render(f"Imagen no encontrada: {image}", True, (255, 255, 255))
        pantalla.blit(text, (50, VIEW_HEIGHT // 2))


def imprimir_pantalla_fons(image, x, y):
    # Imprimeixo imatge de fons:
    background = pygame.image.load(image).convert()
    pantalla.blit(background, (x, y))


def check_enemy_collision():
    # Calcula si el jugador está cerca del enemigo
    # Convertimos coordenadas del enemigo a coordenadas de pantalla
    enemy_screen_x = ENEMY_X + bg_x
    enemy_screen_y = ENEMY_Y + bg_y

    # Calculamos la distancia entre el jugador y el enemigo
    distance = math.sqrt((player_rect.centerx - enemy_screen_x) ** 2 +
                         (player_rect.centery - enemy_screen_y) ** 2)

    # Si está dentro del radio de detección, iniciamos batalla
    if distance < ENEMY_DETECTION_RADIUS:
        return True
    return False


def draw_enemy():
    # Dibuja el enemigo en el mapa
    try:
        enemy_img = pygame.image.load(enemy_image).convert_alpha()
        enemy_rect = enemy_img.get_rect(center=(ENEMY_X + bg_x, ENEMY_Y + bg_y))
        pantalla.blit(enemy_img, enemy_rect)
    except pygame.error:
        # Si no se encuentra la imagen, dibujamos un círculo rojo
        pygame.draw.circle(pantalla, (255, 0, 0), (ENEMY_X + bg_x, ENEMY_Y + bg_y), 15)


def draw_health_bar(x, y, hp, max_hp):
    # Dibuja una barra de salud
    ratio = hp / max_hp
    pygame.draw.rect(pantalla, (255, 0, 0), (x, y, 100, 20))
    pygame.draw.rect(pantalla, (0, 255, 0), (x, y, 100 * ratio, 20))

    # Muestra el valor numérico
    font = pygame.font.SysFont(None, 24)
    text = font.render(f"{hp}/{max_hp}", True, (255, 255, 255))
    pantalla.blit(text, (x + 35, y + 2))


def handle_battle_screen():
    global current_state, battle_turn, player_hp, enemy_hp, battle_message, battle_action_cooldown

    # Cambiar a música de batalla
    change_music(battle_music)

    # Mostrar imagen de fondo de batalla
    imprimir_pantalla(battle_image)

    # Dibujar personajes de batalla (simplificado para este ejemplo)
    player_battle_img = pygame.image.load('assets/sprites/right0.png')
    try:
        enemy_battle_img = pygame.image.load(enemy_image).convert_alpha()
    except pygame.error:
        # Si no hay imagen, creamos un rectángulo rojo
        enemy_battle_img = pygame.Surface((50, 50))
        enemy_battle_img.fill((255, 0, 0))

    # Posicionar personajes en pantalla
    pantalla.blit(player_battle_img, (100, 250))
    pantalla.blit(enemy_battle_img, (450, 250))

    # Dibujar barras de salud
    draw_health_bar(50, 50, player_hp, 100)
    draw_health_bar(450, 50, enemy_hp, 80)

    # Mostrar mensaje de batalla
    font = pygame.font.SysFont(None, 30)
    message_text = font.render(battle_message, True, (255, 255, 255))
    pantalla.blit(message_text, (VIEW_WIDTH // 2 - message_text.get_width() // 2, 300))

    current_time = pygame.time.get_ticks()

    # Mostrar opciones de batalla si es turno del jugador
    if battle_turn == "player":
        # Botones de acción
        attack_button = pygame.Rect(250, 150, 120, 40)
        pygame.draw.rect(pantalla, (150, 0, 0), attack_button)

        defend_button = pygame.Rect(250, 200, 120, 40)
        pygame.draw.rect(pantalla, (0, 0, 150), defend_button)

        # Textos de los botones
        attack_text = font.render("Atacar", True, (255, 255, 255))
        defend_text = font.render("Defender", True, (255, 255, 255))

        pantalla.blit(attack_text, (attack_button.x + 20, attack_button.y + 10))
        pantalla.blit(defend_text, (defend_button.x + 20, defend_button.y + 10))

        # Eventos de clic
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()

        if current_time - battle_action_cooldown > BATTLE_COOLDOWN:
            if mouse_click[0]:
                if attack_button.collidepoint(mouse_pos):
                    # Ataque del jugador
                    damage = player_attack
                    enemy_hp = max(0, enemy_hp - damage)
                    battle_message = f"¡Has atacado y has hecho {damage} de daño!"
                    battle_turn = "enemy"
                    battle_action_cooldown = current_time

                elif defend_button.collidepoint(mouse_pos):
                    # Defensa (menos daño en el próximo turno)
                    battle_message = "Te has defendido. Recibirás menos daño"
                    battle_turn = "enemy"
                    battle_action_cooldown = current_time

    # Turno del enemigo
    elif battle_turn == "enemy":
        # Mostrar mensaje de espera
        wait_text = font.render("Turno del enemigo...", True, (255, 255, 255))
        pantalla.blit(wait_text, (VIEW_WIDTH // 2 - wait_text.get_width() // 2, 250))

        # Esperar un tiempo y luego atacar
        if current_time - battle_action_cooldown > BATTLE_COOLDOWN * 0:
            # Ataque automático del enemigo
            damage = enemy_attack
            player_hp = max(0, player_hp - damage)
            battle_message = f"¡El enemigo ataca y hace {damage} de daño!"
            battle_turn = "player"
            battle_action_cooldown = current_time

    # Verifica condiciones de victoria/derrota
    if player_hp <= 0:
        battle_message = "¡Has sido derrotado!"
        font_big = pygame.font.SysFont(None, 48)
        text = font_big.render("¡DERROTA!", True, (255, 0, 0))
        pantalla.blit(text, (VIEW_WIDTH // 2 - text.get_width() // 2, 100))

        # Mostrar opción para volver al menú
        continue_text = font.render("Presiona ESC para volver al menú", True, (255, 255, 255))
        pantalla.blit(continue_text, (VIEW_WIDTH // 2 - continue_text.get_width() // 2, 330))

        # Verificar si se presiona ESC
        keys = pygame.key.get_pressed()
        if keys[K_ESCAPE]:
            # Reiniciar variables de batalla y volver al menú
            player_hp = 100
            enemy_hp = 80
            battle_turn = "player"
            battle_message = ""
            current_state = MENU_SCREEN
            # Cambiar a música del menú al volver
            change_music(menu_music)
            pygame.time.delay(200)

    elif enemy_hp <= 0:
        # Mostrar mensaje de victoria brevemente
        battle_message = "¡Has derrotado al enemigo!"
        font_big = pygame.font.SysFont(None, 48)
        text = font_big.render("¡VICTORIA!", True, (0, 255, 0))
        pantalla.blit(text, (VIEW_WIDTH // 2 - text.get_width() // 2, 100))

        # CAMBIO: Pequeña pausa y cambio directo a la pantalla final
        pygame.display.update()  # Actualizamos la pantalla para mostrar el mensaje de victoria
        pygame.time.delay(1000)  # Pausa de 1 segundo para que se vea el mensaje

        # Ir a la pantalla final directamente
        current_state = END_SCREEN


def handle_end_screen():
    # Detener música en la pantalla final
    pygame.mixer.music.stop()

    # Mostrar pantalla final
    imprimir_pantalla(end_image)

    # Mostrar texto de fin
    font_big = pygame.font.SysFont(None, 60)
    text = font_big.render("Fin de la aventura", True, (0, 255, 0))
    pantalla.blit(text, (VIEW_WIDTH // 2 - text.get_width() // 2, VIEW_HEIGHT // 2 - 30))

    # Texto para salir
    font = pygame.font.SysFont(None, 30)
    exit_text = font.render("", True, (255, 255, 255))
    pantalla.blit(exit_text, (VIEW_WIDTH // 2 - exit_text.get_width() // 2, VIEW_HEIGHT // 2 + 30))

    # Verificar si se presiona ESPACIO para salir
    keys = pygame.key.get_pressed()
    if keys[K_SPACE]:
        pygame.quit()
        exit()


def handle_credits_screen():
    global current_state

    # Mostrar pantalla de créditos
    imprimir_pantalla(credits_image)

    # Mostrar textos de créditos
    font_title = pygame.font.SysFont(None, 48)
    font_text = pygame.font.SysFont(None, 30)

    # Título de créditos
    title_text = font_title.render("CRÉDITOS", True, (255, 255, 255))
    pantalla.blit(title_text, (VIEW_WIDTH // 2 - title_text.get_width() // 2, 50))

    # Créditos - Ajusta estos según tu proyecto
    credits = [
        "Programación: Joel Paredes Picó i Xavi Sancho",
        "Diseño Gráfico: Joel Paredes Picó",
        "Música: Free Sound",
        "",
        "",
        ""
    ]

    # Mostrar los textos de créditos
    y_pos = 120
    for line in credits:
        credit_text = font_text.render(line, True, (255, 255, 255))
        pantalla.blit(credit_text, (VIEW_WIDTH // 2 - credit_text.get_width() // 2, y_pos))
        y_pos += 40

    # Texto para volver al menú
    back_text = font_text.render("Presiona ESC para volver al menú", True, (255, 255, 0))
    pantalla.blit(back_text, (VIEW_WIDTH // 2 - back_text.get_width() // 2, VIEW_HEIGHT - 50))

    # Verificar si se presiona ESC para volver al menú
    keys = pygame.key.get_pressed()
    if keys[K_ESCAPE]:
        current_state = MENU_SCREEN
        # Cambiar a música del menú al volver
        change_music(menu_music)
        pygame.time.delay(200)


def handle_loading_screen():
    global current_state

    # Mostrar pantalla de carga
    imprimir_pantalla(loading_image)

    # Mostrar texto de instrucción
    font = pygame.font.SysFont(None, 36)
    text = font.render("Presiona ESPACIO para continuar", True, (255, 255, 255))
    pantalla.blit(text, (VIEW_WIDTH // 2 - text.get_width() // 2, VIEW_HEIGHT - 50))

    # Comprobar entrada para avanzar al menú
    keys = pygame.key.get_pressed()
    if keys[K_SPACE]:
        current_state = MENU_SCREEN
        # Iniciar música del menú
        change_music(menu_music)
        # Pequeña pausa para evitar que se salte inmediatamente la siguiente pantalla
        pygame.time.delay(200)


def handle_menu_screen():
    global current_state

    # Cambiar a música del menú
    change_music(menu_music)

    # Mostrar pantalla de menú
    imprimir_pantalla(menu_image)

    # Mostrar opciones del menú
    font = pygame.font.SysFont(None, 36)
    text1 = font.render("", True, (255, 255, 255))
    text2 = font.render("", True, (255, 255, 255))
    text3 = font.render("", True, (255, 255, 255))

    pantalla.blit(text1, (VIEW_WIDTH // 2 - text1.get_width() // 2, VIEW_HEIGHT // 2 - 20))
    pantalla.blit(text2, (VIEW_WIDTH // 2 - text2.get_width() // 2, VIEW_HEIGHT // 2 + 20))
    pantalla.blit(text3, (VIEW_WIDTH // 2 - text3.get_width() // 2, VIEW_HEIGHT // 2 + 60))

    # Comprobar entrada para las opciones del menú
    keys = pygame.key.get_pressed()
    if keys[K_1]:
        current_state = GAME_SCREEN
        # Cambiar a música ambiental del juego
        change_music(game_music)
        pygame.time.delay(200)
    elif keys[K_2]:
        pygame.quit()
        exit()
    elif keys[K_3]:
        current_state = CREDITS_SCREEN
        pygame.time.delay(200)


def handle_game_screen():
    global bg_x, bg_y, sprite_direction, sprite_index, last_change_frame_time, idle, current_state
    global show_collisions, show_coordinates  # Añadimos las variables globales

    # Asegurar que suena la música ambiental del juego
    change_music(game_music)

    current_time = pygame.time.get_ticks()

    # Moviment del jugador
    idle = True
    keys = pygame.key.get_pressed()

    # Variables para almacenar el movimiento previsto
    dx, dy = 0, 0

    if keys[K_UP]:
        idle = False
        sprite_direction = "up"
        dy = -protagonist_speed

    if keys[K_DOWN]:
        idle = False
        sprite_direction = "down"
        dy = protagonist_speed

    if keys[K_RIGHT]:
        idle = False
        sprite_direction = "right"
        dx = protagonist_speed

    if keys[K_LEFT]:
        idle = False
        sprite_direction = "left"
        dx = -protagonist_speed

    # Verificar si hay colisión con los bordes o obstáculos
    if dx != 0 or dy != 0:  # Solo verificar si hay movimiento
        if not check_collision(player_rect, dx, dy):
            # No hay colisión, podemos movernos
            # Determinar si el personaje se mueve o el fondo
            if dx > 0:  # Movimiento a la derecha
                if player_rect.x < VIEW_WIDTH - MARGIN_X or bg_x <= VIEW_WIDTH - background_width:
                    player_rect.x = min(player_rect.x + dx, VIEW_WIDTH - player_rect.width // 2)
                else:
                    if bg_x - dx >= VIEW_WIDTH - background_width:
                        bg_x -= dx
                    else:
                        bg_x = VIEW_WIDTH - background_width

            elif dx < 0:  # Movimiento a la izquierda
                if player_rect.x > MARGIN_X or bg_x >= 0:
                    player_rect.x = max(player_rect.x + dx, player_rect.width // 2)
                else:
                    if bg_x - dx <= 0:
                        bg_x -= dx
                    else:
                        bg_x = 0

            if dy > 0:  # Movimiento hacia abajo
                if player_rect.y < VIEW_HEIGHT - MARGIN_Y or bg_y <= VIEW_HEIGHT - background_height:
                    player_rect.y = min(player_rect.y + dy, VIEW_HEIGHT - player_rect.height // 2)
                else:
                    if bg_y - dy >= VIEW_HEIGHT - background_height:
                        bg_y -= dy
                    else:
                        bg_y = VIEW_HEIGHT - background_height

            elif dy < 0:  # Movimiento hacia arriba
                if player_rect.y > MARGIN_Y or bg_y >= 0:
                    player_rect.y = max(player_rect.y + dy, player_rect.height // 2)
                else:
                    if bg_y - dy <= 0:
                        bg_y -= dy
                    else:
                        bg_y = 0

    # Dibuixar el fons
    imprimir_pantalla_fons(background_image, bg_x, bg_y)

    # Comprobar tecla para mostrar/ocultar colisiones (tecla 'C')
    if keys[K_c]:
        # Pequeña demora para evitar múltiples toggles con una sola pulsación
        pygame.time.delay(100)
        show_collisions = not show_collisions

    # Comprobar tecla para mostrar/ocultar coordenadas (tecla 'V')
    if keys[K_v]:
        # Pequeña demora para evitar múltiples toggles con una sola pulsación
        pygame.time.delay(100)
        show_coordinates = not show_coordinates

    # Dibujar los bordes de colisión si show_collisions está activado
    if show_collisions:
        # Dibujar los obstáculos
        for obstacle in obstacles:
            # Convertir coordenadas del mapa a coordenadas de pantalla
            screen_rect = pygame.Rect(
                obstacle[0] + bg_x,
                obstacle[1] + bg_y,
                obstacle[2],
                obstacle[3]
            )
            # Dibujar solo si es visible en la pantalla
            if screen_rect.colliderect(pygame.Rect(0, 0, VIEW_WIDTH, VIEW_HEIGHT)):
                pygame.draw.rect(pantalla, (0, 0, 255), screen_rect, 2)  # Azul para los obstáculos

    # Dibujar el enemigo en el mapa
    draw_enemy()

    # Verificar colisión con el enemigo
    if check_enemy_collision():
        current_state = BATTLE_SCREEN
        # Pequeña pausa para evitar activación repetida
        pygame.time.delay(200)

    # frame number: (there are 3 frames only)
    # selccionem la imatge a mostrar
    if not idle:
        if current_time - last_change_frame_time >= animation_protagonist_speed:
            last_change_frame_time = current_time
            sprite_index = sprite_index + 1
            sprite_index = sprite_index % sprite_frame_number
    else:
        sprite_index = 0
    # dibuixar el jugador
    player_image = pygame.image.load('assets/sprites/' + sprite_direction + str(sprite_index) + '.png')
    pantalla.blit(player_image, player_rect)
    # mantenir el jugador dins la finestra
    player_rect.clamp_ip(pantalla.get_rect())

    # Mostrar coordenadas del personaje si show_coordinates está activado
    if show_coordinates:
        # Calcular coordenadas absolutas en el mapa
        absolute_x = player_rect.centerx - bg_x
        absolute_y = player_rect.centery - bg_y

        

    # Añadir opción para volver al menú
    font = pygame.font.SysFont(None, 20)
    text = font.render("ESC - Volver al menú", True, (255, 255, 255))
    pantalla.blit(text, (10, 10))

    # Mostrar información sobre las teclas para colisiones y coordenadas


    coord_text = font.render("", True, (255, 255, 255))
    pantalla.blit(coord_text, (VIEW_WIDTH - 200, 30))

    # Comprobar si se presiona ESC para volver al menú
    if keys[K_ESCAPE]:
        current_state = MENU_SCREEN
        # Cambiar a música del menú
        change_music(menu_music)
        pygame.time.delay(200)


# Bucle principal del juego
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    # Gestión de la pantalla actual según el estado
    if current_state == LOADING_SCREEN:
        handle_loading_screen()
    elif current_state == MENU_SCREEN:
        handle_menu_screen()
    elif current_state == GAME_SCREEN:
        handle_game_screen()
    elif current_state == BATTLE_SCREEN:
        handle_battle_screen()
    elif current_state == END_SCREEN:
        handle_end_screen()
    elif current_state == CREDITS_SCREEN:
        handle_credits_screen()

    pygame.display.update()
    clock.tick(fps)
