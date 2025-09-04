import pygame, sys, math, random

# =======================
# Configuración general
# =======================
WIDTH, HEIGHT = 1024, 640
FOV = math.radians(72)
MAX_DISTANCE = 32.0
MOVE_SPEED = 4.2
ROT_SPEED = math.radians(140)
SPRINT_MULT = 1.6
PLAYER_RADIUS = 0.18
NUM_RAYS = WIDTH

# Colores
COL_CEILING = (115,115,120)
COL_WALL    = (210,210,210)
COL_WALL_SIDE = (170,170,170)
COL_MINIMAP_BG = (20,20,24)
COL_MINIMAP_WALL = (180,180,180)
COL_MINIMAP_PLAYER = (255,235,59)
COL_HUD = (255,255,255)
COL_BULLET = (255,230,80)
COL_DMG = (255,80,80)
COL_INFO = (100,210,255)
COL_BLACK = (0, 0, 0)
MIN_SPRITE_DIST = 0.45        # distancia mínima para cálculo de tamaño
MAX_SPRITE_H    = HEIGHT * 2  # tope duro de alto del sprite en píxeles



# ====== RUTAS A IMÁGENES ======
# 👉 Cambia estas rutas por tus archivos reales
FLOOR_PATH = "assets/fondo.jpeg"   # textura del suelo (tablones)
GUN_PATH   = "assets/pistola.png"     # sprite de la pistola (PNG con alpha)
ENEMY_PATH = "assets/alubia_mewing.png"   # sprite 2D del enemigo (PNG con alpha)
WALL_PATH =  "assets/fondo.jpeg" # textura de pared de tablones


# =======================
# Mapa (1 = pared, 0 = libre)
# =======================
MAP = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,1],
    [1,0,1,0,1,0,1,0,0,0,1,0,0,0,0,1,0,0,0,1],
    [1,0,0,0,0,0,1,0,1,0,0,0,1,0,0,1,0,0,0,1],
    [1,0,1,0,1,0,0,0,0,0,0,1,0,0,1,0,0,0,0,1],
    [1,0,1,0,1,0,1,0,1,0,0,1,0,1,0,1,0,1,0,1],
    [1,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,1,0,1],
    [1,0,1,0,1,0,0,0,1,0,0,1,0,0,0,1,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,1,0,1,0,1,0,1,0,1],
    [1,1,1,1,1,0,1,1,1,1,0,1,0,1,0,1,0,1,0,1],
    [1,0,0,0,1,0,0,0,0,1,0,1,0,0,0,1,0,0,0,1],
    [1,0,1,0,1,0,1,1,0,1,0,1,1,1,0,1,0,1,0,1],
    [1,0,0,0,0,0,0,0,0,1,0,0,0,1,0,1,0,0,0,1],
    [1,0,1,0,1,0,0,0,1,0,0,1,0,0,0,1,0,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]
MAP_H, MAP_W = len(MAP), len(MAP[0])

# =======================
# Inicialización
# =======================
pygame.init()
# =======================
# Inicialización de joysticks
# =======================
joysticks = []
for i in range(pygame.joystick.get_count()):
    j = pygame.joystick.Joystick(i)
    j.init()
    joysticks.append(j)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Escapa de la Alubia")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Consolas", 20)

# Jugador
player_x, player_y = 3.5, 3.5
player_angle = 0.0
player_health = 100
damage_flash = 0.0
player_speed = 5  # velocidad del jugador, ajusta a tu gusto


# =======================
# 🎮 Controles táctiles
# =======================
joystick_center = (120, HEIGHT - 120)
joystick_radius = 70
joystick_input = [0.0, 0.0]  # mutable para poder actualizar

fire_button_rect = pygame.Rect(WIDTH - 180, HEIGHT - 160, 120, 120)
reload_button_rect = pygame.Rect(WIDTH - 180, HEIGHT - 300, 120, 100)

