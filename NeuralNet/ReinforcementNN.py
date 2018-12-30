import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import gym
import numpy as np
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

    def forward(self, x):
        x = self.affine1(self.HardTanh(x))
        x = self.affine2(self.HardTanh(x))
        # x = self.HardTanh(x)
        x = self.sig(x)
        return x


policy = Policy()
optimizer = optim.Adam(policy.parameters(), lr=0.01)
eps = np.finfo(np.float32).eps.item()
