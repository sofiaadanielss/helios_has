import pygame
import random
import os

# --- Pygame Initialization ---
pygame.init()

# --- Screen Dimensions ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Level 3: Repair the Satellite")

# --- Colors ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLOR_DAMAGED = (255, 0, 0)
COLOR_REPAIRED = (0, 255, 0)
COLOR_BAR_BACKGROUND = (80, 80, 80)
COLOR_PROGRESS_BAR = (100, 200, 255)

# --- Clock to control game speed ---
clock = pygame.time.Clock()
FPS = 60

# --- Load sprites ---
def load_and_scale_sprite(file_path, size=None):
    try:
        image = pygame.image.load(file_path).convert_alpha()
        if size:
            image = pygame.transform.scale(image, size)
        return image
    except pygame.error as e:
        print(f"Error loading image '{file_path}': {e}")
        # Return a magenta surface as a placeholder if image fails
        error_surface_size = size if size else (50, 50)
        surface = pygame.Surface(error_surface_size)
        surface.fill((255, 0, 255))
        return surface

# --- Load main sprites ---
astronaut_image = load_and_scale_sprite(os.path.join("astronaut.png"), (60, 60))
satellite_image = load_and_scale_sprite(os.path.join("satellite.png"), (800, 400))
particle_images_paths = [os.path.join("particle1.png"), os.path.join("particle2.png"), os.path.join("particle3.png")]
particle_images = [load_and_scale_sprite(path) for path in particle_images_paths if path]
heart_image = load_and_scale_sprite(os.path.join("heart.png"), (30, 30))

# --- CAMBIO 1: Cargar la imagen de fondo ---
background_image = load_and_scale_sprite(os.path.join("background.png"), (SCREEN_WIDTH, SCREEN_HEIGHT))
# Si la imagen de fondo no se carga, usa un fondo negro sólido
if not background_image:
    background_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    background_image.fill(BLACK)

# --- Game Object Classes ---

