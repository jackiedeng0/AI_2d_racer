"""
    Neural Network Implementation from Scratch

    Inputs:
    - Car speed
    - Sensory Input

    Outputs:
    - Forward
    - Turn_left
"""

import random
import math

# Returns sigmoid normalized between -1 and 1


def normalized_sigmoid(x):
    return (2 / (1 + math.exp(-x))) - 1


class FC_NNLayer():

    # Fully connected Layer

    def __init__(self, input_dim, output_dim):

        self.input_dim = input_dim
        self.output_dim = output_dim

        self.weights = [[0] * input_dim] * output_dim
        self.biases = [0] * output_dim

    def randomize_weights_biases(self, min, max):
        for o in range(self.output_dim):
            for i in range(self.input_dim):
                self.weights[o][i] = random.uniform(min, max)
            self.biases[o] = random.uniform(min, max)

    def forward(self, input):
        output = []
        for o in range(self.output_dim):
            sum = 0
            for i in range(self.output_dim):
                sum += input[i] * self.weights[o][i]
            output.append(normalized_sigmoid(sum))
        return output
