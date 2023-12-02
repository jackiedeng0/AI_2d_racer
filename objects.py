"""
    Define game objects.
"""

import pygame
import math

CAR_IMAGE = pygame.image.load("assets/car.png")


class Car():

    # Car object which encapsulates the physics of driving

    def __init__(self, x, y, angle):
        self.image = CAR_IMAGE

        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 0
        # Per-frame physics attributes
        self.max_speed = 7
        self.rotation_coefficient = 2
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

        pygame.draw.line(screen, "#aaaaaa", self.corner_b_l,
                         self.corner_b_r, 2)
        pygame.draw.line(screen, "#aaaaaa", self.corner_b_r,
                         self.corner_f_r, 2)
        pygame.draw.line(screen, "#aaaaaa", self.corner_f_r,
                         self.corner_f_l, 2)
        pygame.draw.line(screen, "#aaaaaa", self.corner_f_l,
                         self.corner_b_l, 2)

    def turn(self, left=False):
        if left:
            self.angle += self.rotation_coefficient * \
                math.log(abs(self.speed) + 1) * math.copysign(1, self.speed)
        else:
            self.angle -= self.rotation_coefficient * \
                math.log(abs(self.speed) + 1) * math.copysign(1, self.speed)
        if (self.angle > 360):
            self.angle -= 360
        elif (self.angle < -360):
            self.angle += 360

    def forward(self):
        if self.speed < self.max_speed:
            self.speed += self.acceleration

    def reverse(self):
        if self.speed > (-1 * self.max_speed):
            self.speed -= self.acceleration

    # Apply generic command interface
    # forward
    #    0.5  to  1.0 for forward
    #   -0.5  to  0.5 for no acceleration
    #   -1.0  to -0.5 for reverse
    # turn_left
    #    0.5  to  1.0 for left
    #   -0.5  to  0.5 for no turn
    #   -1.0  to -0.5 for right
    def apply_command(self, forward, turn_left):
        if forward > 0.5:
            self.forward()
        elif forward < -0.5:
            self.reverse()

        if turn_left > 0.5:
            self.turn(left=True)
        elif turn_left < -0.5:
            self.turn(left=False)

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


class LiDAR_Car(Car):

    # Car Object Extension which has simple LiDAR with a limited number of
    # 'beams'. Each beam is used to detect if there are any objects colliding
    # at a fixed distance.

    def __init__(self, x, y, angle):
        super().__init__(x, y, angle)

        # Beam length should be relative to size of car
        self.beam_lengths = [2.8 * max(self.length, self.width),
                             1.4 * max(self.length, self.width),
                             0.7 * max(self.length, self.width),
                             3.5 * max(self.length, self.width),
                             1.7 * max(self.length, self.width),
                             0.8 * max(self.length, self.width),
                             2.8 * max(self.length, self.width),
                             1.4 * max(self.length, self.width),
                             0.7 * max(self.length, self.width)]
        # Beam angles relative to the direction car is facing
        self.beam_angles = [-60, -60, -60, 0, 0, 0, 60, 60, 60]
        # Beam endpoints (for collision) - Nonsense Initialization
        self.beam_endpoints = [(self.x, self.y)] * len(self.beam_angles)
        self.beam_collided = [False] * len(self.beam_angles)

    def draw_beams(self, screen):
        for i in range(len(self.beam_endpoints)):
            if (self.beam_collided[i]):
                pygame.draw.line(screen, "#ee9999",
                                 (self.x, self.y), self.beam_endpoints[i], 2)
            else:
                pygame.draw.line(screen, "#99ee99",
                                 (self.x, self.y), self.beam_endpoints[i], 2)

    def position_frame_update(self):
        super().position_frame_update()

        # Calculate Beam Endpoints
        radians = math.radians(self.angle)
        for i in range(len(self.beam_angles)):
            self.beam_endpoints[i] = (
                (self.x + (math.sin(radians + math.radians(self.beam_angles[i]))
                           * self.beam_lengths[i])),
                (self.y + (math.cos(radians + math.radians(self.beam_angles[i]))
                           * self.beam_lengths[i])))

        # Reset Beam Collided
        self.beam_collided = [False] * len(self.beam_angles)

    def force_position(self, x, y, angle, speed=0):
        super().force_position(x, y, angle, speed)

        # Re-initialize Beam Endpoints so draw() doesn't go crazy
        self.beam_endpoints = [(self.x, self.y)] * len(self.beam_angles)

    # Detects collision of beams
    def beam_collide_rect(self, rect):
        beam_collided = [False] * len(self.beam_angles)
        for i in range(len(self.beam_endpoints)):
            beam_collided[i] = rect.clipline(
                (self.x, self.y), self.beam_endpoints[i])
        return beam_collided

    # Detects collisions of beams and registers the fact internally to change draw()
    # It operates on an OR basis, therefore there is no mechanism to set False
    def beam_collide_rect_register(self, rect):
        beam_collided = self.beam_collide_rect(rect)
        for i in range(len(beam_collided)):
            if (beam_collided[i]):
                self.beam_collided[i] = True
