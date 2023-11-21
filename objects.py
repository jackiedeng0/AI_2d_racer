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
        # Get car dimensions
        still_rect = self.image.get_rect()
        self.length = still_rect.height
        self.width = still_rect.width
        # Corner positions (for collision) - Nonsense Initialization
        # b = back, f = front, l = left, r = right
        self.corner_b_l = (x, y)
        self.corner_b_r = (x, y)
        self.corner_f_r = (x, y)
        self.corner_f_l = (x, y)

    def draw(self, screen):
        rotated_image = pygame.transform.rotate(
            self.image, self.angle)
        new_rect = rotated_image.get_rect(center=(self.x, self.y))
        screen.blit(rotated_image, new_rect.topleft)

        pygame.draw.line(screen, "#ee0000", self.corner_b_l,
                         self.corner_b_r, 2)
        pygame.draw.line(screen, "#00ee00", self.corner_b_r,
                         self.corner_f_r, 2)
        pygame.draw.line(screen, "#0000ee", self.corner_f_r,
                         self.corner_f_l, 2)
        pygame.draw.line(screen, "#eeeeee", self.corner_f_l,
                         self.corner_b_l, 2)

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
        # Calculate new position
        radians = math.radians(self.angle)
        self.y += math.cos(radians) * self.speed
        self.x += math.sin(radians) * self.speed

        # Update Corners
        radians = math.radians(self.angle)
        half_width_sin_theta = (self.width / 2) * math.sin(radians)
        half_width_cos_theta = (self.width / 2) * math.cos(radians)
        half_length_sin_theta = (self.length / 2) * math.sin(radians)
        half_length_cos_theta = (self.length / 2) * math.cos(radians)
        self.corner_b_l = ((self.x - half_length_sin_theta + half_width_cos_theta),
                           (self.y - half_length_cos_theta - half_width_sin_theta))
        self.corner_b_r = ((self.x - half_length_sin_theta - half_width_cos_theta),
                           (self.y - half_length_cos_theta + half_width_sin_theta))
        self.corner_f_r = ((self.x + half_length_sin_theta - half_width_cos_theta),
                           (self.y + half_length_cos_theta + half_width_sin_theta))
        self.corner_f_l = ((self.x + half_length_sin_theta + half_width_cos_theta),
                           (self.y + half_length_cos_theta - half_width_sin_theta))

    def force_position(self, x, y, angle, speed=0):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed

    def collide_rect(self, rect):
        edge_b = self.corner_b_l, self.corner_b_r
        edge_f = self.corner_f_l, self.corner_f_r
        edge_l = self.corner_b_l, self.corner_f_l
        edge_r = self.corner_b_r, self.corner_f_r
        return (rect.clipline(edge_b) or rect.clipline(edge_f)
                or rect.clipline(edge_l) or rect.clipline(edge_r))

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
