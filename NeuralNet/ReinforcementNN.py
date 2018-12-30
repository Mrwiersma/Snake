import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import gym
import numpy as np
import os
from torch.distributions import Categorical


class Policy(nn.Module):
    def __init__(self):
        super(Policy, self).__init__()
        self.affine1 = nn.Linear(11, 16)
        self.sigmoid1 = nn.Sigmoid()
        self.affine2 = nn.Linear(16, 2)
        self.sigmoid2 = nn.Sigmoid()
        self.HardTanh = nn.Hardtanh(0, 1)
        self.sig = nn.Sigmoid()

        self.saved_log_probs = []
        self.rewards = []
        self.weights = self.state_dict()

    def forward(self, x):
        x = self.affine1(self.HardTanh(x))
        x = self.affine2(self.HardTanh(x))
        # x = self.HardTanh(x)
        x = self.sig(x)
        #print("x", x)
        return x

    def set_weights(self, data):
        self.load_state_dict(data)
        self.weights = self.state_dict()

    def save_model(self, gen, _id):  # slaat de gewichten op met juiste naam en map
        if not os.path.isdir('NeuralNet/Models/Gen_{}'.format(gen)):
            os.makedirs('NeuralNet/Models/Gen_{}'.format(gen))
        torch.save(self.weights, 'NeuralNet/Models/Gen_{}/Snake_{}.pt'.format(gen, _id))
        print("check",gen,_id)

policy = Policy()
optimizer = optim.Adam(policy.parameters(), lr=0.01)
eps = np.finfo(np.float32).eps.item()
