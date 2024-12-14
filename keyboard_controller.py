import pygame
import sys
from robot_control import *


override = False

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
        move_robot_forward(override)
        
    elif key_states[pygame.K_s]:
        print("Robot moves DOWN")
        move_backward(override)
        
    elif key_states[pygame.K_a]:
        print("Robot moves LEFT")
        move_robot_left(override)
        
    elif key_states[pygame.K_d]:
        print("Robot moves RIGHT")
        move_robot_right(override)
        
    elif key_states[pygame.K_SPACE]:
        print("Robot stops")
        # override = True
        stop_robot(override)
        # override = False 
          
    elif key_states[pygame.K_LEFT]:
        print("Robot turns LEFT")
        turn_left_at_junction(override)
        
    elif key_states[pygame.K_RIGHT]:
        print("Robot turns RIGHT")
        turn_right_at_junction(override)
        
    
    # else:
    #     nothing()

    # Update screen
    pygame.display.flip()

    # Cap the frame rate
    pygame.time.Clock().tick(30)

# Clean up
pygame.quit()
sys.exit()
