import sys
import os 
import numpy as np
import math
import torch
import torch.optim as optim
import torch.nn.utils as torch_utils

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(os.path.dirname(__file__))
from model import * 

POSITIVE = 1
NEGATIVE = -1

'''
class LightAgent:
    RL agent for learning Smart-home brightness adpatation
    This agent learn athe task based on Actor-critic
'''
class IoTAgent:
    def __init__(self, n_state, n_action, name):
        self.actor: Actor = Actor(n_state=n_state, n_action=n_action)
        self.critic: Critic = Critic(n_state=n_state)

        self.name = name
        self.n_action = n_action
        self.discount_factor = 0.25
        self.learning_rate = 0.01

        self.actor_optimizer = optim.Adam(self.actor.parameters(), lr=self.learning_rate)
        torch_utils.clip_grad_norm_(self.actor.parameters(), 5.0)
        self.critic_optimizer = optim.Adam(self.critic.parameters(), lr=self.learning_rate)
        torch_utils.clip_grad_norm_(self.critic.parameters(), 5.0)

    def get_action(self, state):
        np_state = np.array(state).reshape(1, -1)
        policy = self.actor(np_state)
        policy = policy.detach().numpy().squeeze(0)
        action = np.random.choice(self.n_action, 1, p=policy)[0]
        return action

    def save_model(self, dir_path):
        torch.save(self.actor.state_dict(), dir_path+self.name+'_actor.pt')
        torch.save(self.critic.state_dict(), dir_path+self.name+'_critic.pt')

    def load_model(self, dir_path):
        self.actor.load_state_dict(torch.load(dir_path+self.name+'_actor.pt'))
        self.critic.load_state_dict(torch.load(dir_path+self.name+'_critic.pt'))

    def set_eval(self):
        self.actor.eval()
        self.critic.eval()

    def train_model(self, state, action, reward, next_state, done):
        self.actor_optimizer.zero_grad(), self.critic_optimizer.zero_grad()
        self.actor.train(), self.critic.train()
        policy, value, next_value = self.actor(state), self.critic(state), self.critic(next_state)

        target = reward + (1 - done) * self.discount_factor * next_value
        
        one_hot_action = torch.zeros(self.n_action)
        one_hot_action[action] = policy[action]
        action_prob = one_hot_action.reshape(self.n_action)
        action_prob = torch.sum(action_prob)
        advantage = (target - value.item()).detach().reshape(1)
        # print(f'advantage: {advantage}, {advantage.shape}, {advantage.dtype}')

        actor_loss = -(torch.log(action_prob + 1e-5)*advantage)
        critic_loss = 0.5 * torch.square(target.detach() - value[0])
        loss = 0.3 * actor_loss + critic_loss
        loss.backward()
        #print(f'loss: {loss.item()}')

        self.actor_optimizer.step()
        self.critic_optimizer.step()
        return loss.item()

    def train_model_from_memory(self, memory, final_state):
        self.actor.train(), self.critic.train()
        self.actor_optimizer.zero_grad(), self.critic_optimizer.zero_grad()

        ''' memory[n, 5] = [states, actions, rewards, next_states, masks]'''
        states = np.array(tuple(map(lambda x: x[0], memory)))
        actions = np.array(tuple(map(lambda x: x[1], memory)))
        next_states = np.array(tuple(map(lambda x: x[2], memory)))
        rewards = []

        # print(f'memory with final ---------------------')
        for i in range(len(memory)):
            #state_distance = sum(list(map(lambda x, y: (x-y)**2, states[i], final_state)))
            #next_state_distance = sum(list(map(lambda x, y: (x-y)**2, next_states[i], final_state)))
            ''' Test - Reward calculation without outside state '''
            state_distance = sum(list(map(lambda x, y: (x-y)**2, states[i][:-1], final_state[:-1])))
            next_state_distance = sum(list(map(lambda x, y: (x-y)**2, next_states[i][:-1], final_state[:-1])))
            reward = POSITIVE if (state_distance > next_state_distance or next_state_distance <= 0.0001) else NEGATIVE
            rewards.append(reward)
            if len(final_state) == 3:
                print(f'States: {states[i]}, distance: {state_distance}')
                print(f'Actions: {actions[i]}')
                print(f'Next_states: {next_states[i]}, distance: {next_state_distance}')
                print(f'final_state: {final_state}')
                print(f'reward: {reward}')
                print(f'---------------------------------------')

        print(f'avg reward = {sum(rewards)/len(rewards)}')
        rewards = np.array(rewards)
        masks = [1]*len(memory)
        #masks[-1] = 0
        masks = np.array(masks)

        torch_masks = torch.from_numpy(masks)
        torch_rewards = torch.from_numpy(rewards)

        for i in range(10):
            policies = self.actor(states)
            values = self.critic(states)
            next_values = self.critic(next_states)
            values = values.squeeze()
            next_values = next_values.squeeze()

            one_hot_actions = torch.zeros(len(actions), self.n_action)

            for i in range(len(actions)):
                one_hot_actions[i][actions[i]] = 1
            #print(one_hot_actions)
            one_hot_actions = policies * one_hot_actions 
            #print(one_hot_actions)
            action_prob = torch.sum(one_hot_actions, dim=1)
            log_prob = torch.log(action_prob+1e-5)
            target = torch_rewards +  torch_masks * self.discount_factor * next_values
            advantage = (target - values).detach()
            actor_loss = torch.sum(-log_prob*advantage)
            critic_loss = torch.sum(0.5 * torch.square(target.detach() - values))
            loss = 0.3 * actor_loss + critic_loss
            loss.backward()

            self.actor_optimizer.step()
            self.critic_optimizer.step()
        self.actor.eval(), self.critic.eval()
        # print(loss)
        return