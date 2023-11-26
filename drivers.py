"""
    Define drivers, including a player driver.
"""

import pygame
import random
from abc import ABC, abstractmethod
from objects import Car, LiDAR_Car
from ann import FC_NNLayer


class Driver(ABC):
    def __init__(self, car):
        self.car = car
        self.win = 0

    @abstractmethod
    def drive_command(self):
        pass


class Player_Driver(Driver):
    def __init__(self, car):
        super().__init__(car)

    def drive_command(self):
        keys = pygame.key.get_pressed()
        forward = 0
        turn_left = 0
        if keys[pygame.K_w]:
            forward += 1
        if keys[pygame.K_s]:
            forward -= 1
        if keys[pygame.K_a]:
            turn_left += 1
        if keys[pygame.K_d]:
            turn_left -= 1

        return forward, turn_left


class Random_Driver(Driver):
    def __init__(self, car):
        super().__init__(car)

    def drive_command(self):
        forward = random.uniform(-1, 1)
        turn_left = random.uniform(-1, 1)
        return (forward, turn_left)


class Momentum_Driver(Driver):
    def __init__(self, car):
        super().__init__(car)
        self.forward_momentum = 0
        self.left_momentum = 0

        self.forward_momentum_coefficient = 0.2
        self.left_momentum_coefficient = 0.1

    # Agent leans towards last action and biases forward
    def drive_command(self):
        forward = max(min(random.uniform(-0.2, 1) +
                      self.forward_momentum, 1), -1)
        turn_left = max(min(random.uniform(-1, 1) + self.left_momentum, 1), -1)
        self.forward_momentum = max(
            min(self.forward_momentum + forward * self.forward_momentum_coefficient, 1), -1)
        self.left_momentum = max(
            min(self.left_momentum + turn_left * self.left_momentum_coefficient, 0.2), -0.2)
        return (forward, turn_left)


class No_Hidden_NN_Driver(Driver):
    def __init__(self, car):
        super().__init__(car)

        # Input to output layer
        #   In: 3 LiDAR beams + Car speed
        #   Out: Forward, Turn Left
        self.io_layer = FC_NNLayer(4, 2)
        self.io_layer.randomize_weights_biases(-2, 2)

    def drive_command(self):
        if type(self.car) is LiDAR_Car:
            input = []
            for bc in self.car.beam_collided:
                if bc == True:
                    input.append(1)
                else:
                    input.append(0)
            input.append(self.car.speed)
            output = self.io_layer.forward(input)
            return output[0], output[1]
        else:
            return 0, 0


class One_Hidden_NN_Driver(Driver):
    def __init__(self, car):
        super().__init__(car)

        # Input to hidden layer
        #   In: 3 LiDAR beams + Car speed
        #   Out: 3 Hidden
        self.ih_layer = FC_NNLayer(4, 3)
        self.ih_layer.randomize_weights_biases(-4, 4)

        # Hidden to output layer
        #   In: 3 Hidden
        #   Out: Forward, Turn Left
        self.ho_layer = FC_NNLayer(3, 2)
        self.ho_layer.randomize_weights_biases(-4, 4)

    def drive_command(self):
        if type(self.car) is LiDAR_Car:
            input = []
            for bc in self.car.beam_collided:
                if bc == True:
                    input.append(1)
                else:
                    input.append(0)
            input.append(self.car.speed)
            hidden = self.ih_layer.forward(input)
            output = self.ho_layer.forward(hidden)
            return output[0], output[1]
        else:
            return 0, 0