def draw_touch_controls():
    # Joystick base
    pygame.draw.circle(screen, (100,100,100), joystick_center, joystick_radius, 5)
    # Joystick indicador
    pygame.draw.circle(screen, (0,255,0),
        (joystick_center[0] + int(joystick_input[0]*joystick_radius),
         joystick_center[1] + int(joystick_input[1]*joystick_radius)), 20)
    # Botón FIRE
    pygame.draw.rect(screen, (255,0,0), fire_button_rect, border_radius=25)
    text = font.render("FIRE", True, (255,255,255))
    screen.blit(text, (fire_button_rect.centerx - text.get_width()//2,
                       fire_button_rect.centery - text.get_height()//2))
    # Botón RELOAD
    pygame.draw.rect(screen, (0,0,255), reload_button_rect, border_radius=25)
    text2 = font.render("RELOAD", True, (255,255,255))
    screen.blit(text2, (reload_button_rect.centerx - text2.get_width()//2,
                        reload_button_rect.centery - text2.get_height()//2))

def handle_touch_event(event):
    global joystick_input
    if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION):
        x, y = event.pos
        dx = x - joystick_center[0]
        dy = y - joystick_center[1]
        dist = math.hypot(dx, dy)
        if dist < joystick_radius:
            # Normalizamos el vector y lo invertimos verticalmente para y pantalla
            joystick_input[0] = dx / joystick_radius
            joystick_input[1] = dy / joystick_radius * -1
        else:
            joystick_input[0] = joystick_input[1] = 0.0

        if fire_button_rect.collidepoint(x, y):
            fire()
        if reload_button_rect.collidepoint(x, y):
            start_reload()

    elif event.type == pygame.MOUSEBUTTONUP:
        joystick_input[0] = 0.0
        joystick_input[1] = 0.0




    # =====================
    # EVENTOS
    # =====================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # 👇 controles táctiles / ratón
        (event)

    # =====================
    # LÓGICA DEL JUEGO
    # =====================
    # Si tienes pantalla de intro
    if en_intro:  
        # Aquí tu lógica de intro (ej: esperar ENTER para empezar)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN]:
            en_intro = False

    else:
        # Movimiento con joystick
        player_x += joystick_input[0] * player_speed
        player_y += joystick_input[1] * player_speed

        # Lógica del juego normal (enemigos, colisiones, disparos…)
        # mover_enemigos()
        # checar_colisiones()

    # =====================
    # DIBUJO DEL JUEGO
    # =====================
    screen.fill((0, 0, 0))  # fondo negro

    if en_intro:
        ()
    else:
        (player_x, player_y)
        ()
        # dibujar_balas()

    # 👇 al final siempre los botones/joystick
    draw_touch_controls()

    # =====================
    # ACTUALIZAR PANTALLA
    # =====================
    pygame.display.flip()
    clock.tick(60)



# Texturas / Sprites

def load_floor_tex():
    try:
        return pygame.image.load(FLOOR_PATH).convert()
    except:
        surf = pygame.Surface((64, 64))
        surf.fill((110, 90, 70))
        for yy in (16,32,48):
            pygame.draw.line(surf, (120,100,80), (0,yy), (64,yy), 2)
        return surf


def load_gun_img():
    try:
        img = pygame.image.load(GUN_PATH).convert_alpha()
    except:
        img = pygame.Surface((220,140), pygame.SRCALPHA)
        pygame.draw.rect(img, (40,40,40), (40,60,160,50))
        pygame.draw.rect(img, (30,30,30), (140,35,60,30))
        pygame.draw.rect(img, (80,80,80), (55,70,40,40))
    return img


def load_enemy_img():
    try:
        img = pygame.image.load(ENEMY_PATH).convert_alpha()
    except:
        img = pygame.Surface((80,120), pygame.SRCALPHA)
        pygame.draw.rect(img, (200,40,40), (10,10,60,100), border_radius=16)
        pygame.draw.circle(img, (240,80,80), (40,20), 16)  # cabeza
    return img


floor_tex = load_floor_tex()
try:
    wall_tex = pygame.image.load(WALL_PATH).convert()
except:
    wall_tex = pygame.Surface((64, 64))
    wall_tex.fill((150, 100, 50))

gun_img   = load_gun_img()
enemy_img = load_enemy_img()

# Pistola

gun_rect = gun_img.get_rect()
gun_scale = 260 / gun_rect.height if gun_rect.height > 260 else 1.0
gun_img = pygame.transform.smoothscale(
    gun_img,
    (int(gun_rect.width*gun_scale), int(gun_rect.height*gun_scale))
)

gun_rect = gun_img.get_rect()
gun_x = WIDTH - gun_rect.width - 20
gun_y = HEIGHT - gun_rect.height - 16
gun_recoil = 0
RECOIL_MAX = 18
RECOIL_RECOVER = 240.0

# Munición / balas
ammo = 36
max_ammo = 36
reloading = False
reload_timer = 0.0
RELOAD_TIME = 1.2
bullets = []  # dict {x,y,angle,alive,life}
BULLET_SPEED = 18.0
BULLET_LIFE = 1.2
FIRE_COOLDOWN = 0.12
time_since_shot = 0.0

def disparar():
    print("🔫 ¡Pew pew! (disparo táctil)")

def recargar():
    print("🔄 Recargando...")


# Enemigos
class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = 35
        self.speed = 1.55
        self.alive = True
        self.attack_cooldown = 0.0  # seg
        self.radius = 0.35
        self.state = "patrol"  # patrol / chase
        self.dir_timer = random.uniform(1.0, 3.0)
        self.dir_angle = random.uniform(0, math.tau)


enemies = [
    Enemy(1.5, 2.5),
    Enemy(4.5, 1.5),
    Enemy(10.5, 3.5),
    Enemy(14.5, 5.5),
]

# =======================
# Auxiliares / Colisiones
# =======================

def wall_at(x, y):
    if x < 0 or y < 0 or x >= MAP_W or y >= MAP_H:
        return 1
    return MAP[int(y)][int(x)]


def can_move_to(x, y):
    return wall_at(x, y) == 0


def move_with_collision(x, y, dx, dy, speed, dt):
    step_x, step_y = dx * speed * dt, dy * speed * dt
    new_x, new_y = x + step_x, y + step_y
    if can_move_to(new_x, y):
        x = new_x
    if can_move_to(x, new_y):
        y = new_y
    return x, y


def line_of_sight(ax, ay, bx, by, step=0.05):
    """DDA simple: True si no hay paredes entre A y B"""
    dx, dy = bx - ax, by - ay
    dist = math.hypot(dx, dy)
    if dist < 1e-6:
        return True
    steps = int(dist/step)
    if steps <= 1:
        return True
    dxn, dyn = dx/steps, dy/steps
    x, y = ax, ay
    for _ in range(steps):
        x += dxn
        y += dyn
        if wall_at(x, y) == 1:
            return False
    return True

# =======================
# Suelo y Techo
# =======================

def draw_floor_and_ceiling():
    # Techo simple
    screen.fill(COL_CEILING, pygame.Rect(0, 0, WIDTH, HEIGHT//2))

    # Suelo fake: bandas escaladas
    half_h = HEIGHT // 2
    for i in range(half_h):
        # factor de escala (más pequeño arriba, más grande abajo)
        scale = 1 + (i / half_h) * 10
        row = pygame.transform.scale(floor_tex, (WIDTH, int(1*scale)))
        y = half_h + i
        screen.blit(row, (0, y))


# =======================
# Raycasting
# =======================

def cast_and_draw():
    screen.fill(COL_BLACK)
    draw_floor_and_ceiling()
    z_buffer = [float('inf')] * WIDTH

    for col in range(WIDTH):
        # Calcular ángulo del rayo
        ray_angle = (player_angle - FOV/2.0) + (col / WIDTH) * FOV
        ray_dir_x = math.cos(ray_angle)
        ray_dir_y = math.sin(ray_angle)

        # Posición inicial
        map_x = int(player_x)
        map_y = int(player_y)

        # Longitudes del rayo
        delta_dist_x = abs(1 / ray_dir_x) if ray_dir_x != 0 else float('inf')
        delta_dist_y = abs(1 / ray_dir_y) if ray_dir_y != 0 else float('inf')

        # Paso inicial
        if ray_dir_x < 0:
            step_x = -1
            side_dist_x = (player_x - map_x) * delta_dist_x
        else:
            step_x = 1
            side_dist_x = (map_x + 1.0 - player_x) * delta_dist_x
        if ray_dir_y < 0:
            step_y = -1
            side_dist_y = (player_y - map_y) * delta_dist_y
        else:
            step_y = 1
            side_dist_y = (map_y + 1.0 - player_y) * delta_dist_y

        hit = False
        side = 0

        # DDA (buscar colisión con pared)
        while not hit:
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1
            if MAP[map_y][map_x] > 0:
                hit = True

        # Distancia perpendicular
        if side == 0:
            distance = (map_x - player_x + (1 - step_x) / 2) / ray_dir_x
        else:
            distance = (map_y - player_y + (1 - step_y) / 2) / ray_dir_y

        # Altura de la pared
        line_height = int(HEIGHT / (distance + 0.0001))
        start_y = max(0, -line_height // 2 + HEIGHT // 2)
        end_y = min(HEIGHT - 1, line_height // 2 + HEIGHT // 2)

        # --- DIBUJAR PARED TEXTURIZADA ---
        if side == 0:
            wall_x = player_y + distance * ray_dir_y
        else:
            wall_x = player_x + distance * ray_dir_x
        wall_x -= math.floor(wall_x)

        tex_x = int(wall_x * wall_tex.get_width())
        if (side == 0 and ray_dir_x > 0) or (side == 1 and ray_dir_y < 0):
            tex_x = wall_tex.get_width() - tex_x - 1

        wall_column = pygame.transform.scale(
            wall_tex.subsurface(tex_x, 0, 1, wall_tex.get_height()),
            (1, end_y - start_y)
        )
        screen.blit(wall_column, (col, start_y))

        # Guardar en z-buffer
        z_buffer[col] = distance

    return z_buffer


# =======================
# Balas
# =======================

def fire():
    global ammo, bullets, gun_recoil, time_since_shot, reloading
    if reloading:
        return
    if ammo > 0 and time_since_shot <= 0.0:
        ammo -= 1
        bullets.append({"x": player_x, "y": player_y, "angle": player_angle, "alive": True, "life": BULLET_LIFE})
        gun_recoil = RECOIL_MAX
        time_since_shot = FIRE_COOLDOWN


def start_reload():
    global reloading, reload_timer
    if not reloading and ammo < max_ammo:
        reloading = True
        reload_timer = RELOAD_TIME


def update_bullets(dt):
    global bullets
    for b in bullets:
        if not b["alive"]:
            continue
        b["x"] += math.cos(b["angle"]) * BULLET_SPEED * dt
        b["y"] += math.sin(b["angle"]) * BULLET_SPEED * dt
        b["life"] -= dt
        if wall_at(b["x"], b["y"]) == 1 or b["life"] <= 0:
            b["alive"] = False


def draw_bullets(z_buffer):
    plane_len = math.tan(FOV / 2)
    for b in bullets:
        if not b["alive"]:
            continue
        # Como billboard pequeñito (trazador)
        dx = b["x"] - player_x
        dy = b["y"] - player_y
        dist = math.hypot(dx, dy)
        if dist < 0.01 or dist > MAX_DISTANCE:
            continue
        ang = math.atan2(dy, dx) - player_angle
        ang = (ang + math.pi) % (2*math.pi) - math.pi
        if abs(ang) > FOV/2:
            continue

        screen_x = WIDTH/2 + (math.tan(ang) / plane_len) * (WIDTH/2)
        size = max(2, int(HEIGHT / (dist+1e-6) * 0.2))
        ccol = int(screen_x)
        if 0 <= ccol < WIDTH and dist < z_buffer[ccol]:
            rect = pygame.Rect(int(screen_x - size/2), int(HEIGHT/2 + size*0.3), size, size)
            pygame.draw.rect(screen, COL_BULLET, rect)

# =======================
# Enemigos: lógica y render
# =======================

def update_enemies(dt):
    global player_health, damage_flash
    for e in enemies:
        if not e.alive:
            continue

        dx = player_x - e.x
        dy = player_y - e.y
        dist = math.hypot(dx, dy)
        see = dist < 10.0 and line_of_sight(e.x, e.y, player_x, player_y)

        if see:
            e.state = "chase"
        elif e.state == "chase" and dist > 12.0:
            e.state = "patrol"

        if e.state == "chase":
            if dist > 0.001:
                dx /= dist
                dy /= dist
            nx, ny = e.x + dx*e.speed*dt, e.y + dy*e.speed*dt
            moved = False
            if can_move_to(nx, e.y):
                e.x = nx
                moved = True
            if can_move_to(e.x, ny):
                e.y = ny
                moved = True
            if not moved:
                # Bordeo simple: perpendicular
                px, py = -dy, dx
                nx2, ny2 = e.x + px*e.speed*dt, e.y + py*e.speed*dt
                if can_move_to(nx2, e.y):
                    e.x = nx2
                if can_move_to(e.x, ny2):
                    e.y = ny2
        else:
            # Patrol aleatorio
            e.dir_timer -= dt
            if e.dir_timer <= 0:
                e.dir_timer = random.uniform(1.0, 3.0)
                e.dir_angle = random.uniform(0, math.tau)
            pdx, pdy = math.cos(e.dir_angle), math.sin(e.dir_angle)
            nx, ny = e.x + pdx*e.speed*0.6*dt, e.y + pdy*e.speed*0.6*dt
            if can_move_to(nx, e.y):
                e.x = nx
            if can_move_to(e.x, ny):
                e.y = ny

        # Ataque cuerpo a cuerpo
        e.attack_cooldown = max(0.0, e.attack_cooldown - dt)
        if dist < (e.radius + 0.55) and e.attack_cooldown <= 0.0 and line_of_sight(e.x, e.y, player_x, player_y):
            player_health = max(0, player_health - 7)
            damage_flash = 0.22
            e.attack_cooldown = 0.9

    # Colisiones balas <-> enemigos
    for e in enemies:
        if not e.alive:
            continue
        for b in bullets:
            if not b["alive"]:
                continue
            dd = (e.x - b["x"])**2 + (e.y - b["y"])**2
            if dd <= (e.radius*e.radius):
                b["alive"] = False
                e.hp -= 18
                if e.hp <= 0:
                    e.alive = False


def draw_enemy_sprites(z_buffer):
    plane_len = math.tan(FOV / 2)
    NEAR_OVERRIDE = 0.6  # puedes dejarlo como está

    for e in enemies:
        if not e.alive:
            continue

        dx = e.x - player_x
        dy = e.y - player_y
        distance = math.hypot(dx, dy)

        # fuera de rango visible
        if distance < 0.001 or distance > MAX_DISTANCE:
            continue

        # Ángulo relativo
        angle_to = math.atan2(dy, dx) - player_angle
        angle_to = (angle_to + math.pi) % (2 * math.pi) - math.pi
        if abs(angle_to) > FOV / 2:
            continue

        # ---- CLAMP CRÍTICO PARA EVITAR CRASH ----
        # si está muy cerca, forzamos una distancia mínima para el cálculo del tamaño
        if distance < MIN_SPRITE_DIST:
            distance = MIN_SPRITE_DIST

        screen_x = WIDTH / 2 + (math.tan(angle_to) / plane_len) * (WIDTH / 2)

        # tamaño del sprite con límites seguros
        sprite_h = int(HEIGHT / (distance + 1e-6) * 1.3)
        sprite_h = max(2, min(sprite_h, int(MAX_SPRITE_H)))   # tope duro
        sprite_w = max(2, min(int(sprite_h * 0.7), WIDTH * 2))  # ancho razonable

        ccol = int(screen_x)

        # Z-buffer override si está muy cerca
        if not (distance < NEAR_OVERRIDE):
            if 0 <= ccol < WIDTH and distance >= z_buffer[ccol]:
                continue

        # --- Renderizado del sprite con try/except por seguridad ---
        try:
            sprite = pygame.transform.smoothscale(enemy_img, (sprite_w, sprite_h))
        except Exception:
            # si por alguna razón falla el escalado, salta este sprite
            continue

        rect = sprite.get_rect()
        rect.centerx = int(screen_x)
        rect.bottom = int(HEIGHT / 2 + sprite_h / 2)

        # opcional: si quedara completamente lejísimos fuera de pantalla, sáltalo
        if rect.right < -2000 or rect.left > WIDTH + 2000:
            continue

        screen.blit(sprite, rect.topleft)


# =======================
# Minimapa
# =======================

def draw_minimap():
    scale = 8
    mw, mh = MAP_W*scale, MAP_H*scale
    minimap = pygame.Surface((mw, mh))
    minimap.fill(COL_MINIMAP_BG)

    for y in range(MAP_H):
        for x in range(MAP_W):
            if MAP[y][x] == 1:
                pygame.draw.rect(minimap, COL_MINIMAP_WALL, (x*scale, y*scale, scale, scale))

    px, py = int(player_x*scale), int(player_y*scale)
    pygame.draw.circle(minimap, COL_MINIMAP_PLAYER, (px, py), 3)
    dx, dy = math.cos(player_angle)*6, math.sin(player_angle)*6
    pygame.draw.line(minimap, COL_MINIMAP_PLAYER, (px, py), (px+int(dx), py+int(dy)), 2)

    for e in enemies:
        if e.alive:
            ex, ey = int(e.x*scale), int(e.y*scale)
            pygame.draw.circle(minimap, (255,80,80), (ex, ey), 2)

    screen.blit(minimap, (10, HEIGHT-mh-10))

# =======================
# HUD
# =======================

def draw_hud():
    cx, cy = WIDTH//2, HEIGHT//2
    pygame.draw.line(screen, (255,255,255), (cx-8,cy), (cx+8,cy), 1)
    pygame.draw.line(screen, (255,255,255), (cx,cy-8), (cx,cy+8), 1)

    hp_text = font.render(f"HP: {player_health}", True, COL_HUD)
    ammo_text = font.render(f"Ammo: {ammo}{' (recargando...)' if reloading else ''}", True, COL_HUD)
    info_text = font.render("WASD moverse | ← → girar | R recargar | Click dispara", True, COL_INFO)
    screen.blit(hp_text, (10, 10))
    screen.blit(ammo_text, (10, 34))
    screen.blit(info_text, (10, 58))


def draw_gun():
    screen.blit(gun_img, (gun_x, gun_y - int(gun_recoil)))


# =======================
# Loading Screen (barra de carga real)
# =======================

def loading_screen(tasks):
    clock = pygame.time.Clock()
    font_big = pygame.font.SysFont("Arial", 60, bold=True)
    font_small = pygame.font.SysFont("Arial", 28)

    title = font_big.render("Escapa de la Alubia", True, (255, 255, 255))

    progress = 0
    total = len(tasks)

    results = {}

    # --- Bucle de carga real ---
    for i, (name, func) in enumerate(tasks):
        # Ejecutar la tarea (ej: cargar una textura)
        results[name] = func()

        # Calcular progreso real
        progress = int(((i + 1) / total) * 100)

        # Dibujar pantalla
        screen.fill((20, 20, 20))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3 - 50))

        bar_width = WIDTH // 2
        bar_height = 40
        bar_x = WIDTH // 2 - bar_width // 2
        bar_y = HEIGHT // 2
        pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height), 3)

        fill_width = int((progress / 100) * (bar_width - 6))
        pygame.draw.rect(screen, (0, 200, 0), (bar_x + 3, bar_y + 3, fill_width, bar_height - 6))

        percent_text = font_small.render(f"{progress}%", True, (255, 255, 255))
        screen.blit(percent_text, (WIDTH//2 - percent_text.get_width()//2, bar_y + bar_height + 10))

        task_text = font_small.render(f"Cargando {name}...", True, (200, 200, 200))
        screen.blit(task_text, (WIDTH//2 - task_text.get_width()//2, bar_y - 40))

        pygame.display.flip()
        clock.tick(30)

    # --- Al terminar: esperar a ENTER ---
    waiting = True
    press_text = font_small.render("Pulsa ENTER para empezar", True, (255, 255, 0))

    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                waiting = False

        screen.fill((20, 20, 20))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3 - 50))
        screen.blit(press_text, (WIDTH//2 - press_text.get_width()//2, HEIGHT//2))
        pygame.display.flip()
        clock.tick(30)

    return results


def load_wall():
    return pygame.image.load(WALL_PATH).convert()


def load_floor():
    return pygame.image.load(FLOOR_PATH).convert()


def load_gun():
    return pygame.image.load(GUN_PATH).convert_alpha()


def load_enemy():
    return pygame.image.load(ENEMY_PATH).convert_alpha()


tasks = [
    ("paredes", load_wall),
    ("suelo", load_floor),
    ("pistola", load_gun),
    ("enemigos", load_enemy),
]
class RoundManager:
    def __init__(self):
        self.round = 0
        self.spawn_timer = 0.0
        self.spawn_interval = 1.0
        self.max_enemies = 5
        self.enemies_spawned = 0
        self.round_active = False  # ← controla si la ronda está en curso

    def start_next_round(self):
        self.round += 1
        self.enemies_spawned = 0
        self.round_active = True  # la ronda empezó
        print(f"Ronda {self.round} comenzando...")

    def update(self, dt):
        global enemies

        # Si no hay ronda activa y todos los enemigos muertos → nueva ronda
        if not self.round_active and all(not e.alive for e in enemies):
            self.start_next_round()

        if not self.round_active:
            return

        # Spawn progresivo
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval and self.enemies_spawned < self.max_enemies * self.round:
            self.spawn_timer = 0.0
            spawn_enemy()  # llama a la función global
            self.enemies_spawned += 1

        # Si ya spawneó todos los enemigos de esta ronda
        if self.enemies_spawned >= self.max_enemies * self.round:
            self.round_active = False  # ronda completada, espera a que los enemigos mueran

        # Spawn progresivo de enemigos
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval and self.enemies_spawned < self.max_enemies * self.round:
            self.spawn_timer = 0.0
            self.enemies_spawned += 1

def spawn_enemy(self):
    global enemies
    tries = 0
    while True:
        x = random.uniform(1, MAP_W - 1)
        y = random.uniform(1, MAP_H - 1)

        # 1) Tiene que ser suelo
        if MAP[int(y)][int(x)] != 0:
            tries += 1
            if tries > 500:
                break
            continue

        # 2) Colchón contra paredes: miramos vecinos
        blocked = False
        for ny in range(-1, 2):
            for nx in range(-1, 2):
                cx = int(x) + nx
                cy = int(y) + ny
                if 0 <= cx < MAP_W and 0 <= cy < MAP_H:
                    if MAP[cy][cx] != '0':
                        # si está pegado a una pared, lo marcamos como bloqueado
                        if math.hypot((cx + 0.5) - x, (cy + 0.5) - y) < 0.6:
                            blocked = True
                            break
            if blocked:
                break
        if blocked:
            tries += 1
            if tries > 500:
                break
            continue

        # 3) No muy cerca del jugador
        if math.hypot(x - player_x, y - player_y) < 6:
            tries += 1
            if tries > 500:
                break
            continue

        # 4) No encima de otro enemigo
        if any(math.hypot(x - e.x, y - e.y) < 1.2 for e in enemies if e.alive):
            tries += 1
            if tries > 500:
                break
            continue

        # ✅ Posición válida → lo añadimos
        enemies.append(Enemy(x, y))
        break




# =======================
# Main loop limpio (sin joysticks)
# =======================
def main():
    global en_intro
    en_intro = True

    global player_x, player_y, player_angle, time_since_shot, gun_recoil
    global damage_flash, ammo, reloading, reload_timer, enemies

    round_manager = RoundManager()
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        time_since_shot = max(0.0, time_since_shot - dt)
        

        # =====================
        # EVENTOS
        # =====================
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    fire()  # disparo normal con ratón
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r:
                    start_reload()  # recarga normal con teclado

        # =====================
        # RECARGA
        # =====================
        if reloading:
            reload_timer -= dt
            if reload_timer <= 0.0:
                ammo = max_ammo
                reloading = False

        # =====================
        # MOVIMIENTO JUGADOR
        # =====================
        keys = pygame.key.get_pressed()
        speed = MOVE_SPEED * (SPRINT_MULT if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) else 1.0)

        mvx, mvy = 0.0, 0.0
        if keys[pygame.K_w]: mvx += math.cos(player_angle); mvy += math.sin(player_angle)
        if keys[pygame.K_s]: mvx -= math.cos(player_angle); mvy -= math.sin(player_angle)
        if keys[pygame.K_a]: mvx -= math.sin(player_angle); mvy += math.cos(player_angle)
        if keys[pygame.K_d]: mvx += math.sin(player_angle); mvy -= math.cos(player_angle)

        l = math.hypot(mvx, mvy)
        if l > 0.0:
            mvx /= l; mvy /= l
            player_x, player_y = move_with_collision(player_x, player_y, mvx, mvy, speed, dt)

        if keys[pygame.K_LEFT]:  player_angle -= ROT_SPEED * dt
        if keys[pygame.K_RIGHT]: player_angle += ROT_SPEED * dt

        # =====================
        # LÓGICA DEL JUEGO
        # =====================
        update_bullets(dt)
        update_enemies(dt)
        round_manager.update(dt)  # rondas automáticas

        # =====================
        # RENDERIZADO
        # =====================
        z_buffer = cast_and_draw()
        draw_enemy_sprites(z_buffer)
        draw_bullets(z_buffer)
        draw_minimap()
        draw_hud()
        draw_gun()

        # Retroceso pistola + flash daño
        if gun_recoil > 0: 
            gun_recoil = max(0, gun_recoil - RECOIL_RECOVER*dt)
        if damage_flash > 0.0:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            alpha = int(120 * (damage_flash / 0.22))  # intensidad proporcional
            overlay.fill((COL_DMG[0], COL_DMG[1], COL_DMG[2], alpha))
            screen.blit(overlay, (0, 0))
            damage_flash = max(0.0, damage_flash - dt)


        # =====================
        # GAME OVER
        # =====================
        if player_health <= 0:
            go = font.render("GAME OVER - Pulsa ESC para salir", True, (255, 80, 80))
            screen.blit(go, (WIDTH//2 - go.get_width()//2, HEIGHT//2 - go.get_height()//2))
            pygame.display.flip()
            waiting = True
            while waiting:
                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT:
                        pygame.quit(); sys.exit()
                    if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()
                clock.tick(30)

        pygame.display.flip()

    pygame.quit()
    sys.exit()






def menu_screen():
    clock = pygame.time.Clock()
    font_big = pygame.font.SysFont("Arial", 60, bold=True)
    font_small = pygame.font.SysFont("Arial", 32)

    options = ["Jugar", "Ajustes", "Créditos", "Salir"]
    selected = 0

    in_menu = True
    while in_menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    choice = options[selected]
                    if choice == "Jugar":
                        return "play"
                    elif choice == "Ajustes":
                        settings_screen()
                    elif choice == "Créditos":
                        credits_screen()
                    elif choice == "Salir":
                        pygame.quit()
                        sys.exit()

        screen.fill((30, 30, 30))
        title = font_big.render("Escapa de la Alubia", True, (255, 255, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4))

        for i, opt in enumerate(options):
            color = (255, 255, 0) if i == selected else (200, 200, 200)
            text = font_small.render(opt, True, color)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 + i*50))

        pygame.display.flip()
        clock.tick(30)


def settings_screen():
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 32)

    settings = {
        "Calidad": "Alta",
        "Volumen": 100
    }
    options = list(settings.keys())
    selected = 0

    in_settings = True
    while in_settings:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % (len(options) + 1)
                elif event.key == pygame.K_UP:
                    selected = (selected - 1) % (len(options) + 1)
                elif event.key == pygame.K_LEFT:
                    if selected < len(options):
                        if options[selected] == "Calidad":
                            settings["Calidad"] = "Baja" if settings["Calidad"] == "Alta" else "Alta"
                        elif options[selected] == "Volumen":
                            settings["Volumen"] = max(0, settings["Volumen"] - 10)
                elif event.key == pygame.K_RIGHT:
                    if selected < len(options):
                        if options[selected] == "Calidad":
                            settings["Calidad"] = "Alta" if settings["Calidad"] == "Baja" else "Baja"
                        elif options[selected] == "Volumen":
                            settings["Volumen"] = min(100, settings["Volumen"] + 10)
                elif event.key == pygame.K_RETURN:
                    if selected == len(options):  # "Volver"
                        in_settings = False

        screen.fill((20, 20, 20))
        title = font.render("Ajustes", True, (255, 255, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4))

        for i, opt in enumerate(options):
            color = (255, 255, 0) if i == selected else (200, 200, 200)
            text = font.render(f"{opt}: {settings[opt]}", True, color)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 + i*40))

        # Opción volver
        volver_color = (255, 255, 0) if selected == len(options) else (200, 200, 200)
        volver = font.render("Volver", True, volver_color)
        screen.blit(volver, (WIDTH//2 - volver.get_width()//2, HEIGHT//2 + len(options)*40))

        pygame.display.flip()
        clock.tick(30)


def credits_screen():
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 32)
    small = pygame.font.SysFont("Arial", 24)

    in_credits = True
    while in_credits:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                in_credits = False

        screen.fill((0, 0, 30))
        title = font.render("Créditos", True, (255, 255, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4))

        text1 = small.render("Hecho por: Iván GM, CEO de Alubia Games", True, (200, 200, 200))
        text2 = small.render("Motor: Pygame", True, (200, 200, 200))
        text3 = small.render("Inspirado en DOOM/Wolfstein3D", True, (200, 200, 200))

        screen.blit(text1, (WIDTH//2 - text1.get_width()//2, HEIGHT//2))
        screen.blit(text2, (WIDTH//2 - text2.get_width()//2, HEIGHT//2 + 30))
        screen.blit(text3, (WIDTH//2 - text3.get_width()//2, HEIGHT//2 + 60))

        press = small.render("Pulsa ENTER para volver", True, (255, 255, 0))
        screen.blit(press, (WIDTH//2 - press.get_width()//2, HEIGHT - 80))

        pygame.display.flip()
        clock.tick(30)


# =======================
# Splash screen estilo "PopCap"
# =======================

def splash_screen():
    logo = pygame.image.load("assets/alubia.png").convert_alpha()

    # Escalar para que quepa completamente en pantalla
    scale_w = WIDTH / logo.get_width()
    scale_h = HEIGHT / logo.get_height()
    scale = min(scale_w, scale_h)  # usar el menor para que no se recorte

    new_width = int(logo.get_width() * scale)
    new_height = int(logo.get_height() * scale)
    logo = pygame.transform.smoothscale(logo, (new_width, new_height))

    # Centrar la imagen en la pantalla
    logo_rect = logo.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    clock = pygame.time.Clock()
    alpha = 0
    fade_in = True
    display_time = 1500
    hold_timer = 0

    running = True
    while running:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))

        # Fade in / hold / fade out
        if fade_in:
            alpha += 300 * (dt / 1000)
            if alpha >= 255:
                alpha = 255
                fade_in = False
        elif hold_timer < display_time:
            hold_timer += dt
        else:
            alpha -= 300 * (dt / 1000)
            if alpha <= 0:
                running = False
                alpha = 0

        screen.fill((0, 0, 0))
        screen.blit(logo, logo_rect)
        overlay.set_alpha(int(255 - alpha))
        screen.blit(overlay, (0, 0))
        pygame.display.flip()








# =======================
# Punto de entrada
# =======================
if __name__ == "__main__":
    # 1) Splash de presentación
    splash_screen()

    # 2) Pantalla de carga de assets y asignación a globales
    loaded = loading_screen(tasks)
    wall_tex = loaded["paredes"]
    floor_tex = loaded["suelo"]
    gun_img   = loaded["pistola"]
    enemy_img = loaded["enemigos"]

    # Recalcular rect de la pistola por si cambió tamaño al recargar
    gun_rect = gun_img.get_rect()
    gun_scale = 260 / gun_rect.height if gun_rect.height > 260 else 1.0
    gun_img = pygame.transform.smoothscale(
        gun_img,
        (int(gun_rect.width*gun_scale), int(gun_rect.height*gun_scale))
    )
    gun_rect = gun_img.get_rect()
    gun_x = WIDTH - gun_rect.width - 20
    gun_y = HEIGHT - gun_rect.height - 16

    # 3) Menú principal → juego
    choice = menu_screen()
    if choice == "play":
        main()
