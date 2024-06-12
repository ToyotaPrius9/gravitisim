import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Solar System Simulator - Intro")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Fonts
font = pygame.font.SysFont('Arial', 40)
small_font = pygame.font.SysFont('Arial', 20)

# Texts
title_text = font.render('Welcome to the Solar System Simulator', True, WHITE)
instructions_text = small_font.render('Press ENTER to start', True, WHITE)

# Main loop for the intro screen
def intro_screen():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    pygame.quit()
                    return  # Exit the intro screen and go to the main simulation

        screen.fill(BLACK)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//2 - title_text.get_height()//2 - 50))
        screen.blit(instructions_text, (WIDTH//2 - instructions_text.get_width()//2, HEIGHT//2 + instructions_text.get_height()//2))

        pygame.display.flip()

if __name__ == "__main__":
    intro_screen()
