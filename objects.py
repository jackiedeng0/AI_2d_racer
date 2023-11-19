"""
    Define game objects.
    Goals and Obstacles are currently Pygame.Rect's
"""

import pygame
import math

CAR_IMAGE = pygame.image.load("assets/car.png")


class Car():
    def __init__(self, x, y, angle):
        self.image = CAR_IMAGE

        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 0
        # Per-frame physics attributes
        self.rotation_coefficient = 1
        self.acceleration = 0.05
        self.friction_deceleration = 0.02

    def draw(self, screen):
        rotated_image = pygame.transform.rotate(
            self.image, self.angle)
        new_rect = rotated_image.get_rect(center=(self.x, self.y))
        screen.blit(rotated_image, new_rect.topleft)

    def turn(self, left=False):
        if left:
            self.angle += self.rotation_coefficient * self.speed
        else:
            self.angle -= self.rotation_coefficient * self.speed
        if (self.angle > 360):
            self.angle -= 360
        elif (self.angle < -360):
            self.angle += 360

    def forward(self):
        self.speed += self.acceleration

    def reverse(self):
        self.speed -= self.acceleration

    def simulate_friction(self):
        if math.fabs(self.speed) < self.friction_deceleration:
            self.speed = 0
        elif self.speed > 0:
            self.speed -= self.friction_deceleration
        elif self.speed < 0:
            self.speed += self.friction_deceleration

    def position_frame_update(self):
        radians = math.radians(self.angle)
        self.y += math.cos(radians) * self.speed
        self.x += math.sin(radians) * self.speed

    def force_position(self, x, y, angle, speed=0):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed

    def collide_rect(self, rect):
        rotated_image = pygame.transform.rotate(
            self.image, self.angle)
        new_rect = rotated_image.get_rect(center=(self.x, self.y))
        return new_rect.colliderect(rect)

    def out_of_rect(self, rect):
        return not self.collide_rect(rect)


class Obstacle():
    collided = False

    def __init__(self, rect):
        self.rect = rect


class Goal():
    reached = False

    def __init__(self, rect):
        self.rect = rect
