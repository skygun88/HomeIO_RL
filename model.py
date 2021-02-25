import torch
import torch.nn as nn
import torch.nn.functional as F

'''
class Actor:
    Actor Module - Neural Network for approximating the policy
'''
class Actor(nn.Module):
    def __init__(self, n_state, n_action):
        super(Actor, self).__init__()
        self.hidden1 = nn.Linear(n_state, 24)
        self.out = nn.Linear(24, n_action)

    def forward(self, x):
        x = torch.Tensor(x)
        x = self.hidden1(x)
        x = torch.tanh(x)
        x = self.out(x)
        out = F.softmax(x, dim=-1)
        return out 

'''
class Critic:
    Critic Module - Neural Network for approximating the value
'''
class Critic(nn.Module):
    def __init__(self, n_state):
        super(Critic, self).__init__()
        self.hidden1 = nn.Linear(n_state, 24)
        self.hidden2 = nn.Linear(24, 24)
        self.out = nn.Linear(24, 1)

    def forward(self, x):
        x = torch.Tensor(x)
        x = self.hidden1(x)
        x = torch.tanh(x)
        x = self.hidden2(x)
        x = torch.tanh(x)
        out = self.out(x)
        return out