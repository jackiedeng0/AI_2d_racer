"""
    AI Agent Driver Version
"""

import pygame
import math
import json
import random
from objects import Car, Obstacle, Goal

class Random_Driver():
    def __init__(self, car):
        self.car = car
        self.win = 0

    # Agent determines how to drive - would normally be a function
    # of perceptive input and car state
    #
    # forward
    #    0.5  to  1.0 for forward
    #   -0.5  to  0.5 for no acceleration
    #   -1.0  to -0.5 for reverse
    # turn_left
    #    0.5  to  1.0 for left
    #   -0.5  to  0.5 for no turn
    #   -1.0  to -0.5 for right
    def drive(self):
        forward = random.uniform(-1, 1)
        turn_left = random.uniform(-1, 1)
        return (forward, turn_left)


class Momentum_Driver():
    def __init__(self, car):
        self.car = car
        self.win = 0
        self.forward_momentum = 0
        self.left_momentum = 0

        self.forward_momentum_coefficient = 0.2
        self.left_momentum_coefficient = 0.2

    # Agent leans towards last action and biases forward
    def drive(self):
        forward = max(min(random.uniform(-0.2, 1) +
                      self.forward_momentum, 1), -1)
        turn_left = max(min(random.uniform(-1, 1) + self.left_momentum, 1), -1)
        self.forward_momentum = max(
            min(self.forward_momentum + forward * self.forward_momentum_coefficient, 1), -1)
        left_momentum = max(
            min(self.left_momentum + turn_left * self.left_momentum_coefficient, 1), -1)
        return (forward, turn_left)


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

ai_car = Car(start_x, start_y, start_angle)
ai_driver = Momentum_Driver(ai_car)

while running:

    # Event polling - Currently used for quitting
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clears screen of last frame
    screen.fill("#eeeeee")

    # Controls
    forward, turn_left = ai_driver.drive()

    if forward > 0.5:
        ai_car.forward()
    elif forward < -0.5:
        ai_car.reverse()

    if turn_left > 0.5:
        ai_car.turn(left=True)
    elif turn_left < -0.5:
        ai_car.turn(left=False)

    # Update Car Position
    ai_car.simulate_friction()
    random_driver = Random_Driver(ai_car)
    ai_car.position_frame_update()
    random_driver = Random_Driver(ai_car)

    # Collisions
    for goal in goals:
        if (ai_car.collide_rect(goal)):
            random_driver = Random_Driver(ai_car)
            pygame.draw.rect(screen, "#6EB141", goal)
        else:
            pygame.draw.rect(screen, "#93F651", goal)
    for obst in obstacles:
        if (ai_car.collide_rect(obst)):
            random_driver = Random_Driver(ai_car)
            pygame.draw.rect(screen, "#B05637", obst)
            ai_car.force_position(start_x, start_y, start_angle)
            random_driver = Random_Driver(ai_car)
        else:
            pygame.draw.rect(screen, "#F27549", obst)

    # Going Off Screen
    if (ai_car.out_of_rect(border_rect)):
        random_driver = Random_Driver(ai_car)
        ai_car.force_position(start_x, start_y, start_angle)
        random_driver = Random_Driver(ai_car)
    pygame.draw.rect(screen, "#444444", border_rect, 4)

    # Draw car on top
    ai_car.draw(screen)
    random_driver = Random_Driver(ai_car)

    # Dsiplays changes to screen
    pygame.display.flip()

    clock.tick(60)

pygame.quit()
