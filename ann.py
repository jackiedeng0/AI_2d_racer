"""
    Neural Network Implementation from Scratch
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
            sum += self.biases[o]
            output.append(normalized_sigmoid(sum))
        return output

    # Output a random combination of weights from one equivalent FC_NNLayer
    # itself. Used for creating evolutionary children.
    @classmethod
    def mix_layers(cls, layer_1, layer_2, weighting_1):
        assert (
            layer_1.input_dim == layer_2.input_dim and
            layer_1.output_dim == layer_2.output_dim
        ), "Input and output dimensions of mixing partners must be the same"

        mixed_layer = cls(layer_1.input_dim, layer_1.output_dim)
        for o in range(layer_1.output_dim):
            for i in range(layer_1.input_dim):
                if (random.random() < weighting_1):
                    mixed_layer.weights[o][i] = layer_1.weights[o][i]
                else:
                    mixed_layer.weights[o][i] = layer_2.weights[o][i]
            if (random.random() < weighting_1):
                mixed_layer.biases[o] = layer_1.biases[o]
            else:
                mixed_layer.biases[o] = layer_2.biases[o]
        return mixed_layer

    # Mutates a random weight
    def mutate_layer(self, min, max):
        o = random.randint(0, self.output_dim - 1)
        i = random.randint(0, self.input_dim - 1)
        self.weights[o][i] += random.uniform(min, max)
