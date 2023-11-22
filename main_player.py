"""
    Playable Version
"""

import pygame
import math
import json
from objects import Car, Obstacle, Goal, LiDARCar

pygame.init()
screen = pygame.display.set_mode((1400, 800))
clock = pygame.time.Clock()
running = True

border_width = 50
border_rect = pygame.Rect(border_width, border_width, screen.get_width() -
                          (border_width * 2), screen.get_height() - (border_width * 2))

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
            goals.append(Goal(pygame.Rect(
                level_goal["left"], level_goal["top"], level_goal["width"], level_goal["height"])))
    if "obstacles" in level.keys():
        for level_obst in level["obstacles"]:
            obstacles.append(Obstacle(pygame.Rect(
                level_obst["left"], level_obst["top"], level_obst["width"], level_obst["height"])))

player_car = LiDARCar(start_x, start_y, start_angle)

while running:

    # Event polling - Currently used for quitting
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clears screen of last frame
    screen.fill("#eeeeee")

    # Controls
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player_car.forward()
    if keys[pygame.K_s]:
        player_car.reverse()
    if keys[pygame.K_a]:
        player_car.turn(left=True)
    if keys[pygame.K_d]:
        player_car.turn(left=False)

    # Update Car Position
    player_car.simulate_friction()
    player_car.position_frame_update()

    # Collisions
    for goal in goals:
        if (player_car.collide_rect(goal.rect)):
            pygame.draw.rect(screen, "#6EB141", goal.rect)
        else:
            pygame.draw.rect(screen, "#93F651", goal.rect)
        if type(player_car) is LiDARCar:
            player_car.beam_collide_rect_register(goal.rect)
    for obst in obstacles:
        if (player_car.collide_rect(obst.rect)):
            pygame.draw.rect(screen, "#B05637", obst.rect)
            player_car.force_position(start_x, start_y, start_angle)
        else:
            pygame.draw.rect(screen, "#F27549", obst.rect)
        if type(player_car) is LiDARCar:
            player_car.beam_collide_rect_register(obst.rect)

    # Going Off Screen
    if (player_car.out_of_rect(border_rect)):
        player_car.force_position(start_x, start_y, start_angle)
    pygame.draw.rect(screen, "#444444", border_rect, 4)

    # Draw car on top
    player_car.draw(screen)

    # Draw LiDAR Beams
    if type(player_car) is LiDARCar:
        player_car.draw_beams(screen)

    # Displays changes to screen
    pygame.display.flip()

    clock.tick(60)

pygame.quit()
