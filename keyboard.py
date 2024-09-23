import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up the screen
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Robot Control")

# Colors
WHITE = (255, 255, 255)

# Dictionary to store key states
key_states = {
    pygame.K_w: False,
    pygame.K_s: False,
    pygame.K_a: False,
    pygame.K_d: False,
    pygame.K_SPACE: False,
    pygame.K_LEFT: False,
    pygame.K_RIGHT: False
}

# Main loop
running = True
while running:
    screen.fill(WHITE)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key in key_states:
                key_states[event.key] = True
        elif event.type == pygame.KEYUP:
            if event.key in key_states:
                key_states[event.key] = False

    # Check key states and print direction
    if key_states[pygame.K_w]:
        print("Robot moves UP")
    elif key_states[pygame.K_s]:
        print("Robot moves DOWN")
    elif key_states[pygame.K_a]:
        print("Robot moves LEFT")
    elif key_states[pygame.K_d]:
        print("Robot moves RIGHT")
    elif key_states[pygame.K_SPACE]:
        print("Robot stops")
    elif key_states[pygame.K_LEFT]:
        print("Robot turns LEFT")
    elif key_states[pygame.K_RIGHT]:
        print("Robot turns RIGHT")

    # Update screen
    pygame.display.flip()

    # Cap the frame rate
    pygame.time.Clock().tick(30)

# Clean up
pygame.quit()
sys.exit()
