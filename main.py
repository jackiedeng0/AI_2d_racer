"""
    Loads a level and runs racer.
    Driver can be configured to player or AI.
"""

import pygame
import json
from objects import *
from drivers import *

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

cars = []
cars.append(LiDAR_Car(start_x, start_y, start_angle))
cars.append(LiDAR_Car(start_x, start_y, start_angle))
cars.append(LiDAR_Car(start_x, start_y, start_angle))
drivers = []
drivers.append(One_Hidden_NN_Driver(cars[0]))
drivers.append(Momentum_Driver(cars[0]))
drivers.append(Player_Driver(cars[1]))

win_count = 0
font = pygame.font.SysFont(None, 24)


def reset_car(car):
    car.force_position(start_x, start_y, start_angle)


def draw_static_objects(goals, obstacles, border_rects):
    for goal in goals:
        pygame.draw.rect(screen, "#93F651", goal)
    for obst in obstacles:
        pygame.draw.rect(screen, "#F27549", obst)
    for border_rect in border_rects:
        pygame.draw.rect(screen, "#111111", border_rect)


def handle_all_collisions(car, goals, obstacles, border_rects):
    win = False
    for goal in goals:
        if (car.collide_rect(goal)):
            win = True
            reset_car(car)

    for obst in obstacles:
        if (car.collide_rect(obst)):
            reset_car(car)
        if type(car) is LiDAR_Car:
            car.beam_collide_rect_register(obst)

    for border_rect in border_rects:
        if (car.collide_rect(border_rect)):
            reset_car(car)
        if type(car) is LiDAR_Car:
            car.beam_collide_rect_register(border_rect)

    return win


while running:

    # Event polling - Currently used for quitting
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clears screen of last frame
    screen.fill("#eeeeee")

    draw_static_objects(goals, obstacles, border_rects)

    for i in range(len(cars)):

        # Controls
        forward, turn_left = drivers[i].drive_command()
        cars[i].apply_command(forward, turn_left)

        # Update Car Position
        cars[i].simulate_friction()
        cars[i].position_frame_update()

        # All Collisions
        win_count += 1 if handle_all_collisions(
            cars[i], goals, obstacles, border_rects) else 0

        # Draw car on top
        cars[i].draw(screen)

        # Draw LiDAR Beams
        if type(cars[i]) is LiDAR_Car:
            cars[i].draw_beams(screen)

    # Text
    text_img = font.render("Wins: " + str(win_count), False, "#ffffff")
    screen.blit(text_img, (20, 20))

    # Displays changes to screen
    pygame.display.flip()

    clock.tick(60)

pygame.quit()
