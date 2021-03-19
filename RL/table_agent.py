from collections import defaultdict
import numpy as np
import random
import pickle

POSITIVE = 1
NEGATIVE = -1

class TabulatedIotAgent:
    def __init__(self, n_state, a_state, name):
        self.n_state = n_state
        self.a_state = a_state
        self.name = name
        self.actions = list(range(a_state))
        self.init_lr = 0.75
        self.time_step = 0
        self.discount_factor = 0.25
        self.rewardQueue = [0.0, 0.0, 0.0, 0.0, 0.0]
        self.T_reset = 3
        self.epsilon = 0.3
        self.q_table = defaultdict(lambda: [1.0]+[0.0]*(a_state-1)) # Initial Policy - only Still
        self.memory = []

    def save_model(self, dir_path):
        with open(dir_path+self.name+'.qt', 'wb') as f:
            pickle.dump(self.q_table, f)
    
    def load_model(self, dir_path):
        with open(dir_path+self.name+'.qt', 'rb') as f:
            self.q_table = pickle.load(f)

    def train_model(self, state, action, reward, next_state):
        self.time_step = max(self.time_step, 1)
        ''' Update the Q Function '''
        curr_state, next_state = str(state), str(next_state)
        q_1 = self.q_table[curr_state][action]
        q_2 = reward + self.discount_factor * max(self.q_table[next_state])
        self.q_table[curr_state][action] += (self.init_lr/self.time_step) * (q_2 - q_1)

        ''' Update the reward queue '''
        self.rewardQueue.pop(0)
        self.rewardQueue.append(reward)

        ''' If Number of positive reward is less than T_reset, reset the time step '''
        if len(list(filter(lambda x: x >= 0, self.rewardQueue))) < self.T_reset:
            self.time_step = 0

        return

    def train_model_from_memory(self, memory, final_state, user_cnt):
        states = list(map(lambda x: x[0], memory))
        actions = list(map(lambda x: x[1], memory))
        next_states = list(map(lambda x: x[2], memory))
        rewards = []

        for i in range(len(memory)):
            ''' Test - Reward calculation without outside state '''
            state_distance = sum(list(map(lambda x, y: (x-y)**2, states[i][:-1], final_state[:-1])))
            next_state_distance = sum(list(map(lambda x, y: (x-y)**2, next_states[i][:-1], final_state[:-1])))
            curr_next_distance = sum(list(map(lambda x, y: (x-y)**2, next_states[i][:-1], states[i][:-1])))
            reward = POSITIVE if ((state_distance > next_state_distance and curr_next_distance > 0.001) or next_state_distance <= 0.0001) else NEGATIVE
            if i == len(memory)-1:
                reward -= user_cnt
            rewards.append(reward)

        print(f'avg reward = {sum(rewards)/len(rewards)}')
        
        for i in range(len(memory)):
            self.train_model(states[i], actions[i], rewards[i], next_states[i])
        self.epsilon = max(0.001, self.epsilon*0.95)

        return


    def get_action(self, state):
        curr_state = str(state)
        q_list = self.q_table[curr_state]
        actions = self.actions[:]
        action = arg_max(q_list)
        if random.uniform(0, 1) < self.epsilon:
            actions.pop(action)
            action = random.choice(actions)
        self.time_step += 1
        
        return action

def arg_max(q_list):
    max_idx_list = np.argwhere(q_list == np.amax(q_list))
    max_idx_list = max_idx_list.flatten().tolist()
    return random.choice(max_idx_list)