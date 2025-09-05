import colors
import pygame
import time

# Initialize Pygame
pygame.init()

# Set up the display
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Simple Pie Game")

# Game clock
clock = pygame.time.Clock()

# Get color values
color_values = list(colors.colors.values())
index = 0

# Game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


    # Fill the screen with each color in sequence
    pygame.draw.circle(screen, colors.DARKER_GREEN, (600, 300), 50)
    for x in range(0, WINDOW_WIDTH, 10):
        if index >= len(color_values):
            break
        pygame.draw.line(screen, color_values[index % len(color_values)], (x, 0), (x, WINDOW_HEIGHT), 10)
        pygame.display.flip()
        index += 1
        time.sleep(0.01)

    # Cap the framerate
    clock.tick(60)

# Quit Pygame
pygame.quit()
