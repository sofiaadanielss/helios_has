import pygame
import random
import math
import os
import sys

pygame.init()

SCREEN_WIDTH = 700
SCREEN_HEIGHT = 900

PLASMA_COLOR = (255, 50, 0)
TEXT_COLOR = (255, 255, 255)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sun Dodge: The Solar Flare Protocol")
clock = pygame.time.Clock()
font_lg = pygame.font.Font(None, 74)
font_md = pygame.font.Font(None, 48)
font_sm = pygame.font.Font(None, 36)

# Obtener la ruta base del script para cargar recursos
script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

# Carga la imagen de fondo de forma segura con una ruta de carpeta
background_image = None
try:
    image_path = os.path.join(script_dir, 'assets', 'images', 'lvl1.png')
    background_image = pygame.image.load(image_path).convert()
except pygame.error as e:
    print(f"Error al cargar la imagen de fondo: {e}")
    print(f"Por favor, asegúrate de que la imagen 'lvl1.png' esté en la carpeta: {os.path.join(script_dir, 'assets', 'images')}")

if background_image:
    background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Carga la imagen del sol
sun_image = None
sun_original_size = None
try:
    sun_image_path = os.path.join(script_dir, 'assets', 'images', 'sun.png')
    sun_image = pygame.image.load(sun_image_path).convert_alpha()
    sun_original_size = sun_image.get_size()
    print(f"Imagen del sol cargada correctamente - Tamaño original: {sun_original_size}")
except pygame.error as e:
    print(f"Error al cargar la imagen del sol: {e}")
    print(f"Por favor, asegúrate de que la imagen 'sun.png' esté en la carpeta: {os.path.join(script_dir, 'assets', 'images')}")

# Carga la imagen de plasma
plasma_image = None
try:
    plasma_image_path = os.path.join(script_dir, 'assets', 'images', 'plasma_ball.png')
    plasma_image = pygame.image.load(plasma_image_path).convert_alpha()
    print("Imagen de plasma cargada correctamente")
except pygame.error as e:
    print(f"Error al cargar la imagen de plasma: {e}")
    print(f"Por favor, asegúrate de que la imagen 'plasma_ball.png' esté en la carpeta: {os.path.join(script_dir, 'assets', 'images')}")


class Sun:
    """Represents the player-controlled Sun object."""
    def __init__(self):
        self.base_radius = 30
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 60
        self.base_speed = 7
        self.charge = 0 
        self.is_flaring = False
        self.current_scaled_image = None
        self.current_image_rect = None
        self.growth_rate = 2

    def move(self, direction):
        """Moves the sun left (-1) or right (1)."""
        if not self.is_flaring:
            # La velocidad aumenta con la carga (máximo 100% más rápido)
            speed_boost = min(self.charge * 1.0, 100)
            current_speed = self.base_speed + (self.base_speed * speed_boost / 100)
            
            self.x += direction * current_speed
            
            # Límites suaves
            if self.x < 0:
                self.x = 0
            if self.x > SCREEN_WIDTH:
                self.x = SCREEN_WIDTH

    def get_current_radius(self):
        """Calcula el radio actual del sol basado en la carga."""
        return self.base_radius + (self.charge * self.growth_rate)
    
    def get_scaled_image(self):
        """Escala la imagen del sol manteniendo la proporción original."""
        if not sun_image:
            return None, None
            
        current_radius = self.get_current_radius()
        
        # Calcular el tamaño manteniendo la proporción
        scale_factor = (current_radius * 2) / max(sun_original_size)
        new_width = int(sun_original_size[0] * scale_factor)
        new_height = int(sun_original_size[1] * scale_factor)
        
        scaled_image = pygame.transform.scale(sun_image, (new_width, new_height))
        return scaled_image, (new_width, new_height)
    
    def get_collision_rect(self):
        """Devuelve el rectángulo de colisión actual del sol."""
        if self.current_image_rect:
            return self.current_image_rect
        else:
            current_radius = self.get_current_radius()
            return pygame.Rect(self.x - current_radius, self.y - current_radius, 
                             current_radius * 2, current_radius * 2)
        
    def draw(self, surface):
        current_radius = self.get_current_radius()
        
        if sun_image:
            self.current_scaled_image, new_size = self.get_scaled_image()
            if self.current_scaled_image:
                self.current_image_rect = self.current_scaled_image.get_rect(center=(self.x, self.y))
                surface.blit(self.current_scaled_image, self.current_image_rect)
            else:
                self.draw_fallback(surface, current_radius)
                self.current_image_rect = None
        else:
            self.draw_fallback(surface, current_radius)
            self.current_image_rect = None
    
    def draw_fallback(self, surface, current_radius):
        """Dibuja un círculo como respaldo cuando no hay imagen."""
        if self.charge < 10:
            color = (255, 255, 150)
        elif self.charge < 20:
            color = (255, 200, 0)
        elif self.charge < 30:
            color = (255, 150, 0)
        else:
            color = (255, 100, 0)
            
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), int(current_radius))
        
        r, g, b = color
        glow_color = (max(0, r-50), max(0, g-50), max(0, b-50))
        pygame.draw.circle(surface, glow_color, (int(self.x), int(self.y)), int(current_radius), 5)