class Astronaut(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        self.original_image = image
        self.image = image
        self.damage_image = self.original_image.copy()
        self.damage_image.fill((255, 0, 0), special_flags=pygame.BLEND_RGB_MULT)
        self.rect = self.image.get_rect(center=(100, SCREEN_HEIGHT // 2))
        self.mask = pygame.mask.from_surface(self.image)
        self.vel_x, self.vel_y = 0, 0
        self.speed = 0.5
        self.friction = 0.98
        self.lives = 3
        self.damage_timer = 0

    def take_damage(self):
        self.damage_timer = 30

    def update(self):
        self.vel_x *= self.friction
        self.vel_y *= self.friction
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        self.rect.clamp_ip(screen.get_rect())
        if self.damage_timer > 0:
            self.image = self.damage_image
            self.damage_timer -= 1
        else:
            self.image = self.original_image

# --- CAMBIO 2: Las partículas vuelven a su comportamiento original ---
class SolarParticle(pygame.sprite.Sprite):
    def __init__(self, images):
        super().__init__()
        original_image = random.choice(images)
        random_size = random.randint(30, 50)
        self.image = pygame.transform.scale(original_image, (random_size, random_size))
        self.rect = self.image.get_rect(
            x=SCREEN_WIDTH + random.randint(20, 100),
            y=random.randint(0, SCREEN_HEIGHT - random_size) # Aparece en una altura aleatoria
        )
        self.mask = pygame.mask.from_surface(self.image)
        self.speed_x = random.randint(-5, -2)
        self.speed_y = random.uniform(-1, 1)

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        if self.rect.right < 0:
            self.kill()

class Satellite(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))

class DamagedPanel(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(COLOR_DAMAGED)
        self.rect = self.image.get_rect(center=(x, y))
        self.is_repaired = False

    def repair(self):
        self.is_repaired = True
        self.image.fill(COLOR_REPAIRED)

# --- Function to reset the game ---
def reset_game():
    global game_over, win, game_state, minigame_progress, active_panel
    game_over, win, game_state = False, False, "FLYING"
    minigame_progress, active_panel = 0, None
    player.lives = 3
    player.rect.center = (SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2)
    player.vel_x, player.vel_y = 0, 0
    player.damage_timer = 0
    for panel in damaged_panels:
        panel.is_repaired = False
        panel.image.fill(COLOR_DAMAGED)
    for particle in particles:
        particle.kill()

# --- Create Game Objects ---
all_sprites = pygame.sprite.Group()
particles = pygame.sprite.Group()
damaged_panels = pygame.sprite.Group()

satellite = Satellite(satellite_image, 10, 250)
all_sprites.add(satellite)

player = Astronaut(astronaut_image)
all_sprites.add(player)

panel_positions = [(200, 300), (600, 300), (200, 500), (600, 500)]
for pos in panel_positions:
    panel = DamagedPanel(pos[0], pos[1])
    all_sprites.add(panel)
    damaged_panels.add(panel)

# --- Game and Minigame Variables ---
game_state, active_panel, minigame_progress = "FLYING", None, 0
MINIGAME_TARGET_SCORE = 100
running, game_over, win = True, False, False
particle_spawn_timer = 0
font = pygame.font.Font(None, 48)
small_font = pygame.font.Font(None, 28)
button_rect = pygame.Rect(0, 0, 0, 0)

# --- Main Game Loop ---
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if game_state == "MINIGAME" and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            minigame_progress += 5
        if event.type == pygame.MOUSEBUTTONDOWN and game_over:
            if button_rect.collidepoint(event.pos):
                reset_game()

    if not game_over:
        if game_state == "FLYING":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]: player.vel_x -= player.speed
            if keys[pygame.K_RIGHT]: player.vel_x += player.speed
            if keys[pygame.K_UP]: player.vel_y -= player.speed
            if keys[pygame.K_DOWN]: player.vel_y += player.speed

            particle_spawn_timer += 1
            if particle_spawn_timer > 30:
                if particle_images:
                    # --- CAMBIO 3: Se crea la partícula sin pasarle la posición del sol ---
                    new_particle = SolarParticle(particle_images)
                    all_sprites.add(new_particle)
                    particles.add(new_particle)
                particle_spawn_timer = 0

            all_sprites.update()

            if pygame.sprite.spritecollide(player, particles, True, pygame.sprite.collide_mask):
                player.lives -= 1
                player.take_damage()
                if player.lives <= 0:
                    game_over = True

            collided_panels = pygame.sprite.spritecollide(player, damaged_panels, False)
            for panel in collided_panels:
                if not panel.is_repaired:
                    game_state, active_panel, minigame_progress = "MINIGAME", panel, 0
                    break

        elif game_state == "MINIGAME":
            if minigame_progress >= MINIGAME_TARGET_SCORE:
                active_panel.repair()
                game_state, active_panel = "FLYING", None

        if all(p.is_repaired for p in damaged_panels):
            win, game_over = True, True

    # --- Drawing Section ---
    # --- CAMBIO 4: Dibujar la imagen de fondo en lugar de un color sólido ---
    screen.blit(background_image, (0, 0))

    all_sprites.draw(screen)
    for i in range(player.lives):
        screen.blit(heart_image, (10 + i * 35, 10))

    if game_state == "MINIGAME":
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        bar_x, bar_y, bar_w, bar_h = 200, 280, 400, 40
        progress_w = (minigame_progress / MINIGAME_TARGET_SCORE) * bar_w
        pygame.draw.rect(screen, COLOR_BAR_BACKGROUND, (bar_x, bar_y, bar_w, bar_h))
        pygame.draw.rect(screen, COLOR_PROGRESS_BAR, (bar_x, bar_y, progress_w, bar_h))
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_w, bar_h), 2)

        inst_text = font.render("Repairing!", True, WHITE)
        screen.blit(inst_text, inst_text.get_rect(centerx=SCREEN_WIDTH / 2, y=230))
        key_text = small_font.render("Press [SPACE] quickly to repair", True, WHITE)
        screen.blit(key_text, key_text.get_rect(centerx=SCREEN_WIDTH / 2, y=340))

    if game_over:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        if win:
            msg_text = font.render("MISSION ACCOMPLISHED!", True, COLOR_REPAIRED)
            sub_text = small_font.render("You have repaired the satellite.", True, WHITE)
            screen.blit(msg_text, msg_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20)))
            screen.blit(sub_text, sub_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20)))
        else:
            title = font.render("MISSION FAILED", True, COLOR_DAMAGED)
            sub = small_font.render("The panels could not be repaired.", True, WHITE)
            c1 = small_font.render("Without power, the communications satellite is offline.", True, WHITE)
            c2 = small_font.render("Global communications and GPS will be affected.", True, WHITE)
            screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100)))
            screen.blit(sub, sub.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60)))
            screen.blit(c1, c1.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))
            screen.blit(c2, c2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30)))

        button_rect.update(SCREEN_WIDTH // 2 - 125, SCREEN_HEIGHT // 2 + 120, 250, 50)
        button_color = (80, 80, 150)
        button_hover_color = (110, 110, 180)

        if button_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(screen, button_hover_color, button_rect, border_radius=10)
        else:
            pygame.draw.rect(screen, button_color, button_rect, border_radius=10)

        btn_text = font.render("Try Again", True, WHITE)
        screen.blit(btn_text, btn_text.get_rect(center=button_rect.center))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()