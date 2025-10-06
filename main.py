import pygame
import sys


def initialize_game():
    pygame.init()
    pygame.mixer.init()

    try:
        pygame.mixer.music.load("./sound_effects/sonido_espacio.mp3")
        pygame.mixer.music.play(-1)
    except Exception as e:
        print("Music load/play error:", e)

    screen_width = 800
    screen_height = 600

    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("HELIOS: The Space Weather Game")

    try:
        background_image = pygame.image.load('levels/assets/images/helioss.jpg').convert()
        background_image = pygame.transform.scale(background_image, (screen_width, screen_height))
    except pygame.error as e:
        background_image=None
        
    return screen, screen_width, screen_height, background_image

def draw_intro_screen(screen, screen_width, screen_height, background_image):

    white = (255, 255, 255)
    black = (0, 0, 0)
    gray = (200, 200, 200)

    if background_image:
        screen.blit(background_image, (0, 0))
    else:
        screen.fill(black)

    font_large = pygame.font.Font(None, 80)
    font_medium = pygame.font.Font(None, 40)
    font_small = pygame.font.Font(None, 30)

    start_text = font_small.render("Click to Start", True, black)
        
    button_width = 200
    button_height = 50
    button_rect = pygame.Rect(0, 0, button_width, button_height)
    button_rect.center = (screen_width / 2, screen_height / 2 + 150)

    pygame.draw.rect(screen, gray, button_rect)
    
    start_text_rect = start_text.get_rect(center=button_rect.center)
    screen.blit(start_text, start_text_rect)

    pygame.display.flip()
    return button_rect

def main():
    screen, screen_width, screen_height, background_image = initialize_game()

    start_button_rect = draw_intro_screen(screen, screen_width, screen_height, background_image)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                
                if start_button_rect.collidepoint(event.pos):
                    
                    running = False 

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()