class Plasma:
    """Represents falling plasma that makes the sun grow."""
    def __init__(self, base_speed=3, speed_increase=0):
        self.radius = random.randint(20, 35)
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = -self.radius
        # Velocidad base + aumento progresivo
        self.speed = random.uniform(base_speed, base_speed + 2) + speed_increase
        self.color = PLASMA_COLOR
        self.image = plasma_image
        self.scaled_image = None
        self.image_rect = None
        
        if self.image:
            size = self.radius * 2 
            self.scaled_image = pygame.transform.scale(self.image, (size, size))
            self.image_rect = self.scaled_image.get_rect(center=(int(self.x), int(self.y)))

    def update(self):
        """Moves the plasma downward."""
        self.y += self.speed
        if self.image_rect:
            self.image_rect.center = (int(self.x), int(self.y))

    def draw(self, surface):
        """Draws the plasma as an image or a circle if image not loaded."""
        if self.scaled_image and self.image_rect:
            surface.blit(self.scaled_image, self.image_rect)
        else:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
            # Efecto de brillo interno
            inner_color = (255, 100, 50)
            pygame.draw.circle(surface, inner_color, (int(self.x), int(self.y)), self.radius - 5)


def check_collision(sun, plasma):
    """Verifica colisión usando distancia circular."""
    sun_current_radius = sun.get_current_radius()
    distance = math.sqrt((sun.x - plasma.x)**2 + (sun.y - plasma.y)**2)
    return distance < (sun_current_radius + plasma.radius)


def draw_text(surface, text, font, color, x, y, center=False):
    """Utility function to draw text."""
    text_surface = font.render(text, True, color)
    rect = text_surface.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(text_surface, rect)


def solar_flare_animation(surface, sun):
    max_radius = int(SCREEN_WIDTH * 1.5)
    for i in range(10):
        radius = int(max_radius * (i / 10))
        alpha = 255 - int(255 * (i / 10))
        
        temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        color = (255, 100, 0, alpha) 
        pygame.draw.circle(temp_surface, color, (sun.x, sun.y), radius)
        surface.blit(temp_surface, (0, 0))


