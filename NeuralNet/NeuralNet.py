import torch
import torch.nn as nn
import numpy as np
import csv
import os

network_dict = {0: {'mode': "Linear", "input": 11, "output": 12, "bias": True, "activation": "ReLU"},
                1: {'mode': "Linear", "input": -1, "output": 6, "bias": True, "activation": "Sigmoid"},
                2: {'mode': "Linear", "input": -1, "output": 4, "bias": True, "activation": "Sigmoid"},
                3: {'mode': "Linear", "input": -1, "output": 2, "bias": True, "activation": "ReLU6"}}

# ______HyperParameters________
LEARNING_RATE = 0.1


class Net(nn.Sequential):
    def __init__(self, x=network_dict):
        super(Net, self).__init__()
        self.setup_layers(x)

        self.Target = None
        self.Training_input = None
        self.Optimizer = None
        self.Criteria = None
        self.minimum_steps = None
        self.sample_size = None
        self.sample_freq = None
        self.stop_threshold = None
        self.stop_delay = None
        self.stop_training = None
        self.stop_counter = None

        self.weights = self.state_dict()

    def setup_layers(self, net_dict):
        for count in range(0, len(net_dict)):
            name, in_feat, out_feat, bias = self.get_params(net_dict, count)
            act_name, activation = self.get_activation_method(net_dict, count)
            if name == "Linear" + str(count):
                self.add_module(name, nn.Linear(in_feat, out_feat, bias))
                self.add_module(act_name, activation)

    @staticmethod
    def get_params(_dict, c):
        _name = _dict[c]["mode"] + str(c)
        _input = _dict[c]["input"]
        _output = _dict[c]["output"]
        _bias = _dict[c]["bias"]
        if _input == -1:
            _input = _dict[c - 1]["output"]
        return _name, _input, _output, _bias

    @staticmethod
    def get_activation_method(_dict, i):
        x = _dict[i]['activation']
        if x == "ReLU":
            return "ReLU" + str(i), nn.ReLU()
        if x == "Sigmoid":
            return "Sigmoid" + str(i), nn.Sigmoid()
        if x == "ReLU6":
            return "ReLU6" + str(i), nn.ReLU6()

    def forward(self, x):
        return super().forward(x)

    def set_target(self, x):
        self.Target = torch.Tensor(x)

    def set_training_input(self, x):
        self.Training_input = torch.Tensor(x)

    def set_optimizer(self, x):
        self.Optimizer = x

    def set_criteria(self, x):
        self.Criteria = x

    def set_stop_criteria(self, min_steps, samp_size, samp_freq, stop_thresh, stop_delay):
        self.minimum_steps = min_steps
        self.sample_size = samp_size
        self.sample_freq = samp_freq
        self.stop_threshold = stop_thresh
        self.stop_delay = stop_delay

    def get_weights(self):
        return self.state_dict()

    def set_weights(self, data):
        self.load_state_dict(data)

    def save_model(self, gen, _id):
        if not os.path.isdir('NeuralNet/Models/Gen_{}'.format(gen)):
            os.makedirs('NeuralNet/Models/Gen_{}'.format(gen))
        torch.save(self.weights, 'NeuralNet/Models/Gen_{}/Snake_{}.pt'.format(gen, _id))

    def load_model(self, gen, _id, weights):
        test = torch.load('NeuralNet/Models/Gen_{}/Snake_{}.pt'.format(gen, _id))
        print('test', test['Linear0.weight'][0][0])
        test['Linear0.weight'][0][0] = test['Linear0.weight'][0][0] * -1
        print('test2', test['Linear0.weight'][0][0])
