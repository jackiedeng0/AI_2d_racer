"""
    Loads a level and runs racer.
    Driver can be configured to player or AI.
"""

import pygame
import json
from objects import Car, LiDAR_Car
from drivers import Driver, Player_Driver, Random_Driver, Momentum_Driver

pygame.init()
SCREEN_HEIGHT = 800
SCREEN_WIDTH = 1400
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
running = True

BORDER_WIDTH = 50
border_rects = []
border_rects.append(pygame.Rect(0, 0, SCREEN_WIDTH, BORDER_WIDTH))
border_rects.append(pygame.Rect(0, SCREEN_HEIGHT -
                    BORDER_WIDTH, SCREEN_WIDTH, BORDER_WIDTH))
border_rects.append(pygame.Rect(0, 0, BORDER_WIDTH, SCREEN_HEIGHT))
border_rects.append(pygame.Rect(SCREEN_WIDTH - BORDER_WIDTH,
                    0, BORDER_WIDTH, SCREEN_HEIGHT))

# Default car position
start_x = 0
start_y = 0
start_angle = 0
goals = []
obstacles = []
# Load level
with open("levels/turn.json") as level_f:
    level = json.loads(level_f.read())
    start_x = level["start"]["x"]
    start_y = level["start"]["y"]
    start_angle = level["start"]["angle"]
    if "goals" in level.keys():
        for level_goal in level["goals"]:
            goals.append(pygame.Rect(
                level_goal["left"], level_goal["top"], level_goal["width"], level_goal["height"]))
    if "obstacles" in level.keys():
        for level_obst in level["obstacles"]:
            obstacles.append(pygame.Rect(
                level_obst["left"], level_obst["top"], level_obst["width"], level_obst["height"]))

car = LiDAR_Car(start_x, start_y, start_angle)
driver = Player_Driver(car)
win_count = 0


def reset_level():
    car.force_position(start_x, start_y, start_angle)


while running:

    # Event polling - Currently used for quitting
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clears screen of last frame
    screen.fill("#eeeeee")

    # Controls
    forward, turn_left = driver.drive_command()
    car.apply_command(forward, turn_left)

    # Update Car Position
    car.simulate_friction()
    car.position_frame_update()

    # Collisions
    for goal in goals:
        if (car.collide_rect(goal)):
            pygame.draw.rect(screen, "#6EB141", goal)
            win_count += 1
            reset_level()
        else:
            pygame.draw.rect(screen, "#93F651", goal)
    for obst in obstacles:
        if (car.collide_rect(obst)):
            pygame.draw.rect(screen, "#B05637", obst)
            reset_level()
        else:
            pygame.draw.rect(screen, "#F27549", obst)
        if type(car) is LiDAR_Car:
            car.beam_collide_rect_register(obst)

    # Going Off Screen
    for border_rect in border_rects:
        if (car.collide_rect(border_rect)):
            reset_level()
        if type(car) is LiDAR_Car:
            car.beam_collide_rect_register(border_rect)
        pygame.draw.rect(screen, "#111111", border_rect)

    # Draw car on top
    car.draw(screen)

    # Draw LiDAR Beams
    if type(car) is LiDAR_Car:
        car.draw_beams(screen)

    # Displays changes to screen
    pygame.display.flip()

    clock.tick(60)

pygame.quit()