def game_loop():
    running = True
    
    player_sun = Sun()
    plasmas = []
    
    spawn_time = 0
    base_spawn_rate = 60  # Tasa base de spawn
    current_spawn_rate = base_spawn_rate
    
    # Variables para aumentar dificultad
    game_time = 0
    speed_increase = 0
    spawn_acceleration = 0
    
    flare_cycles = 0
    
    game_over = False
    game_over_start_time = 0
    flare_duration = 3000  # Reducido a 3 segundos
    
    start_time = pygame.time.get_ticks() 
    elapsed_time = 0
    end_game_time = 0
    
    solar_flare_occurred = False  # Nueva variable para controlar el solar flare
    
    while running:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                player_sun = Sun()
                plasmas = []
                game_over = False
                game_over_start_time = 0
                flare_cycles = 0 
                start_time = pygame.time.get_ticks()
                end_game_time = 0
                # Resetear variables de dificultad
                current_spawn_rate = base_spawn_rate
                speed_increase = 0
                spawn_acceleration = 0
                game_time = 0
                solar_flare_occurred = False
                
        keys = pygame.key.get_pressed()
        
        if not game_over and not solar_flare_occurred:  # Solo actualizar si no hay solar flare
            game_time += 1
            
            # Aumentar dificultad con el tiempo
            if game_time % 600 == 0:  # Cada 10 segundos aproximadamente
                speed_increase += 0.8  # Los plasmas caen más rápido
                spawn_acceleration += 2  # Aparecen más seguido
                current_spawn_rate = max(15, base_spawn_rate - spawn_acceleration)  # Mínimo 15 frames entre spawns
                print(f"Dificultad aumentada! Velocidad: +{speed_increase}, Spawn rate: {current_spawn_rate}")
            
            if keys[pygame.K_LEFT]:
                player_sun.move(-1)
            if keys[pygame.K_RIGHT]:
                player_sun.move(1)

            # Spawn de plasmas (solo plasmas)
            spawn_time += 4
            if spawn_time >= current_spawn_rate:
                plasmas.append(Plasma(base_speed=5, speed_increase=speed_increase))
                spawn_time = 0

            # Actualizar y verificar colisiones con plasmas
            for plasma in list(plasmas): 
                plasma.update()
                
                if check_collision(player_sun, plasma):
                    # COLISIÓN CON PLASMA = CRECIMIENTO
                    player_sun.charge += 6
                    plasmas.remove(plasma)
                    
                    current_radius = player_sun.get_current_radius()
                    max_possible_radius = min(SCREEN_WIDTH, SCREEN_HEIGHT) // 2
                    
                    # CORREGIDO: Condición para solar flare
                    if current_radius >= max_possible_radius * 0.9:  # 90% del tamaño máximo
                        flare_cycles += 1
                        player_sun.charge = 0
                        solar_flare_occurred = True  # Activar solar flare
                        game_over_start_time = pygame.time.get_ticks()  # Iniciar temporizador
                        player_sun.is_flaring = True
                        print(f"¡SOLAR FLARE! Ciclos completados: {flare_cycles}")
                        
                elif plasma.y > SCREEN_HEIGHT + plasma.radius:
                    plasmas.remove(plasma)

            # Dibujar
            if background_image:
                screen.blit(background_image, (0, 0))
            else:
                screen.fill((0, 0, 20)) 

            elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
            
            # Información en pantalla
            draw_text(screen, f"Time: {elapsed_time}s", font_sm, TEXT_COLOR, 10, 50)
            draw_text(screen, f"Plasmas: {player_sun.charge}", font_sm, TEXT_COLOR, 10, 110)

            for plasma in plasmas:
                plasma.draw(screen)

            player_sun.draw(screen)

            draw_text(screen, "Eat the plasmas to grow!", font_sm, TEXT_COLOR, SCREEN_WIDTH // 2, 10, center=True)

        # Mostrar animación de solar flare y luego game over
        if solar_flare_occurred:
            time_elapsed_since_flare = pygame.time.get_ticks() - game_over_start_time
            
            if time_elapsed_since_flare < flare_duration:
                # Mostrar animación de solar flare
                solar_flare_animation(screen, player_sun)
                draw_text(screen, "SOLAR FLARE RELEASE!", font_lg, (255, 0, 0), SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, center=True)
                draw_text(screen, "The sun has grown too large!", font_md, (255, 255, 255), SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, center=True)
            else:
                # Después de la animación, mostrar pantalla de game over
                game_over = True
                screen.fill((50, 0, 0)) 
                draw_text(screen, "SOLAR FLARE COMPLETE", font_lg, (255, 255, 255), SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100, center=True)
                draw_text(screen, f"Flares Released: {flare_cycles}", font_md, (255, 255, 255), SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20, center=True)
                draw_text(screen, f"Time Survived: {elapsed_time}s", font_md, (255, 255, 255), SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20, center=True)
                draw_text(screen, "Press SPACE to Restart", font_sm, (150, 150, 150), SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80, center=True)
                
                if end_game_time == 0:
                    end_game_time = pygame.time.get_ticks()
                if pygame.time.get_ticks() - end_game_time > 5000:
                    running = False

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    
if __name__ == '__main__':
    game_loop()